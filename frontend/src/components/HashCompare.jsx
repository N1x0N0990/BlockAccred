import HashText from "./HashText";

export default function HashCompare({ result }) {
  if (!result) return null;
  const match = result.match;
  return (
    <div>
      <div className="hash-compare">
        <div>
          <div className="hash-col-label">Blockchain-recorded hash</div>
          <div className="hash-box"><HashText hash={result.chain_hash} length={64} /></div>
        </div>
        <div>
          <div className="hash-col-label">Current document hash</div>
          <div className="hash-box"><HashText hash={result.current_hash} length={64} /></div>
        </div>
      </div>
      <div className={`hash-verdict ${match ? "match" : "mismatch"}`}>
        <div className="hash-verdict-title">{match ? "✓ Integrity Verified" : "✗ Hash Mismatch — Document Modified"}</div>
        <div className="muted" style={{ fontSize: 13 }}>{result.message}</div>
      </div>
    </div>
  );
}
