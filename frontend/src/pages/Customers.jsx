import { useState, useEffect } from "react";
import { customerService } from "../services";
import {
  birthdayInputToApi,
  formatBirthdayInput,
  normalizeBirthdayForInput,
} from "../utils/dateInput";
import "./Customers.css";

export default function Customers() {
  const [customers, setCustomers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    nome: "",
    telefone: "",
    email: "",
    data_nascimento: "", // NOVO
  });
  const [editingId, setEditingId] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);

  useEffect(() => {
    fetchCustomers();
  }, [page, search]);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const response = await customerService.list(page, 50, search);
      setCustomers(response.data.data);
      setTotal(response.data.total);
    } catch (err) {
      console.error("Erro ao buscar clientes", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await customerService.create({
        ...form,
        data_nascimento: birthdayInputToApi(form.data_nascimento),
      });
      setForm({ nome: "", telefone: "", email: "", data_nascimento: "" }); // ATUALIZADO
      setShowForm(false);
      setPage(1);
      fetchCustomers();
    } catch (err) {
      console.error("Erro ao criar cliente", err);
    }
  };

  const abrirEdicao = async (clienteId) => {
    try {
      const res = await customerService.getDetalhes(clienteId);
      setEditingId(clienteId);
      setForm({
        nome: res.data.data.nome,
        telefone: res.data.data.telefone || "",
        email: res.data.data.email || "",
        data_nascimento: normalizeBirthdayForInput(res.data.data.data_nascimento),
      });
      setShowEditModal(true);
    } catch (err) {
      console.error("Erro ao carregar detalhes", err);
      alert("Erro ao carregar dados do cliente");
    }
  };

  const salvarEdicao = async (e) => {
    e.preventDefault();
    try {
      await customerService.update(editingId, {
        ...form,
        data_nascimento: birthdayInputToApi(form.data_nascimento),
      });
      alert("Cliente atualizado com sucesso!");
      setShowEditModal(false);
      setEditingId(null);
      setForm({ nome: "", telefone: "", email: "", data_nascimento: "" });
      fetchCustomers();
    } catch (err) {
      console.error("Erro ao atualizar cliente", err);
      alert("Erro ao atualizar cliente");
    }
  };

  const deletarCliente = async (clienteId, nomeCliente) => {
    if (confirm(`Tem certeza que deseja deletar "${nomeCliente}"?`)) {
      try {
        await customerService.delete(clienteId);
        alert("Cliente deletado com sucesso!");
        fetchCustomers();
      } catch (err) {
        console.error("Erro ao deletar cliente", err);
        alert("Erro ao deletar cliente");
      }
    }
  };

  return (
    <div className="customers">
      <h1>👥 Clientes</h1>

      <div className="controls">
        <div className="search-label">Buscar por nome ou telefone</div>
        <input
          type="text"
          placeholder="🔍 Buscar cliente..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        {search && (
          <button
            type="button"
            className="btn-secondary"
            onClick={() => {
              setSearch("");
              setPage(1);
            }}
          >
            Limpar
          </button>
        )}

        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          ➕ Novo Cliente
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="customer-form">
          <input
            type="text"
            placeholder="Nome"
            value={form.nome}
            onChange={(e) => setForm({ ...form, nome: e.target.value })}
            required
          />

          <input
            type="tel"
            placeholder="Telefone (opcional)"
            value={form.telefone}
            onChange={(e) => setForm({ ...form, telefone: e.target.value })}
          />

          <input
            type="email"
            placeholder="Email (opcional)"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />

          <input
            type="text"
            inputMode="numeric"
            maxLength="10"
            placeholder="Data de Nascimento (opcional)"
            value={form.data_nascimento}
            onChange={(e) =>
              setForm({
                ...form,
                data_nascimento: formatBirthdayInput(e.target.value),
              })
            }
          />

          <div className="form-buttons">
            <button type="submit" className="btn-primary">
              Salvar
            </button>
            <button
              type="button"
              className="btn-secondary"
              onClick={() => setShowForm(false)}
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="loading">Carregando...</div>
      ) : (
        <>
          <table className="customers-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Telefone</th>
                <th>Email</th>
                <th>Pontos</th>
                <th>Ação</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.id}>
                  <td>{customer.nome}</td>
                  <td>{customer.telefone || "-"}</td>
                  <td>{customer.email || "-"}</td>
                  <td className="points">{customer.pontos}</td>
                  <td className="actions">
                    <button
                      className="btn-edit"
                      onClick={() => abrirEdicao(customer.id)}
                      title="Editar cliente"
                    >
                      ✏️ Editar
                    </button>
                    <button
                      className="btn-delete"
                      onClick={() => deletarCliente(customer.id, customer.nome)}
                      title="Deletar cliente"
                    >
                      🗑️ Deletar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="pagination">
            <p>
              Mostrando {customers.length} de {total} clientes
            </p>
            <div className="buttons">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
              >
                ← Anterior
              </button>
              <span>Página {page}</span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={customers.length < 50}
              >
                Próximo →
              </button>
            </div>
          </div>
        </>
      )}

      {/* MODAL DE EDIÇÃO */}
      {showEditModal && (
        <div className="modal-overlay" onClick={() => setShowEditModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>✏️ Editar Cliente</h2>
            <form onSubmit={salvarEdicao}>
              <input
                type="text"
                placeholder="Nome"
                value={form.nome}
                onChange={(e) => setForm({ ...form, nome: e.target.value })}
                required
              />

              <input
                type="tel"
                placeholder="Telefone (opcional)"
                value={form.telefone}
                onChange={(e) => setForm({ ...form, telefone: e.target.value })}
              />

              <input
                type="email"
                placeholder="Email (opcional)"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />

              <input
                type="text"
                inputMode="numeric"
                maxLength="10"
                placeholder="Data de Nascimento (opcional)"
                value={form.data_nascimento}
                onChange={(e) =>
                  setForm({
                    ...form,
                    data_nascimento: formatBirthdayInput(e.target.value),
                  })
                }
              />

              <div className="modal-buttons">
                <button type="submit" className="btn-primary">
                  💾 Salvar
                </button>
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingId(null);
                  }}
                >
                  ❌ Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
