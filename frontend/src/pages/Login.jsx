import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { authService } from "../services";
import "./Auth.css";

export default function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
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
      const response = await authService.login(form.email, form.password);

      // Salva token e usuário
      localStorage.setItem("accessToken", response.data.data.access_token);
      localStorage.setItem("user", JSON.stringify(response.data.data));

      const nextPath = searchParams.get("next");
      if (nextPath === "/celular" || nextPath === "/captura") {
        localStorage.setItem("mobileCaptureOnly", "1");
      }

      if (nextPath?.startsWith("/")) {
        navigate(nextPath === "/celular" ? "/captura" : nextPath);
      } else {
        navigate(response.data.data.role === "observador" ? "/captura" : "/dashboard");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Email ou senha incorretos");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1>🎯 Fidelidade Total</h1>
        <h2>Fazer Login</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            required
          />

          <input
            type="password"
            name="password"
            placeholder="Senha"
            value={form.password}
            onChange={handleChange}
            required
          />

          <button type="submit" disabled={loading}>
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        <p>
          Não tem conta? <a href="/register">Registre-se</a>
        </p>
      </div>
    </div>
  );
}
