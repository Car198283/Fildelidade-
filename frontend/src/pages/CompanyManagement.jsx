import { useEffect, useState } from "react";
import { adminService, authService } from "../services";
import "./CompanyManagement.css";

const emptyForm = {
  companyName: "",
  email: "",
  password: "",
};

export default function CompanyManagement() {
  const [companies, setCompanies] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const loadCompanies = async () => {
    const response = await adminService.companies();
    setCompanies(response.data?.data || []);
  };

  useEffect(() => {
    loadCompanies().catch(() =>
      setMessage("Nao foi possivel carregar empresas."),
    );
  }, []);

  const handleCreateCompany = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      await authService.register(form.companyName, form.email, form.password);
      setForm(emptyForm);
      setMessage("Empresa criada com sucesso.");
      await loadCompanies();
    } catch (error) {
      setMessage(
        error.response?.data?.detail || "Nao foi possivel criar a empresa.",
      );
    } finally {
      setLoading(false);
    }
  };

  const updateCompanyStatus = async (company, data) => {
    setMessage("");
    try {
      await adminService.updateCompany(company.id, data);
      await loadCompanies();
      setMessage("Status da empresa atualizado.");
    } catch (error) {
      setMessage(
        error.response?.data?.detail || "Nao foi possivel atualizar a empresa.",
      );
    }
  };

  return (
    <div className="companies-page">
      <div className="companies-header">
        <h1>Empresas cadastradas</h1>
        <p>Controle completo do cadastro e status das empresas no sistema.</p>
      </div>

      {message && <div className="companies-message">{message}</div>}

      <section className="companies-panel">
        <h2>Nova empresa</h2>
        <form className="company-form" onSubmit={handleCreateCompany}>
          <input
            type="text"
            placeholder="Nome da empresa"
            value={form.companyName}
            onChange={(event) =>
              setForm({ ...form, companyName: event.target.value })
            }
            required
          />
          <input
            type="email"
            placeholder="Email do administrador"
            value={form.email}
            onChange={(event) =>
              setForm({ ...form, email: event.target.value })
            }
            required
          />
          <input
            type="password"
            placeholder="Senha temporaria"
            value={form.password}
            onChange={(event) =>
              setForm({ ...form, password: event.target.value })
            }
            minLength={6}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Criando..." : "Criar empresa"}
          </button>
        </form>
      </section>

      <section className="companies-panel">
        <h2>Empresas cadastradas</h2>
        <div className="companies-list">
          {!companies.length ? (
            <div className="company-empty">Nenhuma empresa cadastrada.</div>
          ) : (
            companies.map((company) => (
              <article className="company-row" key={company.id}>
                <div className="company-main">
                  <strong>{company.nome}</strong>
                  <span>{company.plano || "free"}</span>
                </div>

                <div className="company-meta">
                  <span
                    className={
                      company.ativo ? "status-active" : "status-blocked"
                    }
                  >
                    {company.ativo ? "Ativa" : "Bloqueada"}
                  </span>
                  <span
                    className={
                      company.read_only ? "status-readonly" : "status-active"
                    }
                  >
                    {company.read_only
                      ? "Somente leitura"
                      : "Liberada para edicao"}
                  </span>
                </div>

                <div className="company-row-actions">
                  <button
                    type="button"
                    className={company.ativo ? "danger" : "success"}
                    onClick={() =>
                      updateCompanyStatus(company, { ativo: !company.ativo })
                    }
                  >
                    {company.ativo ? "Bloquear" : "Desbloquear"}
                  </button>
                  <button
                    type="button"
                    disabled={!company.ativo}
                    onClick={() =>
                      updateCompanyStatus(company, {
                        read_only: !company.read_only,
                      })
                    }
                  >
                    {company.read_only ? "Liberar edicao" : "Somente leitura"}
                  </button>
                </div>
              </article>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
