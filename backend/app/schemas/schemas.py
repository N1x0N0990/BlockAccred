from typing import Optional
from pydantic import BaseModel


class RegisterIn(BaseModel):
    name: str
    email: str
    password: str
    role: str = "student"


class LoginIn(BaseModel):
    email: str
    password: str


class RejectIn(BaseModel):
    reason: str


class InstitutionIn(BaseModel):
    institution_code: str
    name: str
    address: Optional[str] = ""
    university: Optional[str] = ""
    department: Optional[str] = ""
    academic_year: Optional[str] = ""


class ProgrammeIn(BaseModel):
    institution_id: int
    name: str
    department: Optional[str] = ""
    academic_year: Optional[str] = ""
    faculty_count: Optional[int] = 0
    student_count: Optional[int] = 0


class CriterionIn(BaseModel):
    weight: float


class FeedbackIn(BaseModel):
    teaching_quality: int
    infrastructure: int
    faculty_support: int
    overall_satisfaction: int
    comment: Optional[str] = ""
