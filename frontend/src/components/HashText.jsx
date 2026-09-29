export default function HashText({ hash, length = 18 }) {
  if (!hash) return <span className="muted">—</span>;
  const short = hash.length > length ? `${hash.slice(0, length)}…` : hash;
  return <span className="mono" title={hash}>{short}</span>;
}
