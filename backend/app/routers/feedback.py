from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.security import get_current_user, require_roles
from app.database import get_db
from app.models import StudentFeedback
from app.schemas import FeedbackIn
from app.services import audit

router = APIRouter(prefix="/feedback", tags=["feedback"])


def _avg_pct(rows):
    if not rows:
        return None
    total = sum(r.teaching_quality + r.infrastructure + r.faculty_support + r.overall_satisfaction for r in rows)
    return round(total / (len(rows) * 4) / 5 * 100, 1)  # 4 questions, scale 1-5 -> percent


@router.post("")
def submit_feedback(body: FeedbackIn, db: Session = Depends(get_db), user=Depends(require_roles("student"))):
    for field in ("teaching_quality", "infrastructure", "faculty_support", "overall_satisfaction"):
        v = getattr(body, field)
        if v < 1 or v > 5:
            raise HTTPException(400, f"{field} must be between 1 and 5")
    fb = StudentFeedback(student_id=user.id, **body.model_dump())
    db.add(fb)
    audit.log(db, user, "Student feedback submitted", "feedback", f"overall {body.overall_satisfaction}/5")
    db.commit()
    return {"id": fb.id, "message": "Feedback submitted"}


@router.get("")
def list_feedback(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(StudentFeedback).order_by(StudentFeedback.created_at.desc()).all()
    if user.role == "student":
        rows = [r for r in rows if r.student_id == user.id]
    return [{"id": r.id, "student": r.student.name if r.student else "Anonymous", "teaching_quality": r.teaching_quality,
             "infrastructure": r.infrastructure, "faculty_support": r.faculty_support,
             "overall_satisfaction": r.overall_satisfaction, "comment": r.comment,
             "created_at": r.created_at.isoformat()} for r in rows]


@router.get("/summary")
def feedback_summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.query(StudentFeedback).all()
    return {"count": len(rows), "average_percent": _avg_pct(rows)}
