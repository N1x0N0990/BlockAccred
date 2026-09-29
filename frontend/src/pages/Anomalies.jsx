import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Anomalies() {
  const [rows, setRows] = useState([]);
  const [busy, setBusy] = useState(false);

  function load() { api.get("/anomalies").then((r) => setRows(r.data)); }
  useEffect(load, []);

  async function rescan() {
    setBusy(true);
    try { await api.post("/anomalies/rescan"); load(); } finally { setBusy(false); }
  }

  return (
    <div className="card">
      <div className="flex-between">
        <div>
          <h2>Anomaly detection</h2>
          <p className="muted" style={{ maxWidth: 620 }}>
            A small Isolation Forest model (trained on demo historical data per parameter) flags claimed values that
            differ unusually from prior years. This only identifies unusual patterns — it does not claim manipulation
            or fraud.
          </p>
        </div>
        <button className="btn btn-outline btn-sm" onClick={rescan} disabled={busy}>{busy ? "Scanning…" : "Re-scan all evidence"}</button>
      </div>
      {rows.length === 0 ? <div className="empty">No anomalies flagged.</div> : (
        <table>
          <thead><tr><th>Parameter</th><th>Evidence</th><th>Value</th><th>Anomaly score</th><th>Status</th></tr></thead>
          <tbody>
            {rows.map((a) => (
              <tr key={a.id}>
                <td>{a.parameter}</td>
                <td className="mono">{a.evidence_id || "—"}</td>
                <td>{a.value}%</td>
                <td className="mono">{a.anomaly_score}</td>
                <td><span className="badge badge-flagged">⚠ {a.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
