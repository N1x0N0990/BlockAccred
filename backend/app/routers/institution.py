from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.security import get_current_user, require_roles
from app.database import get_db
from app.models import Institution, Programme, Criterion
from app.schemas import InstitutionIn, ProgrammeIn, CriterionIn
from app.services import audit

router = APIRouter(tags=["institution"])


def inst_out(i):
    return {"id": i.id, "institution_code": i.institution_code, "name": i.name, "address": i.address,
            "university": i.university, "department": i.department, "academic_year": i.academic_year}


def prog_out(p):
    return {"id": p.id, "institution_id": p.institution_id, "institution": p.institution.name, "name": p.name,
            "department": p.department, "academic_year": p.academic_year,
            "faculty_count": p.faculty_count, "student_count": p.student_count}


@router.get("/institutions")
def list_institutions(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [inst_out(i) for i in db.query(Institution).all()]


@router.post("/institutions")
def save_institution(body: InstitutionIn, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    """Creates the institution, or updates it if the institution_code already exists."""
    i = db.query(Institution).filter(Institution.institution_code == body.institution_code).first()
    action = "Institution updated" if i else "Institution created"
    if not i:
        i = Institution(institution_code=body.institution_code, name=body.name)
        db.add(i)
    for k, v in body.model_dump().items():
        setattr(i, k, v)
    audit.log(db, user, action, "institution", i.name)
    db.commit()
    return inst_out(i)


@router.put("/institutions/{inst_id}")
def update_institution(inst_id: int, body: InstitutionIn, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    i = db.get(Institution, inst_id)
    if not i:
        raise HTTPException(404, "Institution not found")
    for k, v in body.model_dump().items():
        setattr(i, k, v)
    audit.log(db, user, "Institution updated", "institution", i.name)
    db.commit()
    return inst_out(i)


@router.get("/programmes")
def list_programmes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [prog_out(p) for p in db.query(Programme).all()]


@router.post("/programmes")
def create_programme(body: ProgrammeIn, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    p = Programme(**body.model_dump())
    db.add(p)
    audit.log(db, user, "Programme created", "programme", body.name)
    db.commit()
    db.refresh(p)
    return prog_out(p)


@router.put("/programmes/{prog_id}")
def update_programme(prog_id: int, body: ProgrammeIn, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    p = db.get(Programme, prog_id)
    if not p:
        raise HTTPException(404, "Programme not found")
    for k, v in body.model_dump().items():
        setattr(p, k, v)
    audit.log(db, user, "Programme updated", "programme", p.name)
    db.commit()
    return prog_out(p)


@router.get("/criteria")
def list_criteria(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return [{"id": c.id, "name": c.name, "description": c.description, "weight": c.weight}
            for c in db.query(Criterion).order_by(Criterion.id).all()]


@router.put("/criteria/{cid}")
def update_weight(cid: int, body: CriterionIn, db: Session = Depends(get_db), user=Depends(require_roles("admin"))):
    c = db.get(Criterion, cid)
    if not c:
        raise HTTPException(404, "Parameter not found")
    if body.weight < 0 or body.weight > 100:
        raise HTTPException(400, "Weight must be between 0 and 100")
    c.weight = body.weight
    audit.log(db, user, "Parameter weight changed", "criterion", f"{c.name} -> {c.weight}%")
    db.commit()
    return {"id": c.id, "name": c.name, "weight": c.weight}
