"""
BlockAccred DEMO data seed script.

Creates demo users, one demo institution/programme, the 5 prototype
parameters, and 20 demo evidence records (submitting each one through the
real evidence_service, so every record gets a real SHA-256 hash AND a real
blockchain transaction on the local Hardhat node).

Run this AFTER:
  1. `npx hardhat node`        (in blockchain/, left running)
  2. `npm run deploy`          (in blockchain/, once, to create deployment.json)

Usage:
    python seed.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import Base, engine, SessionLocal
from app.models import User, Institution, Programme, Criterion, StudentFeedback
from app.auth.security import hash_password
from app.services import evidence_service
from app.blockchain.client import ChainUnavailable
from app.utils.pdf_maker import make_pdf

PARAMETERS = [
    ("Faculty Information", "Faculty qualifications, ratios and experience (demo data)"),
    ("Student Performance", "Academic results and progression (demo data)"),
    ("Placement", "Placement and higher-studies outcomes (demo data)"),
    ("Research/Publications", "Publications, patents and funded projects (demo data)"),
    ("Infrastructure", "Labs, library and campus facilities (demo data)"),
]

random.seed(42)


def get_or_create_user(db, name, email, password, role):
    u = db.query(User).filter(User.email == email).first()
    if u:
        return u
    u = User(name=name, email=email, password_hash=hash_password(password), role=role)
    db.add(u)
    db.flush()
    return u


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    admin = get_or_create_user(db, "College Admin (Demo)", "admin@college.com", "admin123", "admin")
    reviewer = get_or_create_user(db, "NBA Demo Reviewer", "reviewer@nba-demo.com", "reviewer123", "reviewer")
    students = [get_or_create_user(db, f"Demo Student {i}", f"student{i}@college.com" if i else "student@college.com",
                                    "student123", "student") for i in range(0, 6)]
    db.commit()

    inst = db.query(Institution).filter(Institution.institution_code == "XIE-DEMO-001").first()
    if not inst:
        inst = Institution(institution_code="XIE-DEMO-001", name="Xavier Institute of Engineering (DEMO)",
                           address="Demo Road, Demo City", university="Demo University",
                           department="Computer Engineering", academic_year="2026-27")
        db.add(inst)
        db.flush()

    prog = db.query(Programme).filter(Programme.name == "Computer Engineering").first()
    if not prog:
        prog = Programme(institution_id=inst.id, name="Computer Engineering", department="Computer Engineering",
                         academic_year="2026-27", faculty_count=20, student_count=50)
        db.add(prog)
        db.flush()

    crit_by_name = {}
    for name, desc in PARAMETERS:
        c = db.query(Criterion).filter(Criterion.name == name).first()
        if not c:
            c = Criterion(name=name, description=desc, weight=20.0)
            db.add(c)
            db.flush()
        crit_by_name[name] = c
    db.commit()

    if db.query(evidence_service.Evidence).count() == 0:
        print("Submitting 20 demo evidence records (this records 20 real blockchain transactions)...")
        # base values per parameter + 3 intentionally unusual values (for anomaly demo)
        plan = []
        base = {"Faculty Information": 84, "Student Performance": 80, "Placement": 84,
                "Research/Publications": 75, "Infrastructure": 83}
        for name in crit_by_name:
            for i in range(4):
                plan.append((name, round(base[name] + random.uniform(-3, 3), 1)))
        plan += [("Placement", 98.0), ("Faculty Information", 99.0), ("Research/Publications", 41.0)]
        random.shuffle(plan)

        for idx, (pname, value) in enumerate(plan, start=1):
            crit = crit_by_name[pname]
            pdf_bytes = make_pdf(f"{pname} Evidence Report (DEMO)",
                                 [f"Institution: {inst.name}", f"Programme: {prog.name}",
                                  f"Parameter: {pname}", f"Claimed value: {value}%",
                                  "This is fictional demo data for an academic prototype.",
                                  f"Record #{idx}"])
            try:
                ev = evidence_service.create_evidence(db, admin, prog, crit, value,
                                                      f"Demo evidence for {pname}", pdf_bytes,
                                                      f"{pname.lower().replace('/', '_').replace(' ', '_')}_{idx}.pdf")
            except ChainUnavailable as e:
                print("\nERROR: could not reach the local blockchain:", e)
                print("Start 'npx hardhat node' and run 'npm run deploy' in blockchain/, then re-run seed.py.")
                sys.exit(1)
            if idx == 1:
                # keep one original PDF around on disk so the tamper-detection demo has something to edit
                with open(os.path.join(os.path.dirname(__file__), "..", "demo_documents", "placement_report.pdf"), "wb") as f:
                    pass
        # Also save a clean copy of a placement report the user can tamper with in the demo
        demo_pdf = make_pdf("Placement Evidence Report (DEMO)",
                            ["Institution: Xavier Institute of Engineering (DEMO)", "Programme: Computer Engineering",
                             "Parameter: Placement", "Claimed value: 85%",
                             "This is fictional demo data for an academic prototype."])
        os.makedirs(os.path.join(os.path.dirname(__file__), "..", "demo_documents"), exist_ok=True)
        with open(os.path.join(os.path.dirname(__file__), "..", "demo_documents", "placement_report.pdf"), "wb") as f:
            f.write(demo_pdf)
        print("Saved demo_documents/placement_report.pdf for the tamper-detection demo.")
        db.commit()
    else:
        print("Evidence already exists, skipping evidence seeding.")

    if db.query(StudentFeedback).count() == 0:
        for i, s in enumerate(students):
            db.add(StudentFeedback(student_id=s.id, teaching_quality=random.randint(3, 5),
                                   infrastructure=random.randint(3, 5), faculty_support=random.randint(3, 5),
                                   overall_satisfaction=random.randint(3, 5), comment="Demo feedback"))
        db.commit()
        print("Seeded student feedback.")

    print("\nDemo data ready.")
    print("Login accounts:")
    print("  College Admin : admin@college.com / admin123")
    print("  Reviewer      : reviewer@nba-demo.com / reviewer123")
    print("  Student       : student@college.com / student123")


if __name__ == "__main__":
    main()
