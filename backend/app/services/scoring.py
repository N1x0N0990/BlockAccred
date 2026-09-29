"""Prototype Assessment Score = weighted average of the parameter scores (NOT an NBA score)."""
from app.models import Criterion, Evidence, Score, Programme


def latest_claims(db, criterion_id):
    rows = db.query(Evidence).filter(Evidence.criterion_id == criterion_id).all()
    return [e.claimed_value for e in rows if e.claimed_value is not None]


def compute(db, programme_id=None, save=True):
    criteria = db.query(Criterion).order_by(Criterion.id).all()
    total_w = sum(c.weight for c in criteria) or 1
    breakdown, overall = [], 0.0
    for c in criteria:
        vals = latest_claims(db, c.id)
        s = round(sum(vals) / len(vals), 1) if vals else 0.0
        breakdown.append({"criterion_id": c.id, "parameter": c.name, "weight": c.weight, "score": s, "evidence_count": len(vals)})
        overall += s * c.weight / total_w
    overall = round(overall, 1)
    if save:
        prog = db.get(Programme, programme_id) if programme_id else db.query(Programme).first()
        if prog:
            db.query(Score).filter(Score.programme_id == prog.id).delete()
            for b in breakdown:
                db.add(Score(programme_id=prog.id, criterion_id=b["criterion_id"], score=b["score"], weight=b["weight"]))
    return {"label": "Prototype Assessment Score", "overall": overall, "out_of": 100, "breakdown": breakdown}
