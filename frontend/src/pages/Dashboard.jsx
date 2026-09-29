import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "../services/api";
import StatCard from "../components/StatCard";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/dashboard").then((r) => setData(r.data)).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="alert alert-error">{error}</div>;
  if (!data) return <div className="empty">Loading…</div>;

  const chartData = data.prototype_score.breakdown.map((b) => ({ name: b.parameter.split("/")[0], score: b.score }));

  return (
    <div>
      <div className="card" style={{ marginBottom: 18 }}>
        <h2 style={{ marginBottom: 2 }}>{data.institution}</h2>
        <p className="muted" style={{ margin: 0 }}>{data.programme}</p>
      </div>

      <div className="grid grid-4">
        <StatCard label="Evidence submitted" value={data.evidence.submitted} />
        <StatCard label="Verified" value={data.evidence.verified} tone="chain" />
        <StatCard label="Pending" value={data.evidence.pending} />
        <StatCard label="Flagged / revision" value={data.evidence.flagged} tone="amber" />
      </div>

      <div className="grid grid-4 section-gap">
        <StatCard label="Blockchain records" value={data.blockchain_records} tone="chain" />
        <StatCard label="Integrity checks passed" value={data.integrity_verified} tone="chain" />
        <StatCard label="Anomalies flagged" value={data.anomalies} tone="amber" />
        <StatCard label="Prototype Assessment Score" value={`${data.prototype_score.overall}/100`} />
      </div>

      <div className="card section-gap">
        <div className="flex-between" style={{ marginBottom: 14 }}>
          <h3>Prototype Assessment Score — parameter breakdown</h3>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ECE9E1" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="score" fill="#0F8B8D" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <p className="muted" style={{ marginTop: 10, fontSize: 12 }}>
          Prototype Assessment Parameters inspired by accreditation evidence requirements. These are not official NBA criteria or NBA scoring rules.
        </p>
      </div>
    </div>
  );
}
