import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function fill(e, p) { setEmail(e); setPassword(p); }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="login-brand">
          <div className="brand-mark"><span className="brand-chip" />BlockAccred</div>
          <p className="brand-sub" style={{ marginTop: 6 }}>Blockchain-Based Transparent and Tamper-Evident<br />Accreditation Evidence Verification System</p>
        </div>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={submit}>
          <div className="field">
            <label>Email</label>
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required placeholder="you@college.com" />
          </div>
          <div className="field">
            <label>Password</label>
            <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" required placeholder="••••••••" />
          </div>
          <button className="btn" style={{ width: "100%", justifyContent: "center" }} disabled={loading}>
            {loading ? "Signing in…" : "Log in"}
          </button>
        </form>
        <div className="demo-box">
          <div className="demo-title">Demo credentials</div>
          <div>These are fictional accounts created only for demonstration.</div>
          <div style={{ marginTop: 8 }}>
            <a href="#" onClick={(ev) => { ev.preventDefault(); fill("admin@college.com", "admin123"); }}>College Admin</a> — admin@college.com / admin123
          </div>
          <div>
            <a href="#" onClick={(ev) => { ev.preventDefault(); fill("reviewer@nba-demo.com", "reviewer123"); }}>Reviewer</a> — reviewer@nba-demo.com / reviewer123
          </div>
          <div>
            <a href="#" onClick={(ev) => { ev.preventDefault(); fill("student@college.com", "student123"); }}>Student</a> — student@college.com / student123
          </div>
        </div>
      </div>
    </div>
  );
}
