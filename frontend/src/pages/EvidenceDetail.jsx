import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import StatusBadge from "../components/StatusBadge";
import HashText from "../components/HashText";
import HashCompare from "../components/HashCompare";

export default function EvidenceDetail() {
  const { id, code } = useParams();
  const evidenceId = id || code;
  const { user } = useAuth();
  const [ev, setEv] = useState(null);
  const [versions, setVersions] = useState([]);
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");
  const [reason, setReason] = useState("");
  const [checking, setChecking] = useState(false);
  const [checkResult, setCheckResult] = useState(null);
  const [tamperFile, setTamperFile] = useState(null);

  function load() {
    api.get(`/evidence/${evidenceId}`).then((r) => setEv(r.data)).catch((e) => setError(e.message));
    api.get(`/evidence/${evidenceId}/versions`).then((r) => setVersions(r.data));
  }
  useEffect(load, [evidenceId]);

  async function verify() {
    setError(""); setMsg("");
    try { await api.post(`/evidence/${evidenceId}/verify`); setMsg("Evidence verified."); load(); }
    catch (err) { setError(err.message); }
  }

  async function reject() {
    setError(""); setMsg("");
    if (!reason.trim()) { setError("Enter a rejection reason first."); return; }
    try { await api.post(`/evidence/${evidenceId}/reject`, { reason }); setMsg("Evidence marked as Requires Revision."); setReason(""); load(); }
    catch (err) { setError(err.message); }
  }

  async function checkIntegrity(useFile) {
    setError(""); setCheckResult(null); setChecking(true);
    try {
      const fd = new FormData();
      fd.append("version", ev.current_version);
      if (useFile && tamperFile) fd.append("file", tamperFile);
      const { data } = await api.post(`/evidence/${evidenceId}/check-integrity`, fd, { headers: { "Content-Type": "multipart/form-data" } });
      setCheckResult(data);
      load();
    } catch (err) { setError(err.message); }
    finally { setChecking(false); }
  }

  if (error && !ev) return <div className="alert alert-error">{error}</div>;
  if (!ev) return <div className="empty">Loading…</div>;

  return (
    <div>
      <div className="card">
        <div className="flex-between">
          <div>
            <h2 style={{ marginBottom: 4 }}>{ev.code} — {ev.parameter}</h2>
            <p className="muted" style={{ margin: 0 }}>{ev.programme} · submitted by {ev.submitted_by}</p>
          </div>
          <StatusBadge status={ev.status} />
        </div>
        {error && <div className="alert alert-error section-gap">{error}</div>}
        {msg && <div className="alert alert-ok section-gap">{msg}</div>}
        <table className="section-gap">
          <tbody>
            <tr><td className="muted" style={{ width: 180 }}>Claimed value</td><td>{ev.claimed_value}%</td></tr>
            <tr><td className="muted">Description</td><td>{ev.description || "—"}</td></tr>
            <tr><td className="muted">Current version</td><td>v{ev.current_version}</td></tr>
            <tr><td className="muted">Document</td><td>{ev.filename}</td></tr>
            <tr><td className="muted">SHA-256 hash</td><td><HashText hash={ev.document_hash} length={64} /></td></tr>
            <tr><td className="muted">Blockchain</td><td>{ev.blockchain_recorded ? <span className="badge badge-onchain">Recorded — block {ev.block_number}</span> : "Not recorded"}</td></tr>
          </tbody>
        </table>

        {user.role === "reviewer" && ev.status === "Pending Review" && (
          <div className="section-gap">
            <div className="tag-row">
              <button className="btn btn-chain" onClick={verify}>Verify evidence</button>
            </div>
            <div className="field section-gap" style={{ maxWidth: 420 }}>
              <label>Rejection reason (required to reject)</label>
              <textarea rows={2} value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. Supporting document does not match submitted value." />
            </div>
            <button className="btn btn-red" onClick={reject}>Reject / request revision</button>
          </div>
        )}
      </div>

      <div className="card section-gap">
        <h3>Integrity check — compare current document with blockchain record</h3>
        <p className="muted">Check the document currently on file, or upload a (possibly modified) copy to see whether the hash still matches.</p>
        <div className="tag-row">
          <button className="btn btn-outline btn-sm" onClick={() => checkIntegrity(false)} disabled={checking}>Check stored document</button>
        </div>
        <div className="field section-gap" style={{ maxWidth: 420 }}>
          <label>Or upload a document to compare</label>
          <div className="field-file">
            <input type="file" onChange={(e) => setTamperFile(e.target.files[0])} />
          </div>
        </div>
        <button className="btn btn-sm" onClick={() => checkIntegrity(true)} disabled={checking || !tamperFile}>
          {checking ? "Checking…" : "Compare uploaded file"}
        </button>
        {checkResult && <div className="section-gap"><HashCompare result={checkResult} /></div>}
      </div>

      <div className="card section-gap">
        <h3>Version history</h3>
        {versions.length === 0 ? <div className="empty">No versions yet.</div> : (
          <table>
            <thead><tr><th>Version</th><th>Claimed value</th><th>Hash</th><th>Blockchain</th><th>Submitted</th></tr></thead>
            <tbody>
              {versions.map((v) => (
                <tr key={v.version}>
                  <td>v{v.version}</td>
                  <td>{v.claimed_value}%</td>
                  <td><HashText hash={v.document_hash} /></td>
                  <td>{v.blockchain_recorded ? <span className="badge badge-onchain">✓ Recorded</span> : "—"}</td>
                  <td className="muted">{new Date(v.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
