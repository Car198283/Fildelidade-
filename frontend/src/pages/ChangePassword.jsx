import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "../services";
import "./Auth.css";

export default function ChangePassword() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ current: "", next: "", confirm: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    if (form.next !== form.confirm) return setError("A confirmacao nao corresponde a nova senha.");
    try {
      setLoading(true); setError("");
      await authService.changePassword(form.current, form.next);
      const user = JSON.parse(sessionStorage.getItem("user") || "{}");
      user.exigir_troca_senha = false;
      sessionStorage.setItem("user", JSON.stringify(user));
      navigate(user.role === "admin" || user.role === "master" ? "/dashboard" : "/captura");
    } catch (err) { setError(err.response?.data?.detail || "Nao foi possivel alterar a senha."); }
    finally { setLoading(false); }
  };

  return <div className="auth-container"><div className="auth-box"><h1>Fidelidade Total</h1><h2>Crie uma nova senha</h2><p>Por seguranca, altere a senha temporaria antes de continuar.</p>{error && <div className="error-message">{error}</div>}<form onSubmit={submit} autoComplete="off"><input type="password" placeholder="Senha atual" autoComplete="current-password" value={form.current} onChange={(e) => setForm({ ...form, current: e.target.value })} required/><input type="password" placeholder="Nova senha (minimo 8 caracteres)" autoComplete="new-password" minLength="8" value={form.next} onChange={(e) => setForm({ ...form, next: e.target.value })} required/><input type="password" placeholder="Confirme a nova senha" autoComplete="new-password" minLength="8" value={form.confirm} onChange={(e) => setForm({ ...form, confirm: e.target.value })} required/><button disabled={loading}>{loading ? "Alterando..." : "Alterar senha"}</button></form></div></div>;
}
