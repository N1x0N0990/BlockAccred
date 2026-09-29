import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import EvidenceTable from "../components/EvidenceTable";
import { useAuth } from "../context/AuthContext";

export default function Evidence() {
  const { user } = useAuth();
  const [rows, setRows] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => { api.get("/evidence").then((r) => setRows(r.data)); }, []);

  const filtered = filter === "all" ? rows : rows.filter((r) => r.status === filter);

  return (
    <div>
      <div className="flex-between" style={{ marginBottom: 14 }}>
        <div className="tag-row">
          {["all", "Pending Review", "Verified", "Requires Revision", "Flagged"].map((f) => (
            <button key={f} className={`btn btn-sm ${filter === f ? "" : "btn-outline"}`} onClick={() => setFilter(f)}>{f === "all" ? "All" : f}</button>
          ))}
        </div>
        {user.role === "admin" && <Link to="/evidence/upload" className="btn btn-sm">+ Submit evidence</Link>}
      </div>
      <div className="card">
        <EvidenceTable rows={filtered} />
      </div>
    </div>
  );
}
