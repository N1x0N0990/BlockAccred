import { useEffect, useState } from "react";
import { api } from "../services/api";
import AuditTimeline from "../components/AuditTimeline";

export default function AuditTrail() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get("/audit?limit=300").then((r) => setItems(r.data)); }, []);
  return (
    <div className="card">
      <h2>Audit trail</h2>
      <p className="muted">Chronological record of every important action: submissions, hashing, blockchain recording, reviews, and integrity checks.</p>
      <div className="section-gap">
        <AuditTimeline items={[...items].reverse()} />
      </div>
    </div>
  );
}
