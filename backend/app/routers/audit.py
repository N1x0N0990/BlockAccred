from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.security import get_current_user
from app.database import get_db
from app.models import AuditLog

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
def list_audit(entity: str | None = None, limit: int = 200, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
    if entity:
        q = q.filter(AuditLog.entity == entity)
    rows = q.limit(limit).all()
    return [{"id": a.id, "actor": a.actor, "action": a.action, "entity": a.entity, "details": a.details,
             "created_at": a.created_at.isoformat()} for a in rows][::-1]
