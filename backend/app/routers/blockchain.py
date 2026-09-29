from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.security import get_current_user
from app.database import get_db
from app.models import Evidence, BlockchainRecord
from app.blockchain import client as chain

router = APIRouter(prefix="/blockchain", tags=["blockchain"])


@router.get("/status")
def blockchain_status(user=Depends(get_current_user)):
    return chain.status()


@router.get("/{code}")
def evidence_chain(code: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    ev = db.query(Evidence).filter(Evidence.code == code).first()
    if not ev:
        raise HTTPException(404, "Evidence not found")
    records = db.query(BlockchainRecord).filter(BlockchainRecord.evidence_id == ev.id).order_by(BlockchainRecord.version).all()
    out = []
    for r in records:
        onchain = chain.get_evidence(ev.code, r.version)
        out.append({"version": r.version, "document_hash": r.document_hash, "tx_hash": r.tx_hash,
                    "block_number": r.block_number, "contract_address": r.contract_address,
                    "onchain_status": onchain["status"] if onchain else "Not Found",
                    "onchain_hash": onchain["documentHash"] if onchain else None})
    return {"evidence_id": ev.code, "records": out}
