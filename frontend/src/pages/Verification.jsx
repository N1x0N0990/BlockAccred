import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";
import HashText from "../components/HashText";

export default function Verification() {
  const [rows, setRows] = useState([]);

  useEffect(() => { api.get("/evidence").then((r) => setRows(r.data)); }, []);

  return (
    <div className="card">
      <h2>Integrity check overview</h2>
      <p className="muted">Every evidence record's blockchain status at a glance. Open a record to run a document-hash comparison against its blockchain record — the core tamper-detection demonstration.</p>
      {rows.length === 0 ? <div className="empty">No evidence yet.</div> : (
        <table>
          <thead><tr><th>ID</th><th>Parameter</th><th>Hash</th><th>Blockchain</th><th>Status</th><th></th></tr></thead>
          <tbody>
            {rows.map((e) => (
              <tr key={e.id}>
                <td className="mono">{e.code}</td>
                <td>{e.parameter}</td>
                <td><HashText hash={e.document_hash} /></td>
                <td>{e.blockchain_recorded ? <span className="badge badge-onchain">Recorded</span> : <span className="badge badge-pending">Not recorded</span>}</td>
                <td><StatusBadge status={e.status} /></td>
                <td><Link to={`/evidence/${e.code}`} className="btn btn-sm btn-outline">Check integrity</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
