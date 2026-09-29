from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.security import get_current_user, require_roles
from app.database import get_db
from app.models import Anomaly
from app.services import anomaly_service, audit
from app.ml import detector

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("")
def list_anomalies(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(Anomaly).order_by(Anomaly.created_at.desc()).all()
    return [{"id": a.id, "parameter": a.criterion.name, "evidence_id": a.evidence.code if a.evidence else None,
             "year": a.year, "value": a.value, "anomaly_score": a.anomaly_score, "status": a.status,
             "created_at": a.created_at.isoformat()} for a in rows]


@router.get("/history/{parameter}")
def history(parameter: str, user=Depends(get_current_user)):
    return detector.history(parameter)


@router.post("/rescan")
def rescan(db: Session = Depends(get_db), user=Depends(require_roles("admin", "reviewer"))):
    found = anomaly_service.rescan(db)
    audit.log(db, user, "Anomaly rescan run", "anomalies", f"{found} flagged")
    db.commit()
    return {"flagged": found}
