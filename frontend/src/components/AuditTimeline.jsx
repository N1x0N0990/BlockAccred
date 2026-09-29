export default function AuditTimeline({ items }) {
  if (!items || items.length === 0) return <div className="empty">No audit activity yet.</div>;
  return (
    <div className="timeline">
      {items.map((a) => (
        <div className="timeline-item" key={a.id}>
          <div className="timeline-time">{new Date(a.created_at).toLocaleString()}</div>
          <div className="timeline-action">{a.action}{a.entity ? ` — ${a.entity}` : ""}</div>
          {a.details && <div className="timeline-details">{a.details}</div>}
          <div className="timeline-details">by {a.actor}</div>
        </div>
      ))}
    </div>
  );
}
