import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required, current_user
from app.models.models import db, User, CompanySetting, AuditLog
from app.utils.decorators import admin_required
from app.utils.audit import log_audit
from datetime import datetime

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    company = CompanySetting.query.first()
    if not company:
        company = CompanySetting()
        db.session.add(company)
        db.session.commit()

    if request.method == 'POST':
        company.company_name = request.form.get('company_name', '').strip()
        company.nit = request.form.get('nit', '').strip()
        company.phone = request.form.get('phone', '').strip()
        company.email = request.form.get('email', '').strip()
        company.address = request.form.get('address', '').strip()
        company.currency_symbol = request.form.get('currency_symbol', '$').strip()
        
        db.session.commit()
        log_audit('CONFIGURACION', 'Ajustes', 'Información de la empresa actualizada')
        flash('Datos de la empresa actualizados exitosamente.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/index.html', company=company)

@settings_bp.route('/users')
@login_required
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('settings/users.html', users=users_list)

@settings_bp.route('/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    username = request.form.get('username', '').strip()
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip() or None
    role = request.form.get('role', 'almacenista')
    password = request.form.get('password', '')

    if User.query.filter_by(username=username).first():
        flash(f"El nombre de usuario '{username}' ya está en uso.", 'danger')
        return redirect(url_for('settings.users'))

    if len(password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", 'warning')
        return redirect(url_for('settings.users'))

    new_user = User(
        username=username,
        full_name=full_name,
        email=email,
        role=role,
        active=True
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    log_audit('CREAR_USUARIO', 'Seguridad', f"Usuario {username} creado con rol {role}")
    flash(f"Usuario '{username}' creado exitosamente.", 'success')
    return redirect(url_for('settings.users'))

@settings_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    if user_id == current_user.id:
        flash('No puede desactivar su propio usuario actual.', 'danger')
        return redirect(url_for('settings.users'))

    target_user = User.query.get_or_404(user_id)
    target_user.active = not target_user.active
    db.session.commit()
    estado = "activado" if target_user.active else "desactivado"
    log_audit('ESTADO_USUARIO', 'Seguridad', f"Usuario {target_user.username} {estado}")
    flash(f"Usuario {target_user.username} {estado}.", 'info')
    return redirect(url_for('settings.users'))

@settings_bp.route('/audit')
@login_required
@admin_required
def audit():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=40, error_out=False)
    return render_template('settings/audit.html', logs=logs)

@settings_bp.route('/backup')
@login_required
@admin_required
def download_backup():
    db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'postgresql' in db_uri:
        flash('El sistema está conectado a Supabase (PostgreSQL en la nube). Los respaldos se gestionan y descargan automáticamente desde el panel de Supabase (Database -> Backups).', 'info')
        return redirect(url_for('settings.index'))

    db_path = os.path.join(current_app.root_path, '..', 'instance', 'inventarios.db')
    db_path = os.path.abspath(db_path)
    if not os.path.exists(db_path):
        flash('Base de datos no encontrada para generar copia.', 'danger')
        return redirect(url_for('settings.index'))

    log_audit('BACKUP', 'Sistema', 'Descarga de respaldo de base de datos SQLite')
    filename = f"Backup_Inventarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    return send_file(
        db_path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/x-sqlite3"
    )
