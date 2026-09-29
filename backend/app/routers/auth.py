from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.security import hash_password, verify_password, create_token, get_current_user
from app.database import get_db
from app.models import User
from app.schemas import RegisterIn, LoginIn
from app.services import audit

router = APIRouter(prefix="/auth", tags=["auth"])


def user_out(u):
    return {"id": u.id, "name": u.name, "email": u.email, "role": u.role}


@router.post("/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    if body.role not in ("admin", "reviewer", "student"):
        raise HTTPException(400, "Role must be admin, reviewer or student")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    u = User(name=body.name, email=body.email, password_hash=hash_password(body.password), role=body.role)
    db.add(u)
    db.commit()
    return user_out(u)


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == body.email).first()
    if not u or not verify_password(body.password, u.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    audit.log(db, u, "User logged in", "user", u.email)
    db.commit()
    return {"access_token": create_token(u), "token_type": "bearer", "user": user_out(u)}


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user_out(user)
