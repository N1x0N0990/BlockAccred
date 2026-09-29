from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.security import get_current_user
from app.database import get_db
from app.services import scoring

router = APIRouter(prefix="/scores", tags=["scores"])


@router.get("")
def get_scores(programme_id: int | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return scoring.compute(db, programme_id=programme_id)
