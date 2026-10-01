from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.models import db, User
from app.utils.audit import log_audit

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.active:
                flash('Esta cuenta está desactivada. Consulte al administrador.', 'danger')
                return render_template('auth/login.html')
            
            login_user(user, remember=remember)
            log_audit('LOGIN', 'Autenticación', f'Usuario {user.username} inició sesión')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    log_audit('LOGOUT', 'Autenticación', f'Usuario {current_user.username} cerró sesión')
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        new_password = request.form.get('new_password')

        current_user.full_name = full_name
        current_user.email = email
        if new_password and len(new_password) >= 6:
            current_user.set_password(new_password)
            flash('Contraseña actualizada con éxito.', 'success')

        db.session.commit()
        log_audit('ACTUALIZAR', 'Perfil', f'Usuario {current_user.username} actualizó su perfil')
        flash('Perfil actualizado con éxito.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
