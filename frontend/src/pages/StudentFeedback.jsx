import { useEffect, useState } from "react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

const QUESTIONS = [
  { key: "teaching_quality", label: "Teaching quality" },
  { key: "infrastructure", label: "Infrastructure" },
  { key: "faculty_support", label: "Faculty support" },
  { key: "overall_satisfaction", label: "Overall satisfaction" },
];

export default function StudentFeedback() {
  const { user } = useAuth();
  const [form, setForm] = useState({ teaching_quality: 3, infrastructure: 3, faculty_support: 3, overall_satisfaction: 3, comment: "" });
  const [msg, setMsg] = useState(""); const [error, setError] = useState("");
  const [rows, setRows] = useState([]);
  const [summary, setSummary] = useState(null);

  function load() {
    api.get("/feedback").then((r) => setRows(r.data));
    api.get("/feedback/summary").then((r) => setSummary(r.data));
  }
  useEffect(load, []);

  async function submit(e) {
    e.preventDefault();
    setError(""); setMsg("");
    try { await api.post("/feedback", form); setMsg("Thank you — your feedback was submitted."); load(); }
    catch (err) { setError(err.message); }
  }

  return (
    <div>
      {user.role === "student" && (
        <div className="card" style={{ maxWidth: 480 }}>
          <h2>Submit feedback</h2>
          {error && <div className="alert alert-error">{error}</div>}
          {msg && <div className="alert alert-ok">{msg}</div>}
          <form onSubmit={submit}>
            {QUESTIONS.map((q) => (
              <div className="field" key={q.key}>
                <label>{q.label}: {form[q.key]} / 5</label>
                <input type="range" min={1} max={5} value={form[q.key]} onChange={(e) => setForm((f) => ({ ...f, [q.key]: Number(e.target.value) }))} />
              </div>
            ))}
            <div className="field"><label>Comment (optional)</label>
              <textarea rows={2} value={form.comment} onChange={(e) => setForm((f) => ({ ...f, comment: e.target.value }))} /></div>
            <button className="btn">Submit feedback</button>
          </form>
        </div>
      )}

      <div className="card section-gap">
        <h3>Feedback summary</h3>
        {summary && <p className="muted">{summary.count} responses · average satisfaction {summary.average_percent ?? "—"}%</p>}
        {rows.length === 0 ? <div className="empty">No feedback yet.</div> : (
          <table>
            <thead><tr><th>Student</th><th>Teaching</th><th>Infra</th><th>Faculty</th><th>Overall</th><th>Comment</th></tr></thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{r.student}</td><td>{r.teaching_quality}/5</td><td>{r.infrastructure}/5</td>
                  <td>{r.faculty_support}/5</td><td>{r.overall_satisfaction}/5</td><td className="muted">{r.comment}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
