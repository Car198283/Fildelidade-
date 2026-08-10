import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useState } from "react";

// Pages
import Register from "./pages/Register";
import CustomerRegistration from "./pages/CustomerRegistration";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Customers from "./pages/Customers";
import CustomerDetails from "./pages/CustomerDetails";
import Products from "./pages/Products";
import MobileCapture from "./pages/MobileCapture";
import PromotionConfig from "./pages/PromotionConfig";

import "./App.css";

function getStoredUser() {
  const rawUser = localStorage.getItem("user");
  if (!rawUser) return {};

  try {
    return JSON.parse(rawUser);
  } catch {
    localStorage.removeItem("user");
    return {};
  }
}

function PrivateRoute({ children }) {
  const token = localStorage.getItem("accessToken");
  return token ? children : <Navigate to="/login" />;
}

function ProtectedLayout({ children }) {
  const [showMenu, setShowMenu] = useState(false);
  const user = getStoredUser();

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("user");
    window.location.href = "/login";
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-content">
          <div className="navbar-brand">
            <h1>🎯 Fidelidade Total</h1>
          </div>

          <button
            className="menu-toggle"
            onClick={() => setShowMenu(!showMenu)}
          >
            ☰
          </button>

          <div className={`nav-links ${showMenu ? "open" : ""}`}>
            <a href="/dashboard">📊 Dashboard</a>
            <a href="/customers">👥 Clientes</a>
            <a href="/products">📦 Produtos</a>
            <a href="/promotion-config">⚙️ Promoção</a>
            <a href="/capture" className="capture-link">
              📱 Captura
            </a>
            <span className="user-email">{user.email}</span>
            <button onClick={handleLogout} className="logout-btn">
              🚪 Sair
            </button>
          </div>
        </div>
      </nav>

      <main className="main-content">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/cadastro-cliente" element={<CustomerRegistration />} />
        <Route path="/login" element={<Login />} />

        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <Dashboard />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/customers"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <Customers />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/customer/:id"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <CustomerDetails />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/products"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <Products />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/capture"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <MobileCapture />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/promotion-config"
          element={
            <PrivateRoute>
              <ProtectedLayout>
                <PromotionConfig />
              </ProtectedLayout>
            </PrivateRoute>
          }
        />

        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </Router>
  );
}
