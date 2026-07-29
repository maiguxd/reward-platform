from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'danger')
            return render_template('register.html')

        hashed = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()

        flash('Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('main.index'))
