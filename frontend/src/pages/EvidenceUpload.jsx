import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";

export default function EvidenceUpload() {
  const navigate = useNavigate();
  const [programmes, setProgrammes] = useState([]);
  const [criteria, setCriteria] = useState([]);
  const [programmeId, setProgrammeId] = useState("");
  const [criterionId, setCriterionId] = useState("");
  const [value, setValue] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.get("/programmes").then((r) => { setProgrammes(r.data); if (r.data[0]) setProgrammeId(r.data[0].id); });
    api.get("/criteria").then((r) => { setCriteria(r.data); if (r.data[0]) setCriterionId(r.data[0].id); });
  }, []);

  async function submit(e) {
    e.preventDefault();
    setError(""); setResult(null);
    if (!file) { setError("Please choose a document to upload."); return; }
    setBusy(true);
    const fd = new FormData();
    fd.append("programme_id", programmeId);
    fd.append("criterion_id", criterionId);
    fd.append("claimed_value", value);
    fd.append("description", description);
    fd.append("file", file);
    try {
      const { data } = await api.post("/evidence", fd, { headers: { "Content-Type": "multipart/form-data" } });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (result) {
    return (
      <div className="card" style={{ maxWidth: 560 }}>
        <div className="alert alert-ok">Evidence submitted, hashed, and recorded on the blockchain.</div>
        <table>
          <tbody>
            <tr><td className="muted">Evidence ID</td><td className="mono">{result.code}</td></tr>
            <tr><td className="muted">Parameter</td><td>{result.parameter}</td></tr>
            <tr><td className="muted">Claimed value</td><td>{result.claimed_value}%</td></tr>
            <tr><td className="muted">SHA-256</td><td className="mono" style={{ wordBreak: "break-all" }}>{result.document_hash}</td></tr>
            <tr><td className="muted">Version</td><td>{result.current_version}</td></tr>
            <tr><td className="muted">Status</td><td>{result.status}</td></tr>
            <tr><td className="muted">Blockchain tx</td><td className="mono" style={{ wordBreak: "break-all" }}>{result.tx_hash}</td></tr>
          </tbody>
        </table>
        <div className="tag-row section-gap">
          <button className="btn" onClick={() => navigate(`/evidence/${result.code}`)}>View evidence</button>
          <button className="btn btn-outline" onClick={() => setResult(null)}>Submit another</button>
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ maxWidth: 560 }}>
      <h2>Submit evidence</h2>
      <p className="muted">Select a parameter, enter the claimed value, and upload the supporting document. The system will generate its SHA-256 hash and record it on the local blockchain.</p>
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={submit}>
        <div className="field"><label>Programme</label>
          <select value={programmeId} onChange={(e) => setProgrammeId(e.target.value)}>
            {programmes.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select></div>
        <div className="field"><label>Prototype parameter</label>
          <select value={criterionId} onChange={(e) => setCriterionId(e.target.value)}>
            {criteria.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select></div>
        <div className="field"><label>Claimed value (%)</label>
          <input type="number" step="0.1" value={value} onChange={(e) => setValue(e.target.value)} required /></div>
        <div className="field"><label>Description</label>
          <textarea rows={3} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Short note about this evidence" /></div>
        <div className="field">
          <label>Supporting document (PDF or any file)</label>
          <div className="field-file">
            <input type="file" onChange={(e) => setFile(e.target.files[0])} />
          </div>
        </div>
        <button className="btn" disabled={busy}>{busy ? "Submitting…" : "Generate hash and submit"}</button>
      </form>
    </div>
  );
}
