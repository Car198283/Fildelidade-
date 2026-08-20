import {
  BrowserRouter as Router,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
import { useState } from "react";

import Register from "./pages/Register";
import CustomerRegistration from "./pages/CustomerRegistration";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Customers from "./pages/Customers";
import CustomerDetails from "./pages/CustomerDetails";
import Products from "./pages/Products";
import MobileCapture from "./pages/MobileCapture";
import PromotionConfig from "./pages/PromotionConfig";
import UserManagement from "./pages/UserManagement";
import CompanyManagement from "./pages/CompanyManagement";
import ChangePassword from "./pages/ChangePassword";
import WhatsAppIntegration from "./pages/WhatsAppIntegration";
import MasterReports from "./pages/MasterReports";

import "./App.css";

function getStoredUser() {
  const rawUser = sessionStorage.getItem("user");
  if (!rawUser) return {};

  try {
    return JSON.parse(rawUser);
  } catch {
    sessionStorage.removeItem("user");
    return {};
  }
}

function PrivateRoute({ children, roles = [] }) {
  const token = sessionStorage.getItem("accessToken");
  const location = useLocation();
  const user = getStoredUser();
  const mobileCaptureOnly = sessionStorage.getItem("mobileCaptureOnly") === "1";

  if (!token) {
    return (
      <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} />
    );
  }

  if (user.exigir_troca_senha && location.pathname !== "/trocar-senha") {
    return <Navigate to="/trocar-senha" />;
  }

  if (mobileCaptureOnly && location.pathname !== "/captura") {
    return <Navigate to="/captura" />;
  }

  if (roles.length && !roles.includes(user.role)) {
    const canUseDashboard = user.role === "admin" || user.role === "master";
    return <Navigate to={canUseDashboard ? "/dashboard" : "/captura"} />;
  }

  return children;
}

function ProtectedLayout({ children }) {
  const [showMenu, setShowMenu] = useState(false);
  const user = getStoredUser();
  const canManage = user.role === "admin" || user.role === "master";
  const isMaster = user.role === "master";

  const handleLogout = () => {
    sessionStorage.removeItem("accessToken");
    sessionStorage.removeItem("user");
    sessionStorage.removeItem("selectedCompanyId");
    sessionStorage.removeItem("mobileCaptureOnly");
    window.location.href = "/login";
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-content">
          <div className="navbar-brand">
            <h1>Fidelidade Total</h1>
          </div>

          <button
            className="menu-toggle"
            onClick={() => setShowMenu(!showMenu)}
            type="button"
          >
            Menu
          </button>

          <div className={`nav-links ${showMenu ? "open" : ""}`}>
            <a href="/dashboard">Dashboard</a>
            {canManage && <a href="/customers">Clientes</a>}
            {canManage && <a href="/products">Produtos</a>}
            {canManage && <a href="/promotion-config">Promocao</a>}
            {canManage && <a href="/usuarios">Usuarios</a>}
            {canManage && <a href="/integracoes">WhatsApp</a>}
            {isMaster && <a href="/empresas">Empresas</a>}
            {isMaster && <a href="/relatorios-master">Relatorios</a>}
            <a href="/captura" className="capture-link">
              Captura
            </a>
            <span className="user-email">{user.email}</span>
            <button onClick={handleLogout} className="logout-btn" type="button">
              Sair
            </button>
          </div>
        </div>
      </nav>

      <main className="main-content">{children}</main>
    </div>
  );
}

function MobileCaptureEntry() {
  sessionStorage.setItem("mobileCaptureOnly", "1");
  return <Navigate to="/captura" replace />;
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/cadastro-cliente" element={<CustomerRegistration />} />
        <Route path="/login" element={<Login />} />
        <Route path="/trocar-senha" element={<PrivateRoute><ChangePassword /></PrivateRoute>} />

        <Route
          path="/dashboard"
          element={
            <PrivateRoute roles={["admin", "master"]}>
              <ProtectedLayout>
                <Dashboard />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/customers"
          element={
            <PrivateRoute roles={["admin", "master"]}>
              <ProtectedLayout>
                <Customers />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/customer/:id"
          element={
            <PrivateRoute roles={["admin", "master"]}>
              <ProtectedLayout>
                <CustomerDetails />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/products"
          element={
            <PrivateRoute roles={["admin", "master"]}>
              <ProtectedLayout>
                <Products />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/captura"
          element={
            <PrivateRoute>
              <MobileCapture />
            </PrivateRoute>
          }
        />

        <Route
          path="/promotion-config"
          element={
            <PrivateRoute roles={["admin", "master"]}>
              <ProtectedLayout>
                <PromotionConfig />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/usuarios"
          element={
            <PrivateRoute roles={["admin", "master"]}>
              <ProtectedLayout>
                <UserManagement />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/integracoes"
          element={
            <PrivateRoute roles={["admin", "master"]}>
              <ProtectedLayout><WhatsAppIntegration /></ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/empresas"
          element={
            <PrivateRoute roles={["master"]}>
              <ProtectedLayout>
                <CompanyManagement />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/relatorios-master"
          element={
            <PrivateRoute roles={["master"]}>
              <ProtectedLayout><MasterReports /></ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route path="/capture" element={<Navigate to="/captura" />} />
        <Route path="/celular" element={<MobileCaptureEntry />} />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}
