"""All 13 database tables in one readable file."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


def now():
    return datetime.now()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False)  # admin | reviewer | student
    created_at = Column(DateTime, default=now)


class Institution(Base):
    __tablename__ = "institutions"
    id = Column(Integer, primary_key=True)
    institution_code = Column(String(40), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    address = Column(String(250))
    university = Column(String(150))
    department = Column(String(100))
    academic_year = Column(String(20))
    created_at = Column(DateTime, default=now)
    programmes = relationship("Programme", back_populates="institution")


class Programme(Base):
    __tablename__ = "programmes"
    id = Column(Integer, primary_key=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), index=True, nullable=False)
    name = Column(String(120), nullable=False)
    department = Column(String(100))
    academic_year = Column(String(20))
    faculty_count = Column(Integer, default=0)   # representative demo figure
    student_count = Column(Integer, default=0)   # representative demo figure
    created_at = Column(DateTime, default=now)
    institution = relationship("Institution", back_populates="programmes")


class Criterion(Base):
    """Prototype assessment parameter (NOT an official NBA criterion)."""
    __tablename__ = "criteria"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(250))
    weight = Column(Float, default=20.0)  # percent


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, index=True)  # EV001
    programme_id = Column(Integer, ForeignKey("programmes.id"), index=True)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), index=True)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    claimed_value = Column(Float)
    description = Column(Text)
    status = Column(String(30), default="Pending Review")  # Pending Review | Verified | Requires Revision | Flagged
    current_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now, onupdate=now)

    programme = relationship("Programme")
    criterion = relationship("Criterion")
    submitter = relationship("User")
    versions = relationship("EvidenceVersion", back_populates="evidence", order_by="EvidenceVersion.version")
    blockchain_records = relationship("BlockchainRecord", back_populates="evidence", order_by="BlockchainRecord.version")


class EvidenceVersion(Base):
    __tablename__ = "evidence_versions"
    id = Column(Integer, primary_key=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), index=True, nullable=False)
    version = Column(Integer, nullable=False)
    claimed_value = Column(Float)
    description = Column(Text)
    document_hash = Column(String(64), nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=now)
    evidence = relationship("Evidence", back_populates="versions")
    document = relationship("Document", uselist=False, back_populates="version")
    submitter = relationship("User")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    version_id = Column(Integer, ForeignKey("evidence_versions.id"), index=True, nullable=False)
    original_filename = Column(String(200))
    stored_path = Column(String(300))
    size_bytes = Column(Integer)
    sha256 = Column(String(64), nullable=False)
    uploaded_at = Column(DateTime, default=now)
    version = relationship("EvidenceVersion", back_populates="document")


class VerificationRecord(Base):
    __tablename__ = "verification_records"
    id = Column(Integer, primary_key=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), index=True)
    version = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(30))   # verified | rejected | integrity_check
    result = Column(String(40))   # Verified | Requires Revision | Integrity Verified | Hash Mismatch | Not Recorded
    reason = Column(Text)
    created_at = Column(DateTime, default=now)
    user = relationship("User")


class BlockchainRecord(Base):
    __tablename__ = "blockchain_records"
    id = Column(Integer, primary_key=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), index=True, nullable=False)
    version = Column(Integer, nullable=False)
    document_hash = Column(String(64), nullable=False)
    tx_hash = Column(String(80))
    block_number = Column(Integer)
    contract_address = Column(String(60))
    created_at = Column(DateTime, default=now)
    evidence = relationship("Evidence", back_populates="blockchain_records")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    actor = Column(String(120))
    action = Column(String(60), index=True)
    entity = Column(String(40))
    details = Column(Text)
    created_at = Column(DateTime, default=now, index=True)


class StudentFeedback(Base):
    __tablename__ = "student_feedback"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), index=True)
    teaching_quality = Column(Integer)
    infrastructure = Column(Integer)
    faculty_support = Column(Integer)
    overall_satisfaction = Column(Integer)
    comment = Column(String(300))
    created_at = Column(DateTime, default=now)
    student = relationship("User")


class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), index=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=True)
    year = Column(Integer)
    value = Column(Float)
    anomaly_score = Column(Float)
    status = Column(String(30), default="Requires Review")
    created_at = Column(DateTime, default=now)
    criterion = relationship("Criterion")
    evidence = relationship("Evidence")


class Score(Base):
    """Snapshot of the Prototype Assessment Score."""
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True)
    programme_id = Column(Integer, ForeignKey("programmes.id"), index=True)
    criterion_id = Column(Integer, ForeignKey("criteria.id"))
    score = Column(Float)
    weight = Column(Float)
    computed_at = Column(DateTime, default=now)
    criterion = relationship("Criterion")
