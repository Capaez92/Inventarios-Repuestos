from app.models.models import db, AuditLog
from flask_login import current_user
from flask import request

def log_audit(action, module, details):
    try:
        user_id = current_user.id if current_user and current_user.is_authenticated else None
        ip = request.remote_addr if request else None
        entry = AuditLog(
            user_id=user_id,
            action=action,
            module=module,
            details=details,
            ip_address=ip
        )
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        print(f"Error registrando auditoría: {e}")
