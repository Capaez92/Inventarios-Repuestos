from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('Acceso restringido: Se requieren permisos de Administrador.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def stock_manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.can_manage_stock():
            flash('Acceso restringido: No tiene permisos para modificar inventario.', 'warning')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
