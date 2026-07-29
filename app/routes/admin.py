from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.mission import Mission, MissionCompletion
from app.models.redeem import RedeemRequest
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@bp.route('/')
@login_required
def admin_panel():
    if not current_user.is_admin:
        abort(403)
    users_count = User.query.count()
    missions_count = Mission.query.count()
    pending_completions = MissionCompletion.query.filter_by(status='pending').count()
    pending_redeems = RedeemRequest.query.filter_by(status='pending').count()
    return render_template('admin_dashboard.html',
                         users_count=users_count,
                         missions_count=missions_count,
                         pending_completions=pending_completions,
                         pending_redeems=pending_redeems)


@bp.route('/missions', methods=['GET', 'POST'])
@login_required
def manage_missions():
    if not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        reward_points = int(request.form.get('reward_points'))
        link = request.form.get('link')
        image_url = request.form.get('image_url')
        category = request.form.get('category', 'general')

        mission = Mission(
            title=title,
            description=description,
            reward_points=reward_points,
            link=link,
            image_url=image_url,
            category=category
        )
        db.session.add(mission)
        db.session.commit()
        flash('Misión creada!', 'success')
        return redirect(url_for('admin.manage_missions'))

    missions = Mission.query.all()
    return render_template('admin_missions.html', missions=missions)


@bp.route('/missions/delete/<int:mission_id>')
@login_required
def delete_mission(mission_id):
    if not current_user.is_admin:
        abort(403)
    mission = Mission.query.get_or_404(mission_id)
    MissionCompletion.query.filter_by(mission_id=mission_id).delete()
    db.session.delete(mission)
    db.session.commit()
    flash('Misión eliminada.', 'success')
    return redirect(url_for('admin.manage_missions'))


@bp.route('/completions')
@login_required
def manage_completions():
    if not current_user.is_admin:
        abort(403)
    completions = MissionCompletion.query.order_by(MissionCompletion.completed_at.desc()).all()
    return render_template('admin_completions.html', completions=completions)


@bp.route('/completions/approve/<int:completion_id>')
@login_required
def approve_completion(completion_id):
    if not current_user.is_admin:
        abort(403)
    completion = MissionCompletion.query.get_or_404(completion_id)
    completion.status = 'approved'
    user = User.query.get(completion.user_id)
    mission = Mission.query.get(completion.mission_id)
    user.points += mission.reward_points
    user.total_earned += mission.reward_points
    user.missions_completed += 1
    db.session.commit()
    flash('Misión aprobada y puntos otorgados!', 'success')
    return redirect(url_for('admin.manage_completions'))


@bp.route('/completions/reject/<int:completion_id>')
@login_required
def reject_completion(completion_id):
    if not current_user.is_admin:
        abort(403)
    completion = MissionCompletion.query.get_or_404(completion_id)
    completion.status = 'rejected'
    db.session.commit()
    flash('Misión rechazada.', 'warning')
    return redirect(url_for('admin.manage_completions'))


@bp.route('/redeems')
@login_required
def manage_redeems():
    if not current_user.is_admin:
        abort(403)
    redeems = RedeemRequest.query.order_by(RedeemRequest.created_at.desc()).all()
    return render_template('admin_redeems.html', redeems=redeems)


@bp.route('/redeems/complete/<int:redeem_id>')
@login_required
def complete_redeem(redeem_id):
    if not current_user.is_admin:
        abort(403)
    redeem = RedeemRequest.query.get_or_404(redeem_id)
    redeem.status = 'completed'
    db.session.commit()
    flash('Canje completado!', 'success')
    return redirect(url_for('admin.manage_redeems'))


@bp.route('/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@bp.route('/users/make-admin/<int:user_id>')
@login_required
def make_admin(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'{user.username} ahora es admin.', 'success')
    return redirect(url_for('admin.manage_users'))
