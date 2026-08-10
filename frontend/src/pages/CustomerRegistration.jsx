import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { customerService } from "../services";
import API_URL from "../config";
import "./CustomerRegistration.css";

const emptyForm = {
  nome: "",
  telefone: "",
  email: "",
  data_nascimento: "",
};

function getApiMessage(error, fallback) {
  if (!error?.response) {
    return `${fallback} O celular nao conseguiu conectar na API (${API_URL}). Confira se esta no mesmo Wi-Fi do computador e se o backend esta aberto.`;
  }

  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).filter(Boolean).join(", ") || fallback;
  }
  return detail || fallback;
}

export default function CustomerRegistration() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!token) {
      setMessage("Este link de cadastro e invalido.");
      return;
    }

    setLoading(true);
    try {
      await customerService.publicRegistration({
        nome: form.nome.trim(),
        telefone: form.telefone.trim() || null,
        email: form.email.trim() || null,
        data_nascimento: form.data_nascimento || null,
        token,
      });
      setMessage("Cadastro concluido! Agora voce ja faz parte do programa de fidelidade.");
      setForm(emptyForm);
    } catch (error) {
      setMessage(getApiMessage(error, "Nao foi possivel concluir o cadastro."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="customer-registration-page">
      <section className="customer-registration-card">
        <div className="customer-registration-brand">Fidelidade Total</div>
        <h1>Cadastre-se no programa</h1>
        <p>Preencha seus dados para comecar a aproveitar os beneficios.</p>

        {message && <div className="customer-registration-message">{message}</div>}

        <form onSubmit={handleSubmit}>
          <label>
            Nome completo
            <input
              required
              value={form.nome}
              onChange={(event) => setForm({ ...form, nome: event.target.value })}
            />
          </label>

          <label>
            Telefone
            <input
              type="tel"
              inputMode="tel"
              value={form.telefone}
              onChange={(event) => setForm({ ...form, telefone: event.target.value })}
            />
          </label>

          <label>
            E-mail
            <input
              type="email"
              inputMode="email"
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
            />
          </label>

          <label>
            Data de nascimento
            <input
              type="date"
              value={form.data_nascimento}
              onChange={(event) =>
                setForm({ ...form, data_nascimento: event.target.value })
              }
            />
          </label>

          <button type="submit" disabled={loading || !token}>
            {loading ? "Enviando..." : "Concluir cadastro"}
          </button>
        </form>
      </section>
    </main>
  );
}
