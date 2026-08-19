import { useEffect, useMemo, useState } from "react";
import { customerService, dashboardService, pointsService, productService } from "../services";
import API_URL from "../config";
import { birthdayInputToApi, formatBirthdayInput } from "../utils/dateInput";
import "./MobileCapture.css";

const emptyCustomerForm = {
  nome: "",
  telefone: "",
  email: "",
  data_nascimento: "",
};

const emptyPointsForm = {
  pontos: "",
  valor_compra: "",
  product_id: "",
  descricao: "",
};

function getApiMessage(error, fallback) {
  if (!error?.response) {
    return `${fallback}. O celular nao conseguiu conectar na API (${API_URL}). Confira se o backend esta aberto, se o celular esta no mesmo Wi-Fi e se o firewall do Windows liberou a porta 8000.`;
  }

  const detail = error?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).filter(Boolean).join(", ") || fallback;
  }
  return detail || fallback;
}

function formatPoints(value) {
  return Number(value || 0).toLocaleString("pt-BR");
}

function getStoredUser() {
  try {
    return JSON.parse(sessionStorage.getItem("user") || "{}");
  } catch {
    return {};
  }
}

export default function MobileCapture() {
  const currentUser = getStoredUser();
  const canOperateOnMobile =
    currentUser.role === "operador_captura" ||
    currentUser.role === "admin" ||
    currentUser.role === "master";
  const [mode, setMode] = useState("clientes");
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [premiados, setPremiados] = useState([]);
  const [quasePremiados, setQuasePremiados] = useState([]);
  const [aniversariantes, setAniversariantes] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(false);
  const [newCustomerForm, setNewCustomerForm] = useState(emptyCustomerForm);
  const [pointsForm, setPointsForm] = useState(emptyPointsForm);
  const [message, setMessage] = useState("");

  const selectedCustomerBalance = useMemo(
    () => formatPoints(selectedCustomer?.pontos),
    [selectedCustomer],
  );

  const showMessage = (text, timeout = 3000) => {
    setMessage(text);
    if (timeout) window.setTimeout(() => setMessage(""), timeout);
  };

  const handleLogout = () => {
    sessionStorage.removeItem("accessToken");
    sessionStorage.removeItem("user");
    sessionStorage.removeItem("mobileCaptureOnly");
    window.location.href = "/login?next=/captura";
  };

  const buscarClientes = async (searchTerm = "") => {
    try {
      const response = await customerService.list(1, 100, searchTerm);
      setCustomers(Array.isArray(response.data?.data) ? response.data.data : []);
    } catch (err) {
      console.error("Erro ao buscar clientes", err);
      showMessage("Nao foi possivel carregar os clientes.");
    }
  };

  const carregarProdutos = async () => {
    try {
      const response = await productService.list(1, 100, "");
      setProducts(Array.isArray(response.data?.data) ? response.data.data : []);
    } catch (err) {
      console.error("Erro ao carregar produtos", err);
      showMessage("Nao foi possivel carregar os produtos.");
    }
  };

  const carregarPremiados = async () => {
    setListLoading(true);
    try {
      const [premiadosResponse, quaseResponse] = await Promise.all([
        dashboardService.clientesPremiadosCompleto(100),
        dashboardService.clientesQuasePremiados(100),
      ]);
      setPremiados(Array.isArray(premiadosResponse.data?.data) ? premiadosResponse.data.data : []);
      setQuasePremiados(Array.isArray(quaseResponse.data?.data) ? quaseResponse.data.data : []);
    } catch (err) {
      console.error("Erro ao carregar premiados", err);
      showMessage("Nao foi possivel carregar os clientes premiados.");
    } finally {
      setListLoading(false);
    }
  };

  const carregarAniversariantes = async () => {
    setListLoading(true);
    try {
      const response = await dashboardService.aniversariantesDia(100);
      setAniversariantes(Array.isArray(response.data?.data) ? response.data.data : []);
    } catch (err) {
      console.error("Erro ao carregar aniversariantes", err);
      showMessage("Nao foi possivel carregar os aniversariantes.");
    } finally {
      setListLoading(false);
    }
  };

  useEffect(() => {
    if (!canOperateOnMobile) return;
    buscarClientes();
    carregarProdutos();
  }, [canOperateOnMobile]);

  useEffect(() => {
    if (!canOperateOnMobile) return;
    if (mode === "premiados") carregarPremiados();
    if (mode === "aniversarios") carregarAniversariantes();
  }, [canOperateOnMobile, mode]);

  if (!canOperateOnMobile) {
    return (
      <div className="mobile-capture">
        <div className="capture-header">
          <div>
            <h1>Acesso ao Celular</h1>
            <p>Este usuario esta cadastrado como observador.</p>
          </div>
          <button type="button" className="mobile-logout" onClick={handleLogout}>
            Sair
          </button>
        </div>

        <div className="message">
          Para usar o link do celular, cadastre o usuario como Operador de captura.
        </div>
      </div>
    );
  }

  const handleCreateCustomer = async (event) => {
    event.preventDefault();
    setLoading(true);

    try {
      const payload = {
        nome: newCustomerForm.nome.trim(),
        telefone: newCustomerForm.telefone.trim() || null,
        email: newCustomerForm.email.trim() || null,
        data_nascimento: birthdayInputToApi(newCustomerForm.data_nascimento),
      };

      await customerService.create(payload);
      setNewCustomerForm(emptyCustomerForm);
      showMessage("Cliente capturado com sucesso!", 2500);
      buscarClientes(search);
    } catch (err) {
      showMessage(getApiMessage(err, "Erro ao capturar cliente"));
    } finally {
      setLoading(false);
    }
  };

  const handleAddPoints = async (event) => {
    event.preventDefault();

    if (!selectedCustomer) {
      showMessage("Selecione um cliente.");
      return;
    }

    const pontos = Number(pointsForm.pontos);
    if (!Number.isFinite(pontos) || pontos <= 0) {
      showMessage("Informe uma quantidade de pontos maior que zero.");
      return;
    }

    setLoading(true);
    try {
      await pointsService.moviment(selectedCustomer.id, {
        pontos,
        tipo: "entrada",
        descricao: pointsForm.descricao.trim() || "Compra",
        motivo: pointsForm.descricao.trim() || "Compra registrada na captura mobile",
        product_id: pointsForm.product_id ? Number(pointsForm.product_id) : null,
        valor_compra: pointsForm.valor_compra ? Number(pointsForm.valor_compra) : null,
      });

      showMessage(`${formatPoints(pontos)} pontos lancados com sucesso.`);
      setPointsForm(emptyPointsForm);
      setSelectedCustomer(null);
      buscarClientes(search);
    } catch (err) {
      showMessage(getApiMessage(err, "Erro ao lancar pontos"));
    } finally {
      setLoading(false);
    }
  };

  const handleRedeemPrize = async (cliente) => {
    const pontos = Number(cliente.pontos || 0);
    if (pontos <= 0) {
      showMessage("Cliente nao possui pontos para resgatar.");
      return;
    }

    const premio = window.prompt(`Qual premio ${cliente.nome} esta recebendo?`);
    if (premio === null) return;
    if (!premio.trim()) {
      showMessage("Informe o premio entregue ao cliente.");
      return;
    }

    const confirmed = window.confirm(
      `Entregar "${premio.trim()}" para ${cliente.nome} e zerar ${formatPoints(pontos)} ponto(s)?`,
    );
    if (!confirmed) return;

    setLoading(true);
    try {
      await pointsService.moviment(cliente.id, {
        pontos,
        tipo: "saida",
        descricao: `Resgate de premio: ${premio.trim()}`,
        motivo: "Premio resgatado na captura mobile",
      });

      showMessage("Premio resgatado e pontuacao zerada.");
      carregarPremiados();
      buscarClientes(search);
    } catch (err) {
      showMessage(getApiMessage(err, "Erro ao resgatar premio"));
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value) => {
    setSearch(value);
    buscarClientes(value);
  };

  return (
    <div className="mobile-capture">
      <div className="capture-header">
        <div>
          <h1>Operacao no Celular</h1>
          <p>Clientes, pontos, premios e aniversariantes de hoje</p>
        </div>
        <button type="button" className="mobile-logout" onClick={handleLogout}>
          Sair
        </button>
      </div>

      {message && <div className="message">{message}</div>}

      <div className="tabs mobile-tabs">
        <button
          type="button"
          className={`tab ${mode === "clientes" ? "active" : ""}`}
          onClick={() => setMode("clientes")}
        >
          Clientes
        </button>
        <button
          type="button"
          className={`tab ${mode === "pontos" ? "active" : ""}`}
          onClick={() => setMode("pontos")}
        >
          Pontos
        </button>
        <button
          type="button"
          className={`tab ${mode === "premiados" ? "active" : ""}`}
          onClick={() => setMode("premiados")}
        >
          Premiados
        </button>
        <button
          type="button"
          className={`tab ${mode === "aniversarios" ? "active" : ""}`}
          onClick={() => setMode("aniversarios")}
        >
          Aniversarios
        </button>
      </div>

      {mode === "clientes" && (
        <form onSubmit={handleCreateCustomer} className="capture-form">
          <h2>Cadastrar Cliente</h2>

          <input
            type="text"
            placeholder="Nome completo"
            value={newCustomerForm.nome}
            onChange={(event) =>
              setNewCustomerForm({ ...newCustomerForm, nome: event.target.value })
            }
            required
            autoFocus
          />

          <input
            type="tel"
            placeholder="Telefone"
            value={newCustomerForm.telefone}
            onChange={(event) =>
              setNewCustomerForm({ ...newCustomerForm, telefone: event.target.value })
            }
            inputMode="tel"
          />

          <input
            type="email"
            placeholder="Email"
            value={newCustomerForm.email}
            onChange={(event) =>
              setNewCustomerForm({ ...newCustomerForm, email: event.target.value })
            }
            inputMode="email"
          />

          <input
            type="text"
            inputMode="numeric"
            maxLength="10"
            placeholder="Data de nascimento (dd/mm/aaaa)"
            value={newCustomerForm.data_nascimento}
            onChange={(event) =>
              setNewCustomerForm({
                ...newCustomerForm,
                data_nascimento: formatBirthdayInput(event.target.value),
              })
            }
          />

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? "Salvando..." : "Salvar Cliente"}
          </button>
        </form>
      )}

      {mode === "pontos" && (
        <div className="points-section">
          <h2>Lancar Pontos</h2>

          <div className="search-box">
            <input
              type="search"
              placeholder="Buscar cliente..."
              value={search}
              onChange={(event) => handleSearch(event.target.value)}
              autoFocus
            />
          </div>

          <div className="customers-list">
            {customers.length === 0 ? (
              <p className="empty">Nenhum cliente encontrado</p>
            ) : (
              customers.map((customer) => (
                <button
                  type="button"
                  key={customer.id}
                  className={`customer-item ${
                    selectedCustomer?.id === customer.id ? "selected" : ""
                  }`}
                  onClick={() => setSelectedCustomer(customer)}
                >
                  <div className="customer-info">
                    <h3>{customer.nome}</h3>
                    <p>{customer.telefone || "Sem telefone"}</p>
                  </div>
                  <div className="customer-points">
                    <span className="points-value">{formatPoints(customer.pontos)}</span>
                    <span className="points-label">pts</span>
                  </div>
                </button>
              ))
            )}
          </div>

          {selectedCustomer && (
            <form onSubmit={handleAddPoints} className="capture-form points-form">
              <div className="selected-customer">
                <h3>{selectedCustomer.nome}</h3>
                <p>
                  Saldo atual: <strong>{selectedCustomerBalance} pontos</strong>
                </p>
              </div>

              <input
                type="number"
                placeholder="Quantidade de pontos"
                value={pointsForm.pontos}
                onChange={(event) =>
                  setPointsForm({ ...pointsForm, pontos: event.target.value })
                }
                required
                inputMode="decimal"
                step="1"
                min="1"
              />

              <input
                type="number"
                placeholder="Valor da compra (R$)"
                value={pointsForm.valor_compra}
                onChange={(event) =>
                  setPointsForm({ ...pointsForm, valor_compra: event.target.value })
                }
                inputMode="decimal"
                step="0.01"
                min="0"
              />

              <select
                value={pointsForm.product_id}
                onChange={(event) =>
                  setPointsForm({ ...pointsForm, product_id: event.target.value })
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
                placeholder="Descricao (ex: Compra)"
                value={pointsForm.descricao}
                onChange={(event) =>
                  setPointsForm({ ...pointsForm, descricao: event.target.value })
                }
              />

              <button type="submit" disabled={loading} className="btn-primary btn-large">
                {loading ? "Processando..." : "Confirmar Pontos"}
              </button>

              <button
                type="button"
                onClick={() => setSelectedCustomer(null)}
                className="btn-secondary"
              >
                Trocar cliente
              </button>
            </form>
          )}
        </div>
      )}

      {mode === "premiados" && (
        <div className="points-section">
          <div className="section-heading-row">
            <h2>Clientes Premiados</h2>
            <button type="button" className="btn-secondary compact-button" onClick={carregarPremiados}>
              Atualizar
            </button>
          </div>

          {listLoading ? (
            <p className="empty">Carregando...</p>
          ) : premiados.length === 0 ? (
            <p className="empty">Nenhum cliente premiado no momento</p>
          ) : (
            <div className="mobile-card-list">
              {premiados.map((cliente) => (
                <article className="mobile-info-card winner-card" key={cliente.id}>
                  <div>
                    <h3>{cliente.nome}</h3>
                    <p>{cliente.telefone || "Sem telefone"}</p>
                    <strong>{formatPoints(cliente.pontos)} pontos</strong>
                  </div>
                  <button
                    type="button"
                    className="btn-primary redeem-button"
                    onClick={() => handleRedeemPrize(cliente)}
                    disabled={loading}
                  >
                    Resgatar e Zerar
                  </button>
                </article>
              ))}
            </div>
          )}

          {!listLoading && (
            <div className="near-winners-section">
              <h2>Quase Premiados</h2>
              {quasePremiados.length === 0 ? (
                <p className="empty">Nenhum cliente proximo do premio</p>
              ) : (
                <div className="mobile-card-list">
                  {quasePremiados.map((cliente) => (
                    <article className="mobile-info-card near-winner-card" key={cliente.id}>
                      <div><h3>{cliente.nome}</h3><p>{cliente.telefone || "Sem telefone"}</p></div>
                      <div className="near-winner-progress">
                        <strong>{cliente.percentual}%</strong>
                        <span>Faltam {formatPoints(cliente.falta)} pts</span>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {mode === "aniversarios" && (
        <div className="points-section">
          <div className="section-heading-row">
            <h2>Aniversariantes de Hoje</h2>
            <button type="button" className="btn-secondary compact-button" onClick={carregarAniversariantes}>
              Atualizar
            </button>
          </div>

          {listLoading ? (
            <p className="empty">Carregando...</p>
          ) : aniversariantes.length === 0 ? (
            <p className="empty">Nenhum aniversariante hoje</p>
          ) : (
            <div className="mobile-card-list">
              {aniversariantes.map((cliente) => (
                <article className="mobile-info-card" key={cliente.id}>
                  <div>
                    <h3>{cliente.nome}</h3>
                    <p>{cliente.telefone || "Sem telefone"}</p>
                  </div>
                  <strong>{cliente.data_nascimento || "Sem data"}</strong>
                </article>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
