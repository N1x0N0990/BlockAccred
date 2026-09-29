import { useEffect, useState } from "react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Criteria() {
  const { user } = useAuth();
  const [criteria, setCriteria] = useState([]);
  const [error, setError] = useState("");

  function load() { api.get("/criteria").then((r) => setCriteria(r.data)); }
  useEffect(load, []);

  async function updateWeight(c, weight) {
    setError("");
    try {
      await api.put(`/criteria/${c.id}`, { weight: Number(weight) });
      load();
    } catch (err) { setError(err.message); }
  }

  const totalWeight = criteria.reduce((s, c) => s + c.weight, 0);

  return (
    <div className="card">
      <h2>Prototype Assessment Parameters</h2>
      <p className="muted">Prototype Assessment Parameters inspired by accreditation evidence requirements. These are not official NBA criteria or NBA scoring rules.</p>
      {error && <div className="alert alert-error">{error}</div>}
      <table>
        <thead><tr><th>Parameter</th><th>Description</th><th style={{ width: 140 }}>Weight (%)</th></tr></thead>
        <tbody>
          {criteria.map((c) => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td className="muted">{c.description}</td>
              <td>
                {user.role === "admin" ? (
                  <input type="number" min="0" max="100" defaultValue={c.weight} style={{ width: 80, padding: "5px 7px" }}
                    onBlur={(e) => e.target.value !== String(c.weight) && updateWeight(c, e.target.value)} />
                ) : `${c.weight}%`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="muted section-gap" style={{ marginTop: 12 }}>Total weight: {totalWeight}% {totalWeight !== 100 && "(weights do not need to sum to exactly 100 in this prototype — the score is normalized)"}</p>
    </div>
  );
}
