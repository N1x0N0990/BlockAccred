import { useEffect, useState } from "react";
import { api } from "../services/api";
import HashText from "../components/HashText";

export default function Blockchain() {
  const [status, setStatus] = useState(null);
  const [code, setCode] = useState("");
  const [record, setRecord] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => { api.get("/blockchain/status").then((r) => setStatus(r.data)); }, []);

  async function lookup(e) {
    e.preventDefault();
    setError(""); setRecord(null);
    try { const { data } = await api.get(`/blockchain/${code.trim()}`); setRecord(data); }
    catch (err) { setError(err.message); }
  }

  return (
    <div>
      <div className="card">
        <h2>Local blockchain status</h2>
        {!status ? <div className="empty">Loading…</div> : !status.online ? (
          <div className="alert alert-error">{status.message}</div>
        ) : (
          <table>
            <tbody>
              <tr><td className="muted" style={{ width: 180 }}>Network</td><td>{status.network} (chain id {status.chain_id})</td></tr>
              <tr><td className="muted">Contract address</td><td className="mono">{status.address}</td></tr>
              <tr><td className="muted">Latest block</td><td>{status.block_number}</td></tr>
              <tr><td className="muted">Total records on-chain</td><td>{status.total_records}</td></tr>
            </tbody>
          </table>
        )}
      </div>

      <div className="card section-gap">
        <h3>Look up an evidence record</h3>
        <form onSubmit={lookup} className="tag-row" style={{ alignItems: "flex-end" }}>
          <div className="field" style={{ marginBottom: 0, flex: 1, maxWidth: 240 }}>
            <label>Evidence ID</label>
            <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="EV001" />
          </div>
          <button className="btn btn-sm">Look up</button>
        </form>
        {error && <div className="alert alert-error section-gap">{error}</div>}
        {record && (
          <table className="section-gap">
            <thead><tr><th>Version</th><th>Document hash</th><th>Tx hash</th><th>Block</th><th>On-chain status</th></tr></thead>
            <tbody>
              {record.records.map((r) => (
                <tr key={r.version}>
                  <td>v{r.version}</td>
                  <td><HashText hash={r.document_hash} /></td>
                  <td><HashText hash={r.tx_hash} /></td>
                  <td>{r.block_number}</td>
                  <td><span className="badge badge-onchain">{r.onchain_status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
