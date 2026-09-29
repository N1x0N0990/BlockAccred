from app.models import AuditLog


def log(db, user, action, entity="", details=""):
    db.add(AuditLog(user_id=user.id if user else None, actor=(f"{user.name} ({user.role})" if user else "System"),
                    action=action, entity=entity, details=details))
