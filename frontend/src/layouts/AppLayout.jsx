import { NavLink, Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV = [
  { group: "Overview", links: [{ to: "/dashboard", label: "Dashboard" }] },
  {
    group: "Institution", roles: ["admin", "reviewer"],
    links: [
      { to: "/institution", label: "Institution", roles: ["admin"] },
      { to: "/programme", label: "Programmes", roles: ["admin"] },
      { to: "/criteria", label: "Prototype Parameters" },
    ],
  },
  {
    group: "Evidence",
    links: [
      { to: "/evidence", label: "Evidence" },
      { to: "/evidence/upload", label: "Submit Evidence", roles: ["admin"] },
      { to: "/verification", label: "Integrity Check" },
      { to: "/reviewer", label: "Reviewer Queue", roles: ["reviewer"] },
      { to: "/blockchain", label: "Blockchain" },
    ],
  },
  {
    group: "Oversight",
    links: [
      { to: "/anomalies", label: "Anomalies" },
      { to: "/audit-trail", label: "Audit Trail" },
      { to: "/student-feedback", label: "Student Feedback" },
    ],
  },
];

const TITLES = {
  "/dashboard": "Dashboard", "/institution": "Institution", "/programme": "Programmes",
  "/criteria": "Prototype Assessment Parameters", "/evidence": "Evidence", "/evidence/upload": "Submit Evidence",
  "/verification": "Integrity Check", "/reviewer": "Reviewer Queue", "/blockchain": "Blockchain",
  "/anomalies": "Anomaly Detection", "/audit-trail": "Audit Trail", "/student-feedback": "Student Feedback",
};

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  function visible(link) {
    return !link.roles || link.roles.includes(user.role);
  }

  const title = Object.entries(TITLES).find(([p]) => location.pathname.startsWith(p) && p !== "/evidence" || location.pathname === p)?.[1]
    || (location.pathname.startsWith("/evidence/") ? "Evidence Detail" : "BlockAccred");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><span className="brand-chip" />BlockAccred</div>
          <div className="brand-sub">Academic Prototype — Not an Official NBA System</div>
        </div>
        {NAV.map((g) => {
          const links = g.links.filter(visible);
          if (links.length === 0) return null;
          return (
            <div className="nav-group" key={g.group}>
              <div className="nav-label">{g.group}</div>
              {links.map((l) => (
                <NavLink key={l.to} to={l.to} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}>
                  {l.label}
                </NavLink>
              ))}
            </div>
          );
        })}
        <div className="sidebar-footer">
          <div className="user-chip">{user.name}</div>
          <div className="user-role">{user.role}</div>
          <button className="logout-btn" onClick={() => { logout(); navigate("/login"); }}>Log out</button>
        </div>
      </aside>
      <div className="main">
        <div className="topbar">
          <div className="topbar-title">{title}</div>
          <div className="proto-flag">Academic Prototype — Not an Official NBA System</div>
        </div>
        <div className="content">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
