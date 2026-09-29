"""Core workflow: hash -> database -> blockchain -> audit trail."""
import os
import uuid
from dotenv import load_dotenv
from app.blockchain import client as chain
from app.models import (Evidence, EvidenceVersion, Document, BlockchainRecord, VerificationRecord)
from app.services import audit, anomaly_service
from app.utils.hashing import sha256_bytes, sha256_file

load_dotenv()
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")


def _store_version(db, user, evidence, claimed_value, description, data: bytes, filename: str):
    version_no = (evidence.current_version + 1) if evidence.versions else 1
    doc_hash = sha256_bytes(data)                                        # 1) SHA-256
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_name = os.path.basename(filename or "document.pdf").replace(" ", "_")
    path = os.path.join(UPLOAD_DIR, f"{evidence.code}_v{version_no}_{safe_name}")

    ver = EvidenceVersion(evidence_id=evidence.id, version=version_no, claimed_value=claimed_value,
                          description=description, document_hash=doc_hash, submitted_by=user.id)
    db.add(ver)
    db.flush()
    db.add(Document(version_id=ver.id, original_filename=safe_name, stored_path=path, size_bytes=len(data), sha256=doc_hash))
    audit.log(db, user, "SHA-256 hash generated", evidence.code, f"v{version_no} {doc_hash}")

    inst_code = evidence.programme.institution.institution_code
    try:
        tx = chain.register_evidence(evidence.code, version_no, doc_hash, inst_code)   # 2) blockchain
    except Exception:
        db.rollback()
        raise
    with open(path, "wb") as f:                                          # file saved only after chain success
        f.write(data)
    db.add(BlockchainRecord(evidence_id=evidence.id, version=version_no, document_hash=doc_hash, tx_hash=tx["tx_hash"],
                            block_number=tx["block_number"], contract_address=tx["contract_address"]))
    audit.log(db, user, "Blockchain record created", evidence.code, f"v{version_no} tx {tx['tx_hash'][:18]}... block {tx['block_number']}")

    evidence.current_version = version_no
    evidence.claimed_value = claimed_value
    evidence.description = description
    evidence.status = "Pending Review"
    anomaly_service.check_value(db, evidence, claimed_value)             # 3) ML check
    return ver


def create_evidence(db, user, programme, criterion, claimed_value, description, data, filename):
    ev = Evidence(code="TMP-" + uuid.uuid4().hex[:8], programme_id=programme.id, criterion_id=criterion.id,
                  submitted_by=user.id, claimed_value=claimed_value, description=description, current_version=0)
    db.add(ev)
    db.flush()
    ev.code = f"EV{ev.id:03d}"
    db.flush()
    db.refresh(ev)
    audit.log(db, user, "Evidence submitted", ev.code, f"{criterion.name}: claimed {claimed_value}")
    _store_version(db, user, ev, claimed_value, description, data, filename)
    db.commit()
    return ev


def add_version(db, user, evidence, claimed_value, description, data, filename):
    audit.log(db, user, "New evidence version submitted", evidence.code, f"claimed {claimed_value}")
    _store_version(db, user, evidence, claimed_value, description, data, filename)
    db.commit()
    return evidence


def get_version(evidence, version_no):
    for v in evidence.versions:
        if v.version == version_no:
            return v
    return None


def compare_hash(db, user, evidence, version_no, current_hash, source):
    """Compare a document hash with the hash stored on the blockchain."""
    chain_rec = chain.get_evidence(evidence.code, version_no)
    ver = get_version(evidence, version_no)
    chain_hash = chain_rec["documentHash"] if chain_rec else None
    if chain_hash is None:
        result = "Not Recorded"
    elif chain_hash == current_hash:
        result = "Integrity Verified"
    else:
        result = "Hash Mismatch"
    match = result == "Integrity Verified"
    db.add(VerificationRecord(evidence_id=evidence.id, version=version_no, user_id=user.id if user else None,
                              action="integrity_check", result=result, reason=source))
    audit.log(db, user, f"Integrity check: {result}", evidence.code, f"v{version_no} ({source})")
    if result == "Hash Mismatch" and version_no == evidence.current_version:
        evidence.status = "Flagged"
    db.commit()
    return {"evidence_id": evidence.code, "version": version_no, "match": match, "result": result,
            "chain_hash": chain_hash, "current_hash": current_hash,
            "db_hash": ver.document_hash if ver else None, "chain_record": chain_rec,
            "message": ("The document matches the blockchain record." if match else
                        "The current document does not match the original blockchain-recorded hash. Requires review.")}


def stored_file_hash(evidence, version_no):
    ver = get_version(evidence, version_no)
    if not ver or not ver.document or not os.path.exists(ver.document.stored_path):
        return None
    return sha256_file(ver.document.stored_path)
