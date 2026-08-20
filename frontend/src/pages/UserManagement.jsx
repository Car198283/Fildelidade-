import { useEffect, useMemo, useState } from "react";
import { adminService } from "../services";
import { formatApiDateTime } from "../utils/dateTime";
import "./UserManagement.css";

const emptyForm = { nome: "", email: "", senha: "", role: "operador_captura", ativo: true, motivo: "Cadastro de usuario" };
const roleNames = { master: "Master", admin: "Administrador", operador_captura: "Operador de captura", observador: "Observador" };
const roleDescriptions = {
  admin: "Gerencia clientes, produtos, promocoes, usuarios e relatorios.",
  operador_captura: "Registra compras e movimenta pontos, sem acesso administrativo.",
  observador: "Consulta informacoes permitidas, sem alterar dados.",
};

function storedUser() { try { return JSON.parse(sessionStorage.getItem("user") || "{}"); } catch { return {}; } }
function formatDate(value) { return value ? formatApiDateTime(value) : "Nunca acessou"; }

export default function UserManagement() {
  const currentUser = storedUser();
  const isMaster = currentUser.role === "master";
  const [users, setUsers] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState(sessionStorage.getItem("selectedCompanyId") || "");
  const [form, setForm] = useState(emptyForm);
  const [editingUserId, setEditingUserId] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [filters, setFilters] = useState({ search: "", role: "", status: "" });
  const [metrics, setMetrics] = useState({ total: 0, ativos: 0, inativos: 0, administradores: 0 });
  const [history, setHistory] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 10;

  const selectedCompany = companies.find((item) => String(item.id) === String(selectedCompanyId));
  const queryFilters = useMemo(() => ({
    search: filters.search || undefined,
    role: filters.role || undefined,
    ativo: filters.status === "" ? undefined : filters.status === "active",
    page, limit: pageSize,
  }), [filters, page]);

  const loadUsers = async () => {
    const response = await adminService.users(isMaster ? selectedCompanyId || null : null, queryFilters);
    setUsers(response.data?.data || []); setMetrics(response.data?.metrics || {}); setTotal(response.data?.total || 0);
  };
  const loadHistory = async () => {
    const response = await adminService.userHistory(isMaster ? selectedCompanyId || null : null);
    setHistory(response.data?.data || []);
  };
  const refresh = async () => { await Promise.all([loadUsers(), loadHistory()]); };

  useEffect(() => {
    if (!isMaster) return;
    adminService.companies().then((response) => {
      const data = response.data?.data || []; setCompanies(data);
      if (!selectedCompanyId && data.length) { const id = String(data[0].id); setSelectedCompanyId(id); sessionStorage.setItem("selectedCompanyId", id); }
    }).catch(() => setMessage("Nao foi possivel carregar empresas."));
  }, []);
  useEffect(() => { refresh().catch(() => setMessage("Nao foi possivel carregar usuarios.")); }, [selectedCompanyId, queryFilters]);

  const submit = async (event) => {
    event.preventDefault(); setLoading(true); setMessage("");
    try {
      if (editingUserId) {
        await adminService.updateUser(editingUserId, { nome: form.nome, email: form.email, role: form.role, ativo: form.ativo, motivo: form.motivo });
        setMessage("Usuario atualizado e alteracao auditada.");
      } else {
        await adminService.createUser({ nome: form.nome, email: form.email, senha: form.senha, role: form.role, company_id: isMaster ? Number(selectedCompanyId) : null, exigir_troca_senha: true });
        setMessage("Usuario criado. No primeiro login, use a senha temporaria e cadastre uma nova senha.");
      }
      cancelEdit(false); await refresh();
    } catch (error) { setMessage(error.response?.data?.detail || "Nao foi possivel salvar usuario."); }
    finally { setLoading(false); }
  };
  const cancelEdit = (clear = true) => { setEditingUserId(null); setForm(emptyForm); setShowPassword(false); if (clear) setMessage(""); };
  const edit = (user) => { setEditingUserId(user.id); setForm({ ...emptyForm, nome: user.nome || "", email: user.email, role: user.role, ativo: user.ativo, motivo: "Atualizacao cadastral" }); setMessage(""); };
  const toggle = async (user) => {
    const action = user.ativo ? "desativar" : "reativar";
    if (!window.confirm(`Confirma ${action} ${user.nome || user.email}?`)) return;
    try { await adminService.updateUser(user.id, { ativo: !user.ativo, motivo: `${action} usuario` }); await refresh(); setMessage(`Usuario ${user.ativo ? "desativado" : "reativado"}.`); }
    catch (error) { setMessage(error.response?.data?.detail || "Acao nao permitida."); }
  };
  const resetPassword = async (user) => {
    const password = window.prompt(`Digite uma senha temporaria para ${user.email} (minimo 8 caracteres):`);
    if (!password) return;
    if (password.length < 8) return setMessage("A senha temporaria deve ter pelo menos 8 caracteres.");
    if (!window.confirm("Confirma redefinir a senha? O usuario sera obrigado a troca-la no proximo acesso.")) return;
    try { await adminService.updateUser(user.id, { senha: password, exigir_troca_senha: true, motivo: "Redefinicao administrativa de senha" }); await refresh(); setMessage("Senha temporaria definida com troca obrigatoria no proximo acesso."); }
    catch (error) { setMessage(error.response?.data?.detail || "Nao foi possivel redefinir a senha."); }
  };
  const removeUser = async (user) => {
    const identification = user.nome || user.email;
    if (!window.confirm(`Excluir o usuario ${identification}?\n\nO acesso sera removido, mas o historico de atividades sera preservado.`)) return;
    try {
      await adminService.deleteUser(user.id);
      if (editingUserId === user.id) cancelEdit(false);
      await refresh();
      setMessage("Usuario excluido da lista; o historico de atividades foi preservado.");
    } catch (error) { setMessage(error.response?.data?.detail || "Nao foi possivel excluir o usuario."); }
  };
  const updateCompany = async (data) => {
    try { await adminService.updateCompany(selectedCompanyId, data); const response = await adminService.companies(); setCompanies(response.data?.data || []); setMessage("Status da empresa atualizado."); }
    catch (error) { setMessage(error.response?.data?.detail || "Nao foi possivel atualizar a empresa."); }
  };

  return <div className="users-page">
    <header className="users-header"><h1>Usuarios e Acessos</h1><p>Controle seguro de perfis, atividades e historico por empresa.</p></header>
    {message && <div className="users-message">{message}</div>}
    {isMaster && <section className="users-panel"><div className="company-control"><div><label>Empresa em gestao</label><select value={selectedCompanyId} onChange={(e) => { setSelectedCompanyId(e.target.value); sessionStorage.setItem("selectedCompanyId", e.target.value); setPage(1); }}>{companies.map((company) => <option key={company.id} value={company.id}>{company.nome}</option>)}</select></div>{selectedCompany && <div className="company-status"><span className={selectedCompany.ativo ? "status-active" : "status-blocked"}>{selectedCompany.ativo ? "Ativa" : "Bloqueada"}</span><span className={selectedCompany.read_only ? "status-readonly" : "status-active"}>{selectedCompany.read_only ? "Somente leitura" : "Liberada para edicao"}</span></div>}</div>{selectedCompany && <div className="company-actions"><button className={selectedCompany.ativo ? "danger" : "success"} onClick={() => updateCompany({ ativo: !selectedCompany.ativo })}>{selectedCompany.ativo ? "Bloquear conta" : "Desbloquear conta"}</button><button disabled={!selectedCompany.ativo} onClick={() => updateCompany({ read_only: !selectedCompany.read_only })}>{selectedCompany.read_only ? "Liberar edicao" : "Somente leitura"}</button></div>}</section>}

    <section className="users-metrics">{[["Total", metrics.total],["Ativos", metrics.ativos],["Inativos", metrics.inativos],["Administradores", metrics.administradores]].map(([label, value]) => <article key={label}><span>{label}</span><strong>{value || 0}</strong></article>)}</section>

    <section className="users-panel"><h2>{editingUserId ? "Editar usuario" : "Novo usuario"}</h2><form className="users-form" onSubmit={submit} autoComplete="off">
      <input placeholder="Nome completo" value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} autoComplete="off" required minLength="2"/>
      <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} autoComplete="off" required/>
      {!editingUserId && <div className="password-field"><input type={showPassword ? "text" : "password"} placeholder="Senha temporaria" value={form.senha} onChange={(e) => setForm({ ...form, senha: e.target.value })} autoComplete="new-password" required minLength="8"/><button type="button" className="password-toggle" onClick={() => setShowPassword(!showPassword)}>{showPassword ? "Ocultar" : "Ver"}</button></div>}
      <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}><option value="operador_captura">Operador de captura</option><option value="observador">Observador</option><option value="admin">Administrador</option></select>
      {editingUserId && <><select value={form.ativo ? "true" : "false"} onChange={(e) => setForm({ ...form, ativo: e.target.value === "true" })}><option value="true">Ativo</option><option value="false">Inativo</option></select><input placeholder="Motivo da alteracao" value={form.motivo} onChange={(e) => setForm({ ...form, motivo: e.target.value })} required minLength="3"/></>}
      <button type="submit" disabled={loading || (isMaster && !selectedCompanyId)}>{loading ? "Salvando..." : editingUserId ? "Salvar alteracoes" : "Criar usuario"}</button>{editingUserId && <button type="button" className="secondary" onClick={() => cancelEdit()}>Cancelar</button>}
    </form><div className="role-help"><strong>{roleNames[form.role]}:</strong> {roleDescriptions[form.role]}</div></section>

    <section className="users-panel"><div className="list-header"><h2>Usuarios cadastrados</h2><div className="users-filters"><input placeholder="Buscar por nome ou email" value={filters.search} onChange={(e) => { setFilters({ ...filters, search: e.target.value }); setPage(1); }}/><select value={filters.role} onChange={(e) => { setFilters({ ...filters, role: e.target.value }); setPage(1); }}><option value="">Todos os perfis</option><option value="admin">Administradores</option><option value="operador_captura">Operadores</option><option value="observador">Observadores</option></select><select value={filters.status} onChange={(e) => { setFilters({ ...filters, status: e.target.value }); setPage(1); }}><option value="">Todos os status</option><option value="active">Ativos</option><option value="inactive">Inativos</option></select></div></div>
      <div className="users-list">{users.map((user) => <article className="user-row" key={user.id}><div className="user-identity"><strong>{user.nome || "Nome nao informado"}</strong><span>{user.email}</span><div><span className={`role-badge role-${user.role}`}>{roleNames[user.role] || user.role}</span><span className={user.ativo ? "active-badge" : "inactive-badge"}>{user.ativo ? "Ativo" : "Inativo"}</span>{user.exigir_troca_senha && <span className="password-badge">Troca de senha pendente</span>}</div><small>Ultimo acesso: {formatDate(user.ultimo_acesso)} · Criado em: {formatDate(user.created_at)}</small></div><div className="user-actions"><button onClick={() => edit(user)}>Editar</button><button className="secondary" onClick={() => resetPassword(user)}>Redefinir senha</button><button className={user.ativo ? "danger" : "success"} onClick={() => toggle(user)}>{user.ativo ? "Desativar" : "Reativar"}</button>{isMaster && <button className="danger-outline" onClick={() => removeUser(user)}>Excluir</button>}</div></article>)}</div>
      {!users.length && <p className="empty-users">Nenhum usuario encontrado com estes filtros.</p>}<div className="pagination"><button disabled={page === 1} onClick={() => setPage(page - 1)}>Anterior</button><span>Pagina {page} de {Math.max(1, Math.ceil(total / pageSize))}</span><button disabled={page * pageSize >= total} onClick={() => setPage(page + 1)}>Proxima</button></div>
    </section>

    <section className="users-panel"><h2>Historico de alteracoes</h2><div className="audit-list">{history.slice(0, 10).map((item) => <div key={item.id}><strong>{item.acao}</strong><span>Usuario #{item.target_user_id} por usuario #{item.actor_user_id}</span><small>{item.motivo} · {formatDate(item.created_at)}</small></div>)}{!history.length && <p>Nenhuma alteracao registrada ainda.</p>}</div></section>
  </div>;
}
