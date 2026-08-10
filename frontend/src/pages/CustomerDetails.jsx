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
  const [loading, setLoading] = useState(true);
  const [pointsForm, setPointsForm] = useState({
    pontos: "",
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
      });

      setPointsForm({ pontos: "", tipo: "entrada", product_id: "", descricao: "" });
      fetchCustomer();
    } catch (err) {
      alert(err.response?.data?.detail || "Erro ao movimentar pontos");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading">Carregando...</div>;

  if (!customer) return <div className="error">Cliente não encontrado</div>;

  return (
    <div className="customer-details">
      <div className="header">
        <h1>{customer.nome}</h1>
        <div className="points-display">
          <span className="label">Saldo de Pontos:</span>
          <span className="points">{customer.pontos}</span>
        </div>
      </div>

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
    </div>
  );
}
