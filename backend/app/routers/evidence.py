from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.auth.security import get_current_user, require_roles
from app.database import get_db
from app.models import Evidence, Programme, Criterion, VerificationRecord
from app.schemas import RejectIn
from app.services import evidence_service, audit
from app.utils.serializers import evidence_dict, version_dict
from app.blockchain.client import ChainUnavailable

router = APIRouter(prefix="/evidence", tags=["evidence"])


def _get_evidence_or_404(db, code_or_id):
    ev = db.query(Evidence).filter(Evidence.code == str(code_or_id)).first()
    if not ev and str(code_or_id).isdigit():
        ev = db.get(Evidence, int(code_or_id))
    if not ev:
        raise HTTPException(404, "Evidence not found")
    return ev


@router.get("")
def list_evidence(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [evidence_dict(e) for e in db.query(Evidence).order_by(Evidence.id.desc()).all()]


@router.post("")
async def submit_evidence(
    programme_id: int = Form(...), criterion_id: int = Form(...), claimed_value: float = Form(...),
    description: str = Form(""), file: UploadFile = File(...),
    db: Session = Depends(get_db), user=Depends(require_roles("admin")),
):
    programme = db.get(Programme, programme_id)
    criterion = db.get(Criterion, criterion_id)
    if not programme or not criterion:
        raise HTTPException(404, "Programme or parameter not found")
    data = await file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty")
    try:
        ev = evidence_service.create_evidence(db, user, programme, criterion, claimed_value, description, data, file.filename)
    except ChainUnavailable as e:
        raise HTTPException(503, str(e))
    return evidence_dict(ev)


@router.post("/{code}/versions")
async def submit_new_version(
    code: str, claimed_value: float = Form(...), description: str = Form(""), file: UploadFile = File(...),
    db: Session = Depends(get_db), user=Depends(require_roles("admin")),
):
    ev = _get_evidence_or_404(db, code)
    data = await file.read()
    if not data:
        raise HTTPException(400, "Uploaded file is empty")
    try:
        evidence_service.add_version(db, user, ev, claimed_value, description, data, file.filename)
    except ChainUnavailable as e:
        raise HTTPException(503, str(e))
    return evidence_dict(ev)


@router.get("/{code}")
def get_evidence(code: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return evidence_dict(_get_evidence_or_404(db, code))


@router.get("/{code}/versions")
def get_versions(code: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ev = _get_evidence_or_404(db, code)
    return [version_dict(ev, v) for v in ev.versions]


@router.post("/{code}/verify")
def verify(code: str, db: Session = Depends(get_db), user=Depends(require_roles("reviewer"))):
    from app.blockchain import client as chain
    ev = _get_evidence_or_404(db, code)
    try:
        chain.verify_evidence(ev.code, ev.current_version, "Verified")
    except ChainUnavailable as e:
        raise HTTPException(503, str(e))
    ev.status = "Verified"
    db.add(VerificationRecord(evidence_id=ev.id, version=ev.current_version, user_id=user.id, action="verified", result="Verified"))
    audit.log(db, user, "Reviewer verified evidence", ev.code, f"v{ev.current_version}")
    db.commit()
    return evidence_dict(ev)


@router.post("/{code}/reject")
def reject(code: str, body: RejectIn, db: Session = Depends(get_db), user=Depends(require_roles("reviewer"))):
    from app.blockchain import client as chain
    if not body.reason.strip():
        raise HTTPException(400, "A rejection reason is required")
    ev = _get_evidence_or_404(db, code)
    try:
        chain.verify_evidence(ev.code, ev.current_version, "Requires Revision")
    except ChainUnavailable as e:
        raise HTTPException(503, str(e))
    ev.status = "Requires Revision"
    db.add(VerificationRecord(evidence_id=ev.id, version=ev.current_version, user_id=user.id, action="rejected",
                              result="Requires Revision", reason=body.reason))
    audit.log(db, user, "Reviewer rejected evidence", ev.code, f"v{ev.current_version}: {body.reason}")
    db.commit()
    return evidence_dict(ev)


@router.post("/{code}/check-integrity")
async def check_integrity(code: str, version: int = Form(...), file: Optional[UploadFile] = File(None),
                          db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Re-hash the current document (or an uploaded replacement) and compare with the blockchain record."""
    ev = _get_evidence_or_404(db, code)
    if file is not None:
        data = await file.read()
        from app.utils.hashing import sha256_bytes
        current_hash = sha256_bytes(data)
        source = f"uploaded file: {file.filename}"
    else:
        current_hash = evidence_service.stored_file_hash(ev, version)
        if current_hash is None:
            raise HTTPException(404, "Stored document not found for that version")
        source = "stored document on server"
    try:
        return evidence_service.compare_hash(db, user, ev, version, current_hash, source)
    except ChainUnavailable as e:
        raise HTTPException(503, str(e))
