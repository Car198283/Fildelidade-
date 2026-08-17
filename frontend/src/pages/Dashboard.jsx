import { useEffect, useState } from "react";
import { adminService, dashboardService, customerService, pointsService } from "../services";
import {
  birthdayInputToApi,
  formatBirthdayInput,
  normalizeBirthdayForInput,
} from "../utils/dateInput";
import "./Dashboard.css";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [topCustomers, setTopCustomers] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const [clientesPremiadosCompleto, setClientesPremiadosCompleto] = useState(
    [],
  );
  const [clientesQuasePremiados, setClientesQuasePremiados] = useState([]);
  const [currentCompany, setCurrentCompany] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState(
    localStorage.getItem("selectedCompanyId") || "",
  );
  const [loading, setLoading] = useState(true);
  const [editingCliente, setEditingCliente] = useState(null);
  const [formData, setFormData] = useState({
    nome: "",
    telefone: "",
    email: "",
    data_nascimento: "",
  });

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      let companyRequest = adminService.me();

      if (user.role === "master") {
        const companiesRes = await adminService.companies();
        const companyList = companiesRes.data?.data || [];
        const storedCompanyId =
          localStorage.getItem("selectedCompanyId") || selectedCompanyId;
        const selectedCompany =
          companyList.find(
            (company) =>
              company.ativo && String(company.id) === String(storedCompanyId),
          ) ||
          companyList.find((company) => company.ativo) ||
          companyList[0] ||
          null;

        setCompanies(companyList);
        setCurrentCompany(selectedCompany);

        if (selectedCompany) {
          const nextCompanyId = String(selectedCompany.id);
          setSelectedCompanyId(nextCompanyId);
          localStorage.setItem("selectedCompanyId", nextCompanyId);
        } else {
          localStorage.removeItem("selectedCompanyId");
        }

        companyRequest = Promise.resolve(companiesRes);
      }

      const [statsRes, topRes, productsRes, premiadosRes, quaseRes, companyRes] = await Promise.allSettled([
        dashboardService.stats(),
        dashboardService.topCustomers(10),
        dashboardService.topProducts(10),
        dashboardService.clientesPremiadosCompleto(),
        dashboardService.clientesQuasePremiados(),
        companyRequest,
      ]);

      if (statsRes.status === "fulfilled") setStats(statsRes.value.data.data);
      if (topRes.status === "fulfilled") setTopCustomers(topRes.value.data.data);
      if (productsRes.status === "fulfilled") setTopProducts(productsRes.value.data.data);
      if (premiadosRes.status === "fulfilled") {
        setClientesPremiadosCompleto(premiadosRes.value.data.data);
      }
      if (quaseRes.status === "fulfilled") {
        setClientesQuasePremiados(quaseRes.value.data.data);
      }

      if (user.role === "master") {
        const companies = companyRes.status === "fulfilled" ? companyRes.value.data?.data || [] : [];
        setCompanies(companies);
        setCurrentCompany(
          companies.find((company) => String(company.id) === localStorage.getItem("selectedCompanyId")) || null,
        );
      } else {
        const me = companyRes.data?.data || {};
        setCurrentCompany({
          id: me.company_id,
          nome: me.company_name || "Minha empresa",
          read_only: me.company_read_only,
        });
      }
    } catch (err) {
      console.error("Erro ao carregar dashboard", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleCompanyChange = (event) => {
    const companyId = event.target.value;
    setSelectedCompanyId(companyId);
    localStorage.setItem("selectedCompanyId", companyId);
    setCurrentCompany(
      companies.find((company) => String(company.id) === String(companyId)) || null,
    );
    fetchDashboardData();
  };

  const abrirEdicao = async (clienteId) => {
    try {
      const res = await customerService.getDetalhes(clienteId);
      setEditingCliente(res.data.data);
      setFormData({
        nome: res.data.data.nome,
        telefone: res.data.data.telefone || "",
        email: res.data.data.email || "",
        data_nascimento: normalizeBirthdayForInput(res.data.data.data_nascimento),
      });
    } catch (err) {
      console.error("Erro ao carregar dados do cliente", err);
    }
  };

  const salvarEdicao = async () => {
    try {
      await customerService.update(editingCliente.id, {
        ...formData,
        data_nascimento: birthdayInputToApi(formData.data_nascimento),
      });
      alert("Cliente atualizado com sucesso!");
      setEditingCliente(null);
      // Recarregar dados
      window.location.reload();
    } catch (err) {
      console.error("Erro ao atualizar cliente", err);
      alert("Erro ao atualizar cliente");
    }
  };

  const deletarCliente = async (clienteId) => {
    if (confirm("Tem certeza que deseja deletar este cliente?")) {
      try {
        await customerService.delete(clienteId);
        alert("Cliente deletado com sucesso!");
        // Recarregar dados
        window.location.reload();
      } catch (err) {
        console.error("Erro ao deletar cliente", err);
        alert("Erro ao deletar cliente");
      }
    }
  };

  const resgatarPremio = async (cliente) => {
    if (cliente.pontos <= 0) {
      alert("Cliente nao tem pontos para resgatar.");
      return;
    }

    if (
      confirm(
        `Resgatar premio de ${cliente.nome} e zerar ${cliente.pontos} ponto(s)?`,
      )
    ) {
      try {
        await pointsService.moviment(cliente.id, {
          pontos: Number(cliente.pontos),
          tipo: "saida",
          descricao: "Resgate de premio",
          motivo: "Premio resgatado pelo dashboard",
        });

        alert("Premio resgatado e pontos zerados com sucesso!");
        fetchDashboardData();
      } catch (err) {
        console.error("Erro ao resgatar premio", err);
        alert(err.response?.data?.detail || "Erro ao resgatar premio");
      }
    }
  };

  const baixarPdf = async (downloadFn, filename) => {
    try {
      const response = await downloadFn();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");

      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Erro ao baixar PDF", err);
      alert(err.response?.data?.detail || "Erro ao baixar PDF");
    }
  };

  if (loading) return <div className="loading">Carregando...</div>;

  const totalClientes = stats?.total_clientes ?? stats?.total_customers ?? 0;
  const user = JSON.parse(localStorage.getItem("user") || "{}");
  const isMaster = user.role === "master";

  return (
    <div className="dashboard">
      <div className="dashboard-heading">
        <div>
          <h1>Dashboard</h1>
          <p>
            Empresa em visualizacao:{" "}
            {isMaster ? (
              <select
                className="company-view-select"
                value={selectedCompanyId}
                onChange={handleCompanyChange}
              >
                {companies.map((company) => (
                  <option key={company.id} value={company.id} disabled={!company.ativo}>
                    {company.nome}
                  </option>
                ))}
              </select>
            ) : (
              <strong>{currentCompany?.nome || "Nao identificada"}</strong>
            )}
          </p>
        </div>
        {currentCompany?.read_only && (
          <span className="dashboard-status">Somente leitura</span>
        )}
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>👥 Total de Clientes</h3>
            <p className="stat-value">{totalClientes}</p>
          </div>

          <div className="stat-card premium">
            <h3>⭐ Clientes Premiados (100%)</h3>
            <p className="stat-value">{clientesPremiadosCompleto.length}</p>
          </div>

          <div className="stat-card warning">
            <h3>⚡ Quase Premiados (80-99%)</h3>
            <p className="stat-value">{clientesQuasePremiados.length}</p>
          </div>

          <div className="stat-card danger">
            <h3>⚠️ Sem compras (15+ dias)</h3>
            <p className="stat-value">{stats.clientes_inativos_15 ?? stats.clientes_inativos}</p>
          </div>

          <div className="stat-card danger">
            <h3>🚨 Sem compras (30+ dias)</h3>
            <p className="stat-value">{stats.clientes_inativos_30 ?? 0}</p>
          </div>

          <div className="stat-card birthday">
            <h3>🎂 Aniversariantes Mês</h3>
            <p className="stat-value">{stats.aniversariantes_mes}</p>
          </div>

          <div className="stat-card">
            <h3>⬆️ Pontos Distribuídos</h3>
            <p className="stat-value">{stats.total_points_distributed}</p>
          </div>

          <div className="stat-card">
            <h3>⬇️ Pontos Resgatados</h3>
            <p className="stat-value">{stats.total_points_redeemed}</p>
          </div>

          <div className="stat-card">
            <h3>🔄 Em Circulação</h3>
            <p className="stat-value">{stats.total_points_circulation}</p>
          </div>
        </div>
      )}

      {/* SEÇÃO: CLIENTES PREMIADOS (100%) */}
      <div className="premios-section">
        <h2>🏆 Clientes Premiados (100%)</h2>
        {clientesPremiadosCompleto.length === 0 ? (
          <p className="vazio">Nenhum cliente 100% premiado ainda</p>
        ) : (
          <div className="clientes-grid">
            {clientesPremiadosCompleto.map((cliente) => (
              <div key={cliente.id} className="cliente-card premiado">
                <div className="card-header">
                  <h4>{cliente.nome}</h4>
                  <span className="badge badge-premium">100%</span>
                </div>
                <p>
                  <strong>Telefone:</strong> {cliente.telefone || "N/A"}
                </p>
                <p>
                  <strong>Email:</strong> {cliente.email || "N/A"}
                </p>
                <p>
                  <strong>Pontos:</strong> {cliente.pontos}
                </p>
                <p>
                  <strong>Valor Gasto:</strong> R${" "}
                  {cliente.valor_gasto_atual?.toFixed(2) || "0.00"}
                </p>
                <p>
                  <strong>Produtos Comprados:</strong>{" "}
                  {cliente.quantidade_produtos_comprados || 0}
                </p>
                <div className="card-actions">
                  <button
                    className="btn btn-small btn-redeem"
                    onClick={() => resgatarPremio(cliente)}
                  >
                    Resgatar premio
                  </button>
                  <button
                    className="btn btn-small btn-edit"
                    onClick={() => abrirEdicao(cliente.id)}
                  >
                    ✏️ Editar
                  </button>
                  <button
                    className="btn btn-small btn-delete"
                    onClick={() => deletarCliente(cliente.id)}
                  >
                    🗑️ Deletar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* SEÇÃO: CLIENTES QUASE PREMIADOS (80-99%) */}
      <div className="premios-section">
        <h2>⚡ Clientes Quase Premiados (80-99%)</h2>
        {clientesQuasePremiados.length === 0 ? (
          <p className="vazio">Nenhum cliente quase premiado</p>
        ) : (
          <div className="clientes-grid">
            {clientesQuasePremiados.map((cliente) => (
              <div key={cliente.id} className="cliente-card quase-premiado">
                <div className="card-header">
                  <h4>{cliente.nome}</h4>
                  <span className="badge badge-warning">
                    {cliente.percentual}%
                  </span>
                </div>
                <p>
                  <strong>Telefone:</strong> {cliente.telefone || "N/A"}
                </p>
                <p>
                  <strong>Email:</strong> {cliente.email || "N/A"}
                </p>
                <p>
                  <strong>Pontos:</strong> {cliente.pontos}
                </p>
                <p>
                  <strong>Falta:</strong>{" "}
                  <span className="falta">{cliente.falta} pontos</span>
                </p>
                <div className="progress-bar">
                  <div
                    className="progress"
                    style={{ width: `${cliente.percentual}%` }}
                  ></div>
                </div>
                <div className="card-actions">
                  <button
                    className="btn btn-small btn-edit"
                    onClick={() => abrirEdicao(cliente.id)}
                  >
                    ✏️ Editar
                  </button>
                  <button
                    className="btn btn-small btn-delete"
                    onClick={() => deletarCliente(cliente.id)}
                  >
                    🗑️ Deletar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="reports-section">
        <h2>📄 Relatórios em PDF</h2>
        <div className="reports-grid">
          <button
            className="btn-report aniversariantes"
            onClick={() =>
              baixarPdf(
                dashboardService.downloadAniversariantesPdf,
                "aniversariantes.pdf",
              )
            }
          >
            🎂 Baixar Aniversariantes
          </button>
          <button
            className="btn-report premiados"
            onClick={() =>
              baixarPdf(
                dashboardService.downloadPremiadosPdf,
                "clientes_premiados.pdf",
              )
            }
          >
            ⭐ Baixar Premiados
          </button>
          <button
            className="btn-report inativos"
            onClick={() =>
              baixarPdf(
                dashboardService.downloadInativosPdf,
                "clientes_inativos.pdf",
              )
            }
          >
            ⚠️ Baixar Inativos
          </button>
        </div>
      </div>

      <div className="top-customers">
        <h2>🏆 Top 10 Clientes</h2>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Nome</th>
              <th>Pontos</th>
              <th>Telefone</th>
            </tr>
          </thead>
          <tbody>
            {topCustomers.map((customer, idx) => (
              <tr key={customer.id}>
                <td>{idx + 1}</td>
                <td>{customer.nome}</td>
                <td className="points">{customer.pontos}</td>
                <td>{customer.telefone || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* MODAL DE EDIÇÃO */}
      <div className="top-customers">
        <h2>Produtos Mais Vendidos</h2>
        {topProducts.length === 0 ? (
          <p className="vazio">Nenhum produto consumido registrado ainda</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Produto</th>
                <th>Vendas</th>
                <th>Pontos</th>
              </tr>
            </thead>
            <tbody>
              {topProducts.map((product, idx) => (
                <tr key={`${product.product_id || "manual"}-${product.produto}`}>
                  <td>{idx + 1}</td>
                  <td>{product.produto}</td>
                  <td>{product.quantidade}</td>
                  <td className="points">{product.pontos}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {editingCliente && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Editar Cliente</h3>
              <button
                className="close-btn"
                onClick={() => setEditingCliente(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Nome:</label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) =>
                    setFormData({ ...formData, nome: e.target.value })
                  }
                />
              </div>
              <div className="form-group">
                <label>Telefone:</label>
                <input
                  type="tel"
                  value={formData.telefone}
                  onChange={(e) =>
                    setFormData({ ...formData, telefone: e.target.value })
                  }
                />
              </div>
              <div className="form-group">
                <label>Email:</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                />
              </div>
              <div className="form-group">
                <label>Data de Nascimento:</label>
                <input
                  type="text"
                  inputMode="numeric"
                  maxLength="10"
                  placeholder="dd/mm/aaaa"
                  value={formData.data_nascimento}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      data_nascimento: formatBirthdayInput(e.target.value),
                    })
                  }
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-cancel"
                onClick={() => setEditingCliente(null)}
              >
                Cancelar
              </button>
              <button className="btn btn-primary" onClick={salvarEdicao}>
                Salvar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
