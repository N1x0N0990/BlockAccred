import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import AppLayout from "./layouts/AppLayout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Institution from "./pages/Institution";
import Programme from "./pages/Programme";
import Criteria from "./pages/Criteria";
import Evidence from "./pages/Evidence";
import EvidenceUpload from "./pages/EvidenceUpload";
import EvidenceDetail from "./pages/EvidenceDetail";
import Verification from "./pages/Verification";
import Reviewer from "./pages/Reviewer";
import Blockchain from "./pages/Blockchain";
import AuditTrail from "./pages/AuditTrail";
import Anomalies from "./pages/Anomalies";
import StudentFeedback from "./pages/StudentFeedback";

function Protected({ roles }) {
  const { user, ready } = useAuth();
  if (!ready) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/dashboard" replace />;
  return <AppLayout />;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<Protected />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/criteria" element={<Criteria />} />
          <Route path="/evidence" element={<Evidence />} />
          <Route path="/evidence/:id" element={<EvidenceDetail />} />
          <Route path="/evidence/:code" element={<EvidenceDetail />} />
          <Route path="/verification" element={<Verification />} />
          <Route path="/blockchain" element={<Blockchain />} />
          <Route path="/audit-trail" element={<AuditTrail />} />
          <Route path="/anomalies" element={<Anomalies />} />
          <Route path="/student-feedback" element={<StudentFeedback />} />
        </Route>
        <Route element={<Protected roles={["admin"]} />}>
          <Route path="/institution" element={<Institution />} />
          <Route path="/programme" element={<Programme />} />
          <Route path="/evidence/upload" element={<EvidenceUpload />} />
        </Route>
        <Route element={<Protected roles={["reviewer"]} />}>
          <Route path="/reviewer" element={<Reviewer />} />
        </Route>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
