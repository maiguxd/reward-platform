from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.mission import Mission, MissionCompletion
from app.models.redeem import RedeemRequest
import logging
import os

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/terms')
def terms():
    return render_template('terms.html')


@bp.route('/privacy')
def privacy():
    return render_template('privacy.html')


@bp.route('/callback/cpx', methods=['GET', 'POST'])
def cpx_callback():
    data = request.args if request.method == 'GET' else request.form

    status = data.get('status', '0')
    trans_id = data.get('trans_id', '')
    sub_id = data.get('user_id') or data.get('ext_user_id') or data.get('sub_id') or data.get('subid_1') or data.get('subid')
    amount_usd = data.get('amount_usd') or data.get('amount') or data.get('payout') or '0'
    offer_id = data.get('offer_id', '')

    logger.info(f'CPX callback received: status={status} trans_id={trans_id} sub_id={sub_id} amount={amount_usd} full={dict(data)}')

    try:
        with open(os.path.join(os.path.dirname(__file__), '../../cpx_debug.log'), 'a') as f:
            f.write(f'{dict(data)}\n')
    except Exception:
        pass

    if not sub_id:
        return 'OK'

    try:
        sub_id = int(sub_id)
    except (TypeError, ValueError):
        logger.warning(f'CPX callback: invalid sub_id {sub_id}')
        return 'OK'

    user = User.query.filter_by(id=sub_id).first()
    if not user:
        logger.warning(f'CPX callback: user {sub_id} not found')
        return 'OK'

    if status in ('1', 'success', 'approved', 'complete', 'completed'):
        try:
            points = int(float(amount_usd) * 100)
        except (TypeError, ValueError):
            points = 0
        if points <= 0:
            points = 50
        user.points += points
        user.total_earned += points
        db.session.commit()
        logger.info(f'Credited {points} points to user {user.username} from CPX')
    elif status == '2':
        try:
            points = int(float(amount_usd) * 100)
        except (TypeError, ValueError):
            points = 0
        if points > 0:
            user.points = max(0, user.points - points)
            user.total_earned = max(0, user.total_earned - points)
            db.session.commit()
            logger.info(f'Reversed {points} points from user {user.username} (fraud reversal)')
    return 'OK'


@bp.route('/dashboard')
@login_required
def dashboard():
    missions = Mission.query.filter_by(is_active=True).all()
    completions = MissionCompletion.query.filter_by(user_id=current_user.id).all()
    completed_ids = [c.mission_id for c in completions if c.status == 'approved']
    pending_ids = [c.mission_id for c in completions if c.status == 'pending']
    return render_template('dashboard.html',
                         missions=missions,
                         completed_ids=completed_ids,
                         pending_ids=pending_ids,
                         completions=completions)


@bp.route('/mission/complete/<int:mission_id>', methods=['POST'])
@login_required
def complete_mission(mission_id):
    mission = Mission.query.get_or_404(mission_id)
    existing = MissionCompletion.query.filter_by(
        user_id=current_user.id,
        mission_id=mission_id
    ).first()

    if existing:
        flash('Ya has completado o solicitado esta misión.', 'warning')
        return redirect(url_for('main.dashboard'))

    proof = request.form.get('proof', '')
    completion = MissionCompletion(
        user_id=current_user.id,
        mission_id=mission_id,
        proof_text=proof
    )
    db.session.add(completion)
    db.session.commit()

    flash('Misión completada! Espera la verificación.', 'success')
    return redirect(url_for('main.dashboard'))


@bp.route('/redeem', methods=['GET', 'POST'])
@login_required
def redeem():
    if request.method == 'POST':
        reward_type = request.form.get('reward_type')
        amount = int(request.form.get('amount', 0))
        discord_contact = request.form.get('discord_contact')

        if reward_type == 'robux':
            points_cost = amount * 10
        elif reward_type == 'giftcard':
            points_cost = amount * 100
        else:
            flash('Tipo de recompensa inválido.', 'danger')
            return redirect(url_for('main.redeem'))

        if current_user.points < points_cost:
            flash('No tienes suficientes puntos.', 'danger')
            return redirect(url_for('main.redeem'))

        redeem_req = RedeemRequest(
            user_id=current_user.id,
            reward_type=reward_type,
            amount=amount,
            points_cost=points_cost,
            discord_contact=discord_contact
        )
        current_user.points -= points_cost
        db.session.add(redeem_req)
        db.session.commit()

        flash(f'Solicitud enviada! Contacta a soporte por Discord para recibir tu recompensa.', 'success')
        return redirect(url_for('main.redeem'))

    return render_template('redeem.html')


@bp.route('/convert-points', methods=['POST'])
@login_required
def convert_points():
    points = int(request.form.get('points', 0))
    if points < 100:
        flash('Mínimo 100 puntos para convertir.', 'warning')
        return redirect(url_for('main.dashboard'))
    if points > current_user.points:
        flash('No tienes suficientes puntos.', 'danger')
        return redirect(url_for('main.dashboard'))

    current_user.points -= points
    current_user.missions_completed += 1
    db.session.commit()
    flash(f'{points} puntos convertidos exitosamente!', 'success')
    return redirect(url_for('main.dashboard'))
