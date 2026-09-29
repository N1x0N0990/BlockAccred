import { useEffect, useState } from "react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Programme() {
  const { user } = useAuth();
  const [programmes, setProgrammes] = useState([]);
  const [institutions, setInstitutions] = useState([]);
  const [form, setForm] = useState({ institution_id: "", name: "", department: "", academic_year: "", faculty_count: 0, student_count: 0 });
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  function load() {
    api.get("/programmes").then((r) => setProgrammes(r.data));
    api.get("/institutions").then((r) => { setInstitutions(r.data); if (r.data[0]) setForm((f) => ({ ...f, institution_id: r.data[0].id })); });
  }
  useEffect(load, []);

  async function submit(e) {
    e.preventDefault();
    setError(""); setMsg("");
    try {
      await api.post("/programmes", { ...form, institution_id: Number(form.institution_id) });
      setMsg("Programme created.");
      setForm((f) => ({ ...f, name: "", department: "", academic_year: "" }));
      load();
    } catch (err) { setError(err.message); }
  }

  return (
    <div>
      <div className="card">
        <h2>Programmes</h2>
        {programmes.length === 0 ? <div className="empty">No programmes yet.</div> : (
          <table>
            <thead><tr><th>Programme</th><th>Institution</th><th>Department</th><th>Academic year</th><th>Faculty</th><th>Students</th></tr></thead>
            <tbody>
              {programmes.map((p) => (
                <tr key={p.id}><td>{p.name}</td><td>{p.institution}</td><td>{p.department}</td><td>{p.academic_year}</td><td>{p.faculty_count}</td><td>{p.student_count}</td></tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {user.role === "admin" && (
        <div className="card section-gap" style={{ maxWidth: 520 }}>
          <h3>Create / edit a programme</h3>
          {error && <div className="alert alert-error">{error}</div>}
          {msg && <div className="alert alert-ok">{msg}</div>}
          <form onSubmit={submit}>
            <div className="field"><label>Institution</label>
              <select value={form.institution_id} onChange={(e) => setForm((f) => ({ ...f, institution_id: e.target.value }))}>
                {institutions.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}
              </select></div>
            <div className="field"><label>Programme name</label>
              <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required /></div>
            <div className="grid grid-2">
              <div className="field"><label>Department</label>
                <input value={form.department} onChange={(e) => setForm((f) => ({ ...f, department: e.target.value }))} /></div>
              <div className="field"><label>Academic year</label>
                <input value={form.academic_year} onChange={(e) => setForm((f) => ({ ...f, academic_year: e.target.value }))} /></div>
            </div>
            <div className="grid grid-2">
              <div className="field"><label>Faculty count (representative)</label>
                <input type="number" value={form.faculty_count} onChange={(e) => setForm((f) => ({ ...f, faculty_count: Number(e.target.value) }))} /></div>
              <div className="field"><label>Student count (representative)</label>
                <input type="number" value={form.student_count} onChange={(e) => setForm((f) => ({ ...f, student_count: Number(e.target.value) }))} /></div>
            </div>
            <button className="btn">Save programme</button>
          </form>
        </div>
      )}
    </div>
  );
}
