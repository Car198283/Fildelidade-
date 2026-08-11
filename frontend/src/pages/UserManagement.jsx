import { useEffect, useState } from "react";
import { adminService } from "../services";
import "./UserManagement.css";

const emptyForm = {
  email: "",
  senha: "",
  role: "observador",
};

function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem("user") || "{}");
  } catch {
    return {};
  }
}

export default function UserManagement() {
  const currentUser = getStoredUser();
  const [users, setUsers] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState(
    localStorage.getItem("selectedCompanyId") || "",
  );
  const [form, setForm] = useState(emptyForm);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const isMaster = currentUser.role === "master";

  const loadUsers = async () => {
    const response = await adminService.users(isMaster ? selectedCompanyId || null : null);
    setUsers(response.data?.data || []);
  };

  const loadCompanies = async () => {
    if (!isMaster) return;
    const response = await adminService.companies();
    const data = response.data?.data || [];
    setCompanies(data);
    if (!selectedCompanyId && data.length) {
      const firstCompanyId = String(data[0].id);
      setSelectedCompanyId(firstCompanyId);
      localStorage.setItem("selectedCompanyId", firstCompanyId);
    }
  };

  useEffect(() => {
    loadCompanies().catch(() => setMessage("Nao foi possivel carregar empresas."));
  }, []);

  useEffect(() => {
    loadUsers().catch(() => setMessage("Nao foi possivel carregar usuarios."));
  }, [selectedCompanyId]);

  const handleCompanyChange = (event) => {
    const value = event.target.value;
    setSelectedCompanyId(value);
    if (value) localStorage.setItem("selectedCompanyId", value);
    else localStorage.removeItem("selectedCompanyId");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");

    try {
      await adminService.createUser({
        email: form.email,
        senha: form.senha,
        role: form.role,
        company_id: isMaster ? Number(selectedCompanyId) : null,
      });
      setForm(emptyForm);
      setMessage("Usuario criado com sucesso.");
      await loadUsers();
    } catch (error) {
      setMessage(error.response?.data?.detail || "Nao foi possivel criar usuario.");
    } finally {
      setLoading(false);
    }
  };

  const toggleUser = async (user) => {
    await adminService.updateUser(user.id, { ativo: !user.ativo });
    await loadUsers();
  };

  return (
    <div className="users-page">
      <div className="users-header">
        <h1>Usuarios e Acessos</h1>
        <p>Controle de administradores e observadores por empresa.</p>
      </div>

      {message && <div className="users-message">{message}</div>}

      {isMaster && (
        <section className="users-panel">
          <label>Empresa em gestao</label>
          <select value={selectedCompanyId} onChange={handleCompanyChange}>
            {companies.map((company) => (
              <option key={company.id} value={company.id}>
                {company.nome}
              </option>
            ))}
          </select>
        </section>
      )}

      <section className="users-panel">
        <h2>Novo usuario</h2>
        <form className="users-form" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
            required
          />
          <input
            type="password"
            placeholder="Senha temporaria"
            value={form.senha}
            onChange={(event) => setForm({ ...form, senha: event.target.value })}
            required
          />
          <select
            value={form.role}
            onChange={(event) => setForm({ ...form, role: event.target.value })}
          >
            <option value="observador">Observador</option>
            <option value="admin">Administrador</option>
          </select>
          <button type="submit" disabled={loading || (isMaster && !selectedCompanyId)}>
            {loading ? "Criando..." : "Criar usuario"}
          </button>
        </form>
      </section>

      <section className="users-panel">
        <h2>Usuarios cadastrados</h2>
        <div className="users-list">
          {users.map((user) => (
            <article className="user-row" key={user.id}>
              <div>
                <strong>{user.email}</strong>
                <span>{user.role}</span>
              </div>
              <button type="button" onClick={() => toggleUser(user)}>
                {user.ativo ? "Desativar" : "Ativar"}
              </button>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
