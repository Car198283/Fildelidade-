import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../services";
import "./Auth.css";

export default function Register() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [form, setForm] = useState({
    companyName: "",
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await authService.register(
        form.companyName,
        form.email,
        form.password,
      );

      // Salva dados
      sessionStorage.setItem("user", JSON.stringify(response.data.data));

      // Vai para login
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Erro ao registrar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1>🎯 Fidelidade Total</h1>
        <h2>Registre sua Empresa</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <input
            type="text"
            name="companyName"
            placeholder="Nome da Empresa"
            value={form.companyName}
            onChange={handleChange}
            required
          />

          <input
            type="email"
            name="email"
            placeholder="Email do Admin"
            value={form.email}
            onChange={handleChange}
            required
          />

          <div className="password-field">
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              placeholder="Senha"
              value={form.password}
              onChange={handleChange}
              required
              minLength="6"
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              title={showPassword ? "Ocultar senha" : "Mostrar senha"}
            >
              {showPassword ? "Ocultar" : "Ver"}
            </button>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Registrando..." : "Registrar"}
          </button>
        </form>

        <p>
          Já tem conta? <a href="/login">Faça login</a>
        </p>
      </div>
    </div>
  );
}
