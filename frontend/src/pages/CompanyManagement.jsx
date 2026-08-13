import { useEffect, useState } from "react";
import { adminService } from "../services";
import "./CompanyManagement.css";

const emptyForm = {
  razao_social: "",
  nome: "",
  cnpj: "",
  telefone: "",
  email: "",
  responsavel: "",
  cep: "",
  endereco: "",
  numero: "",
  bairro: "",
  cidade: "",
  estado: "",
  logotipo: "",
  admin_email: "",
  admin_senha: "",
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
      await adminService.createCompany({
        ...form,
        estado: form.estado.toUpperCase(),
      });
      setForm(emptyForm);
      setMessage("Empresa e administrador criados com sucesso.");
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
          <label>
            Razao social *
            <input
              type="text"
              placeholder="Barcellos Gelataria LTDA"
              value={form.razao_social}
              onChange={(event) =>
                setForm({ ...form, razao_social: event.target.value })
              }
              required
            />
          </label>

          <label>
            Nome fantasia *
            <input
              type="text"
              placeholder="Barcellos Gelataria"
              value={form.nome}
              onChange={(event) => setForm({ ...form, nome: event.target.value })}
              required
            />
          </label>

          <label>
            CNPJ *
            <input
              type="text"
              placeholder="12.345.678/0001-90"
              value={form.cnpj}
              onChange={(event) => setForm({ ...form, cnpj: event.target.value })}
              required
            />
          </label>

          <label>
            Telefone *
            <input
              type="tel"
              placeholder="(32) 99999-9999"
              value={form.telefone}
              onChange={(event) =>
                setForm({ ...form, telefone: event.target.value })
              }
              required
            />
          </label>

          <label>
            E-mail da empresa *
            <input
              type="email"
              placeholder="contato@barcellos.com.br"
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
              required
            />
          </label>

          <label>
            Responsavel *
            <input
              type="text"
              placeholder="Carlos Eduardo"
              value={form.responsavel}
              onChange={(event) =>
                setForm({ ...form, responsavel: event.target.value })
              }
              required
            />
          </label>

          <div className="form-section-title">Endereco</div>

          <label>
            CEP
            <input
              type="text"
              placeholder="36000-000"
              value={form.cep}
              onChange={(event) => setForm({ ...form, cep: event.target.value })}
            />
          </label>

          <label className="wide-field">
            Endereco
            <input
              type="text"
              placeholder="Rua Exemplo"
              value={form.endereco}
              onChange={(event) =>
                setForm({ ...form, endereco: event.target.value })
              }
            />
          </label>

          <label>
            Numero
            <input
              type="text"
              placeholder="100"
              value={form.numero}
              onChange={(event) =>
                setForm({ ...form, numero: event.target.value })
              }
            />
          </label>

          <label>
            Bairro
            <input
              type="text"
              placeholder="Centro"
              value={form.bairro}
              onChange={(event) =>
                setForm({ ...form, bairro: event.target.value })
              }
            />
          </label>

          <label>
            Cidade
            <input
              type="text"
              placeholder="Juiz de Fora"
              value={form.cidade}
              onChange={(event) =>
                setForm({ ...form, cidade: event.target.value })
              }
            />
          </label>

          <label>
            Estado
            <input
              type="text"
              placeholder="MG"
              maxLength={2}
              value={form.estado}
              onChange={(event) =>
                setForm({ ...form, estado: event.target.value.toUpperCase() })
              }
            />
          </label>

          <label className="wide-field">
            Logotipo
            <input
              type="text"
              placeholder="URL ou nome do arquivo"
              value={form.logotipo}
              onChange={(event) =>
                setForm({ ...form, logotipo: event.target.value })
              }
            />
          </label>

          <div className="form-section-title">Administrador inicial</div>

          <label>
            E-mail do usuario *
            <input
              type="email"
              placeholder="admin@barcellos.com.br"
              value={form.admin_email}
              onChange={(event) =>
                setForm({ ...form, admin_email: event.target.value })
              }
              required
            />
          </label>

          <label>
            Senha temporaria *
            <input
              type="password"
              placeholder="Minimo 6 caracteres"
              value={form.admin_senha}
              onChange={(event) =>
                setForm({ ...form, admin_senha: event.target.value })
              }
              minLength={6}
              required
            />
          </label>

          <div className="company-form-actions">
            <button type="submit" disabled={loading}>
              {loading ? "Criando..." : "Criar empresa"}
            </button>
          </div>
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
                  <span>{company.razao_social || "Razao social nao informada"}</span>
                  <span>{company.cnpj || "CNPJ nao informado"}</span>
                </div>

                <div className="company-contact">
                  <span>{company.responsavel || "Responsavel nao informado"}</span>
                  <span>{company.telefone || "Telefone nao informado"}</span>
                  <span>{company.email || "Email nao informado"}</span>
                  <span>
                    {[company.cidade, company.estado].filter(Boolean).join(" - ") ||
                      "Cidade nao informada"}
                  </span>
                </div>

                <div className="company-meta">
                  <span className="status-plan">{company.plano || "free"}</span>
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
