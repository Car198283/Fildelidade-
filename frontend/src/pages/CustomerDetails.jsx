import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { customerService, dashboardService, pointsService, productService } from "../services";
import "./CustomerDetails.css";

export default function CustomerDetails() {
  const { id } = useParams();
  const [customer, setCustomer] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [products, setProducts] = useState([]);
  const [consumedProducts, setConsumedProducts] = useState([]);
  const [activeTab, setActiveTab] = useState("perfil");
  const [loading, setLoading] = useState(true);
  const [pointsForm, setPointsForm] = useState({
    pontos: "",
    valor_compra: "",
    tipo: "entrada",
    product_id: "",
    descricao: "",
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchCustomer();
  }, [id]);

  const fetchCustomer = async () => {
    setLoading(true);
    try {
      const response = await customerService.get(id);
      setCustomer(response.data.data);
      setTransactions(response.data.data.transactions || []);
      const [productsRes, consumedRes] = await Promise.all([
        productService.list(1, 100, ""),
        dashboardService.customerConsumedProducts(id, 50),
      ]);
      setProducts(Array.isArray(productsRes.data?.data) ? productsRes.data.data : []);
      setConsumedProducts(Array.isArray(consumedRes.data?.data) ? consumedRes.data.data : []);
    } catch (err) {
      console.error("Erro ao buscar cliente", err);
    } finally {
      setLoading(false);
    }
  };

  const handlePointsSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await pointsService.moviment(id, {
        pontos: parseFloat(pointsForm.pontos),
        tipo: pointsForm.tipo,
        product_id: pointsForm.product_id ? Number(pointsForm.product_id) : null,
        descricao: pointsForm.descricao,
        motivo: pointsForm.descricao.trim() || "Movimentacao manual no cadastro do cliente",
        valor_compra: pointsForm.valor_compra ? Number(pointsForm.valor_compra) : null,
      });

      setPointsForm({ pontos: "", valor_compra: "", tipo: "entrada", product_id: "", descricao: "" });
      fetchCustomer();
    } catch (err) {
      alert(err.response?.data?.detail || "Erro ao movimentar pontos");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading">Carregando...</div>;

  if (!customer) return <div className="error">Cliente não encontrado</div>;

  const purchaseProfile = customer.purchase_profile || {};
  const purchases = transactions.filter((tx) => tx.tipo === "entrada" && tx.valor_compra != null);
  const formatCurrency = (value) => Number(value || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  const formatDateTime = (value) => value ? new Date(value).toLocaleString("pt-BR") : "-";

  return (
    <div className="customer-details">
      <div className="header">
        <h1>{customer.nome}</h1>
        <div className="points-display">
          <span className="label">Saldo de Pontos:</span>
          <span className="points">{customer.pontos}</span>
        </div>
      </div>

      <div className="customer-tabs" role="tablist" aria-label="Seções do cliente">
        <button type="button" className={activeTab === "perfil" ? "active" : ""} onClick={() => setActiveTab("perfil")}>Perfil</button>
        <button type="button" className={activeTab === "historico" ? "active" : ""} onClick={() => setActiveTab("historico")}>Histórico de compras</button>
      </div>

      {activeTab === "perfil" && <>
      <div className="info-card">
        <h3>📋 Informações</h3>
        <p>
          <strong>Email:</strong> {customer.email || "-"}
        </p>
        <p>
          <strong>Telefone:</strong> {customer.telefone || "-"}
        </p>
        <p>
          <strong>Data de Nascimento:</strong>{" "}
          {customer.data_nascimento
            ? new Date(customer.data_nascimento).toLocaleDateString("pt-BR")
            : "-"}
        </p>
        <p>
          <strong>Cadastro:</strong>{" "}
          {new Date(customer.created_at).toLocaleDateString("pt-BR")}
        </p>
      </div>

      <div className="points-card">
        <h3>🎯 Movimentação de Pontos</h3>
        <form onSubmit={handlePointsSubmit} className="points-form">
          <input
            type="number"
            placeholder="Quantidade de pontos"
            value={pointsForm.pontos}
            onChange={(e) =>
              setPointsForm({ ...pointsForm, pontos: e.target.value })
            }
            required
            step="0.01"
            min="0"
          />

          <input
            type="number"
            placeholder="Valor da compra (R$)"
            value={pointsForm.valor_compra}
            onChange={(e) => setPointsForm({ ...pointsForm, valor_compra: e.target.value })}
            step="0.01"
            min="0"
          />

          <select
            value={pointsForm.tipo}
            onChange={(e) =>
              setPointsForm({ ...pointsForm, tipo: e.target.value })
            }
          >
            <option value="entrada">➕ Adicionar Pontos</option>
            <option value="saida">➖ Resgatar Pontos</option>
          </select>

          <select
            value={pointsForm.product_id}
            onChange={(e) =>
              setPointsForm({ ...pointsForm, product_id: e.target.value })
            }
          >
            <option value="">Produto consumido</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.nome}
              </option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Descrição (ex: Compra realizada)"
            value={pointsForm.descricao}
            onChange={(e) =>
              setPointsForm({ ...pointsForm, descricao: e.target.value })
            }
          />

          <button type="submit" className="btn-primary" disabled={submitting}>
            {submitting ? "Procesando..." : "Confirmar"}
          </button>
        </form>
      </div>

      </>}

      {activeTab === "historico" && <>
      <div className="purchase-summary">
        <article><span>Total gasto</span><strong>{formatCurrency(purchaseProfile.total_gasto)}</strong></article>
        <article><span>Compras registradas</span><strong>{purchaseProfile.total_compras || 0}</strong></article>
        <article><span>Ticket médio</span><strong>{formatCurrency(purchaseProfile.ticket_medio)}</strong></article>
        <article><span>Última compra</span><strong>{formatDateTime(purchaseProfile.ultima_compra)}</strong></article>
        <article><span>Produto favorito</span><strong>{purchaseProfile.produto_favorito || "-"}</strong></article>
      </div>

      <div className="history-card">
        <h3>Histórico de compras</h3>
        {purchases.length === 0 ? <p className="empty">Nenhuma compra com valor registrada</p> : (
          <div className="table-scroll"><table className="transactions-table">
            <thead><tr><th>Data e hora</th><th>Produto</th><th>Valor</th><th>Pontos</th><th>Registrado por</th><th>Descrição</th></tr></thead>
            <tbody>{purchases.map((tx) => <tr key={tx.id}>
              <td>{formatDateTime(tx.created_at)}</td>
              <td>{tx.product_nome || "-"}</td>
              <td className="purchase-value">{formatCurrency(tx.valor_compra)}</td>
              <td className="points entrada">+{tx.pontos}</td>
              <td>{tx.usuario_nome || "-"}</td>
              <td>{tx.descricao || tx.motivo || "-"}</td>
            </tr>)}</tbody>
          </table></div>
        )}
      </div>

      <div className="history-card">
        <h3>Produtos Consumidos</h3>
        {consumedProducts.length === 0 ? (
          <p className="empty">Nenhum produto consumido registrado</p>
        ) : (
          <table className="transactions-table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Produto</th>
                <th>Pontos</th>
                <th>Descricao</th>
              </tr>
            </thead>
            <tbody>
              {consumedProducts.map((item) => (
                <tr key={item.id}>
                  <td>{new Date(item.created_at).toLocaleDateString("pt-BR")}</td>
                  <td>{item.produto}</td>
                  <td className="points entrada">{item.pontos}</td>
                  <td>{item.descricao || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="history-card">
        <h3>📜 Histórico de Transações</h3>
        {transactions.length === 0 ? (
          <p className="empty">Sem transações</p>
        ) : (
          <table className="transactions-table">
            <thead>
              <tr>
                <th>Data</th>
                <th>Tipo</th>
                <th>Pontos</th>
                <th>Descrição</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx) => (
                <tr key={tx.id} className={`type-${tx.tipo}`}>
                  <td>{new Date(tx.created_at).toLocaleDateString("pt-BR")}</td>
                  <td className="tipo">
                    {tx.tipo === "entrada" ? "➕ Entrada" : "➖ Saída"}
                  </td>
                  <td className={`points ${tx.tipo}`}>
                    {tx.tipo === "entrada" ? "+" : "-"}
                    {tx.pontos}
                  </td>
                  <td>{tx.descricao || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      </>}
    </div>
  );
}
