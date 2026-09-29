import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import StatusBadge from "../components/StatusBadge";
import HashText from "../components/HashText";

export default function Reviewer() {
  const [rows, setRows] = useState([]);

  useEffect(() => { api.get("/evidence").then((r) => setRows(r.data)); }, []);
  const pending = rows.filter((r) => r.status === "Pending Review");
  const decided = rows.filter((r) => r.status !== "Pending Review");

  return (
    <div>
      <div className="card">
        <h2>Reviewer queue</h2>
        <p className="muted">Evidence awaiting verification. Open a record to verify, reject with a reason, or run an integrity check.</p>
        {pending.length === 0 ? <div className="empty">Nothing pending review.</div> : (
          <table>
            <thead><tr><th>ID</th><th>Parameter</th><th>Claimed value</th><th>Document hash</th><th>Blockchain</th><th></th></tr></thead>
            <tbody>
              {pending.map((e) => (
                <tr key={e.id}>
                  <td className="mono">{e.code}</td><td>{e.parameter}</td><td>{e.claimed_value}%</td>
                  <td><HashText hash={e.document_hash} /></td>
                  <td>{e.blockchain_recorded ? <span className="badge badge-onchain">Recorded</span> : "—"}</td>
                  <td><Link to={`/evidence/${e.code}`} className="btn btn-sm">Review</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <div className="card section-gap">
        <h3>Already reviewed</h3>
        {decided.length === 0 ? <div className="empty">No reviewed records yet.</div> : (
          <table>
            <thead><tr><th>ID</th><th>Parameter</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {decided.map((e) => (
                <tr key={e.id}>
                  <td className="mono">{e.code}</td><td>{e.parameter}</td><td><StatusBadge status={e.status} /></td>
                  <td><Link to={`/evidence/${e.code}`} className="btn btn-sm btn-outline">Open</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
