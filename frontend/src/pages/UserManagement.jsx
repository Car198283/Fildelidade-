import { useEffect, useState } from "react";
import { adminService } from "../services";
import "./UserManagement.css";

const emptyForm = {
  email: "",
  senha: "",
  role: "operador_captura",
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
  const [editingUserId, setEditingUserId] = useState(null);
  const [showPassword, setShowPassword] = useState(false);

  const isMaster = currentUser.role === "master";
  const selectedCompany = companies.find(
    (company) => String(company.id) === String(selectedCompanyId),
  );

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
      if (editingUserId) {
        const payload = {
          role: form.role,
          ativo: form.ativo,
        };
        if (form.senha) payload.senha = form.senha;
        await adminService.updateUser(editingUserId, payload);
        setEditingUserId(null);
        setMessage("Usuario atualizado com sucesso.");
      } else {
        await adminService.createUser({
          email: form.email,
          senha: form.senha,
          role: form.role,
          company_id: isMaster ? Number(selectedCompanyId) : null,
        });
        setMessage("Usuario criado com sucesso.");
      }
      setForm(emptyForm);
      setShowPassword(false);
      await loadUsers();
    } catch (error) {
      setMessage(error.response?.data?.detail || "Nao foi possivel salvar usuario.");
    } finally {
      setLoading(false);
    }
  };

  const startEditUser = (user) => {
    setEditingUserId(user.id);
    setForm({
      email: user.email,
      senha: "",
      role: user.role,
      ativo: user.ativo,
    });
    setShowPassword(false);
    setMessage("");
  };

  const cancelEditUser = () => {
    setEditingUserId(null);
    setForm(emptyForm);
    setShowPassword(false);
    setMessage("");
  };

  const toggleUser = async (user) => {
    await adminService.updateUser(user.id, { ativo: !user.ativo });
    await loadUsers();
  };

  const deleteUser = async (user) => {
    const confirmed = window.confirm(`Excluir o usuario ${user.email}?`);
    if (!confirmed) return;

    setMessage("");
    try {
      await adminService.deleteUser(user.id);
      if (editingUserId === user.id) cancelEditUser();
      await loadUsers();
      setMessage("Usuario excluido com sucesso.");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Nao foi possivel excluir usuario.");
    }
  };

  const updateCompanyStatus = async (data) => {
    if (!selectedCompanyId) return;
    setMessage("");
    try {
      await adminService.updateCompany(selectedCompanyId, data);
      await loadCompanies();
      setMessage("Status da empresa atualizado.");
    } catch (error) {
      setMessage(error.response?.data?.detail || "Nao foi possivel atualizar a empresa.");
    }
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
          <div className="company-control">
            <div>
              <label>Empresa em gestao</label>
              <select value={selectedCompanyId} onChange={handleCompanyChange}>
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.nome}
                  </option>
                ))}
              </select>
            </div>

            {selectedCompany && (
              <div className="company-status">
                <span className={selectedCompany.ativo ? "status-active" : "status-blocked"}>
                  {selectedCompany.ativo ? "Ativa" : "Bloqueada"}
                </span>
                <span className={selectedCompany.read_only ? "status-readonly" : "status-active"}>
                  {selectedCompany.read_only ? "Somente leitura" : "Liberada para edicao"}
                </span>
              </div>
            )}
          </div>

          {selectedCompany && (
            <div className="company-actions">
              <button
                type="button"
                className={selectedCompany.ativo ? "danger" : "success"}
                onClick={() => updateCompanyStatus({ ativo: !selectedCompany.ativo })}
              >
                {selectedCompany.ativo ? "Bloquear conta" : "Desbloquear conta"}
              </button>
              <button
                type="button"
                disabled={!selectedCompany.ativo}
                onClick={() => updateCompanyStatus({ read_only: !selectedCompany.read_only })}
              >
                {selectedCompany.read_only ? "Liberar edicao" : "Somente leitura"}
              </button>
            </div>
          )}
        </section>
      )}

      <section className="users-panel">
        <h2>{editingUserId ? "Editar usuario" : "Novo usuario"}</h2>
        <form className="users-form" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
            disabled={Boolean(editingUserId)}
            required
          />
          <div className="password-field">
            <input
              type={showPassword ? "text" : "password"}
              placeholder={editingUserId ? "Nova senha opcional" : "Senha temporaria"}
              value={form.senha}
              onChange={(event) => setForm({ ...form, senha: event.target.value })}
              required={!editingUserId}
              minLength={form.senha ? 6 : undefined}
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              title={showPassword ? "Ocultar senha" : "Mostrar senha"}
              aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
            >
              {showPassword ? "Ocultar" : "Ver"}
            </button>
          </div>
          <select
            value={form.role}
            onChange={(event) => setForm({ ...form, role: event.target.value })}
          >
            <option value="operador_captura">Operador de captura</option>
            <option value="observador">Observador</option>
            <option value="admin">Administrador</option>
          </select>
          {editingUserId && (
            <select
              value={form.ativo ? "true" : "false"}
              onChange={(event) =>
                setForm({ ...form, ativo: event.target.value === "true" })
              }
            >
              <option value="true">Ativo</option>
              <option value="false">Inativo</option>
            </select>
          )}
          <button type="submit" disabled={loading || (isMaster && !selectedCompanyId)}>
            {loading ? "Salvando..." : editingUserId ? "Salvar alteracoes" : "Criar usuario"}
          </button>
          {editingUserId && (
            <button type="button" className="secondary" onClick={cancelEditUser}>
              Cancelar
            </button>
          )}
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
                <span>{user.ativo ? "Ativo" : "Inativo"}</span>
              </div>
              <div className="user-actions">
                <button type="button" onClick={() => startEditUser(user)}>
                  Editar
                </button>
                <button type="button" onClick={() => toggleUser(user)}>
                  {user.ativo ? "Desativar" : "Ativar"}
                </button>
                <button type="button" className="danger" onClick={() => deleteUser(user)}>
                  Excluir
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
