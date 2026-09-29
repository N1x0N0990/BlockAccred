from app.ml import detector
from app.models import Anomaly, Evidence

CURRENT_YEAR = 2026


def check_value(db, evidence, value):
    """Score one claimed value; store an Anomaly row if it looks unusual."""
    r = detector.score(evidence.criterion.name, value)
    if r["is_anomaly"]:
        db.add(Anomaly(criterion_id=evidence.criterion_id, evidence_id=evidence.id, year=CURRENT_YEAR,
                       value=value, anomaly_score=r["anomaly_score"], status="Requires Review"))
    return r


def rescan(db):
    """Re-score the current claim of every evidence record."""
    db.query(Anomaly).delete()
    db.flush()
    found = 0
    for e in db.query(Evidence).all():
        if e.claimed_value is not None and check_value(db, e, e.claimed_value)["is_anomaly"]:
            found += 1
    return found
