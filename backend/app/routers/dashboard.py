from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.security import get_current_user
from app.database import get_db
from app.models import Evidence, BlockchainRecord, Anomaly, Institution, Programme, VerificationRecord
from app.services import scoring

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    evs = db.query(Evidence).all()
    counts = {"submitted": len(evs), "verified": sum(1 for e in evs if e.status == "Verified"),
              "pending": sum(1 for e in evs if e.status == "Pending Review"),
              "flagged": sum(1 for e in evs if e.status in ("Flagged", "Requires Revision"))}
    integ = db.query(VerificationRecord).filter(VerificationRecord.action == "integrity_check").all()
    integrity_verified = sum(1 for i in integ if i.result == "Integrity Verified")
    inst = db.query(Institution).first()
    prog = db.query(Programme).first()
    score = scoring.compute(db, programme_id=prog.id if prog else None, save=False)
    return {
        "institution": inst.name if inst else None, "programme": prog.name if prog else None,
        "evidence": counts, "blockchain_records": db.query(BlockchainRecord).count(),
        "integrity_verified": integrity_verified, "anomalies": db.query(Anomaly).count(),
        "prototype_score": score,
    }
