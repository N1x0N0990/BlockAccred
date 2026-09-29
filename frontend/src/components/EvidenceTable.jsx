import { useNavigate } from "react-router-dom";
import StatusBadge from "./StatusBadge";
import HashText from "./HashText";

export default function EvidenceTable({ rows }) {
  const navigate = useNavigate();
  if (!rows || rows.length === 0) return <div className="empty">No evidence submitted yet.</div>;
  return (
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Parameter</th><th>Claimed value</th><th>Document hash</th><th>Chain</th><th>Status</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((e) => (
          <tr key={e.id} className="clickable" onClick={() => navigate(`/evidence/${e.code}`)}>
            <td className="mono">{e.code}</td>
            <td>{e.parameter}</td>
            <td>{e.claimed_value}%</td>
            <td><HashText hash={e.document_hash} /></td>
            <td>{e.blockchain_recorded ? <span className="badge badge-onchain">Recorded</span> : <span className="badge badge-pending">Not recorded</span>}</td>
            <td><StatusBadge status={e.status} /></td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
