def iso(d):
    return d.isoformat() if d else None


def evidence_dict(e):
    cur = next((v for v in e.versions if v.version == e.current_version), None)
    rec = next((r for r in e.blockchain_records if r.version == e.current_version), None)
    prog = e.programme
    return {
        "id": e.id, "code": e.code, "institution": prog.institution.name if prog else None,
        "programme": prog.name if prog else None, "criterion_id": e.criterion_id,
        "parameter": e.criterion.name if e.criterion else None, "claimed_value": e.claimed_value,
        "description": e.description, "status": e.status, "current_version": e.current_version,
        "submitted_by": e.submitter.name if e.submitter else None, "created_at": iso(e.created_at),
        "document_hash": cur.document_hash if cur else None,
        "filename": cur.document.original_filename if cur and cur.document else None,
        "blockchain_recorded": rec is not None, "tx_hash": rec.tx_hash if rec else None,
        "block_number": rec.block_number if rec else None,
    }


def version_dict(e, v):
    rec = next((r for r in e.blockchain_records if r.version == v.version), None)
    return {"version": v.version, "claimed_value": v.claimed_value, "description": v.description,
            "document_hash": v.document_hash, "created_at": iso(v.created_at),
            "submitted_by": v.submitter.name if v.submitter else None,
            "filename": v.document.original_filename if v.document else None,
            "blockchain_recorded": rec is not None, "tx_hash": rec.tx_hash if rec else None,
            "block_number": rec.block_number if rec else None}
