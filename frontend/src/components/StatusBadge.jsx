const MAP = {
  "Verified": "badge-verified",
  "Pending Review": "badge-pending",
  "Requires Revision": "badge-revision",
  "Flagged": "badge-flagged",
  "Integrity Verified": "badge-verified",
  "Hash Mismatch": "badge-mismatch",
  "Not Recorded": "badge-pending",
  "Recorded": "badge-onchain",
};

export default function StatusBadge({ status }) {
  const cls = MAP[status] || "badge-pending";
  return <span className={`badge ${cls}`}>{status}</span>;
}
