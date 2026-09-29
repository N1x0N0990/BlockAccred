import { useEffect, useState } from "react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

const EMPTY = { institution_code: "", name: "", address: "", university: "", department: "", academic_year: "" };

export default function Institution() {
  const { user } = useAuth();
  const [form, setForm] = useState(EMPTY);
  const [savedMsg, setSavedMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/institutions").then((r) => { if (r.data[0]) setForm(r.data[0]); });
  }, []);

  function set(k, v) { setForm((f) => ({ ...f, [k]: v })); }

  async function save(e) {
    e.preventDefault();
    setError(""); setSavedMsg("");
    try {
      const { data } = await api.post("/institutions", form);
      setForm(data);
      setSavedMsg("Institution information saved.");
    } catch (err) { setError(err.message); }
  }

  return (
    <div className="card" style={{ maxWidth: 560 }}>
      <h2>Institution profile</h2>
      <p className="muted">Demo data — not a real institution.</p>
      {error && <div className="alert alert-error">{error}</div>}
      {savedMsg && <div className="alert alert-ok">{savedMsg}</div>}
      <form onSubmit={save}>
        <div className="grid grid-2">
          <div className="field"><label>Institution code</label>
            <input value={form.institution_code} onChange={(e) => set("institution_code", e.target.value)} required disabled={user.role !== "admin"} /></div>
          <div className="field"><label>Institution name</label>
            <input value={form.name} onChange={(e) => set("name", e.target.value)} required disabled={user.role !== "admin"} /></div>
        </div>
        <div className="field"><label>Address</label>
          <input value={form.address || ""} onChange={(e) => set("address", e.target.value)} disabled={user.role !== "admin"} /></div>
        <div className="grid grid-2">
          <div className="field"><label>University</label>
            <input value={form.university || ""} onChange={(e) => set("university", e.target.value)} disabled={user.role !== "admin"} /></div>
          <div className="field"><label>Department</label>
            <input value={form.department || ""} onChange={(e) => set("department", e.target.value)} disabled={user.role !== "admin"} /></div>
        </div>
        <div className="field"><label>Academic year</label>
          <input value={form.academic_year || ""} onChange={(e) => set("academic_year", e.target.value)} disabled={user.role !== "admin"} /></div>
        {user.role === "admin" && <button className="btn">Save institution</button>}
      </form>
    </div>
  );
}
