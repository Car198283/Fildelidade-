import { useEffect, useMemo, useState } from "react";
import { QRCodeSVG } from "qrcode.react";
import { customerService, dashboardService, pointsService, productService } from "../services";
import API_URL, { PUBLIC_APP_URL } from "../config";
import "./MobileCapture.css";

const emptyCustomerForm = {
  nome: "",
  telefone: "",
  email: "",
  data_nascimento: "",
};

const emptyPointsForm = {
  pontos: "",
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

export default function MobileCapture() {
  const [mode, setMode] = useState("clientes");
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [premiados, setPremiados] = useState([]);
  const [aniversariantes, setAniversariantes] = useState([]);
  const [search, setSearch] = useState("");
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(false);
  const [newCustomerForm, setNewCustomerForm] = useState(emptyCustomerForm);
  const [pointsForm, setPointsForm] = useState(emptyPointsForm);
  const [message, setMessage] = useState("");
  const [registrationLink, setRegistrationLink] = useState("");
  const [linkLoading, setLinkLoading] = useState(false);

  const selectedCustomerBalance = useMemo(
    () => formatPoints(selectedCustomer?.pontos),
    [selectedCustomer],
  );

  const showMessage = (text, timeout = 3000) => {
    setMessage(text);
    if (timeout) window.setTimeout(() => setMessage(""), timeout);
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
      const response = await dashboardService.clientesPremiadosCompleto(100);
      setPremiados(Array.isArray(response.data?.data) ? response.data.data : []);
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
      const response = await dashboardService.aniversariantes(100);
      setAniversariantes(Array.isArray(response.data?.data) ? response.data.data : []);
    } catch (err) {
      console.error("Erro ao carregar aniversariantes", err);
      showMessage("Nao foi possivel carregar os aniversariantes.");
    } finally {
      setListLoading(false);
    }
  };

  useEffect(() => {
    buscarClientes();
    carregarProdutos();
  }, []);

  useEffect(() => {
    if (mode === "premiados") carregarPremiados();
    if (mode === "aniversarios") carregarAniversariantes();
  }, [mode]);

  const handleCreateCustomer = async (event) => {
    event.preventDefault();
    setLoading(true);

    try {
      const payload = {
        nome: newCustomerForm.nome.trim(),
        telefone: newCustomerForm.telefone.trim() || null,
        email: newCustomerForm.email.trim() || null,
        data_nascimento: newCustomerForm.data_nascimento || null,
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
        product_id: pointsForm.product_id ? Number(pointsForm.product_id) : null,
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

    const confirmed = window.confirm(
      `Resgatar premio de ${cliente.nome} e zerar ${formatPoints(pontos)} ponto(s)?`,
    );
    if (!confirmed) return;

    setLoading(true);
    try {
      await pointsService.moviment(cliente.id, {
        pontos,
        tipo: "saida",
        descricao: "Resgate de premio - pontuacao zerada",
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

  const handleGenerateRegistrationLink = async () => {
    setLinkLoading(true);
    try {
      const response = await customerService.createRegistrationLink();
      const token = response.data?.data?.token;
      if (!token) throw new Error("Token ausente na resposta da API");

      const appUrl = (PUBLIC_APP_URL || window.location.origin).replace(/\/$/, "");
      setRegistrationLink(`${appUrl}/cadastro-cliente?token=${encodeURIComponent(token)}`);
    } catch (err) {
      console.error("Erro ao gerar link", err);
      showMessage("Nao foi possivel gerar o link de cadastro.");
    } finally {
      setLinkLoading(false);
    }
  };

  const handleCopyRegistrationLink = async () => {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(registrationLink);
        showMessage("Link copiado. Envie-o ao cliente.", 2500);
        return;
      }
      showMessage("Selecione o link e copie manualmente.", 3500);
    } catch {
      showMessage("Nao foi possivel copiar automaticamente.", 3500);
    }
  };

  const handleSearch = (value) => {
    setSearch(value);
    buscarClientes(value);
  };

  return (
    <div className="mobile-capture">
      <div className="capture-header">
        <h1>Operacao no Celular</h1>
        <p>Clientes, pontos, premios e aniversariantes</p>
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
        <>
          <form onSubmit={handleCreateCustomer} className="capture-form">
            <h2>Capturar Cliente</h2>

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
              type="date"
              value={newCustomerForm.data_nascimento}
              onChange={(event) =>
                setNewCustomerForm({
                  ...newCustomerForm,
                  data_nascimento: event.target.value,
                })
              }
            />

            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? "Salvando..." : "Salvar Cliente"}
            </button>
          </form>

          <section className="registration-link-card">
            <div className="registration-link-copy">
              <span className="registration-link-eyebrow">CADASTRO PELO CLIENTE</span>
              <h2>Gerar link ou QR Code</h2>
              <p>Envie o link para o cliente preencher o cadastro no proprio celular.</p>
              <button
                type="button"
                className="btn-secondary generate-link-button"
                onClick={handleGenerateRegistrationLink}
                disabled={linkLoading}
              >
                {linkLoading ? "Gerando..." : "Gerar link e QR Code"}
              </button>
            </div>

            {registrationLink && (
              <div className="registration-link-result">
                <QRCodeSVG value={registrationLink} size={156} level="M" includeMargin />
                <div className="registration-link-actions">
                  <input
                    value={registrationLink}
                    readOnly
                    aria-label="Link de cadastro do cliente"
                    onFocus={(event) => event.target.select()}
                  />
                  <button type="button" className="btn-primary" onClick={handleCopyRegistrationLink}>
                    Copiar link
                  </button>
                  <small>O link expira em 30 dias.</small>
                </div>
              </div>
            )}
          </section>
        </>
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
        </div>
      )}

      {mode === "aniversarios" && (
        <div className="points-section">
          <div className="section-heading-row">
            <h2>Aniversariantes</h2>
            <button type="button" className="btn-secondary compact-button" onClick={carregarAniversariantes}>
              Atualizar
            </button>
          </div>

          {listLoading ? (
            <p className="empty">Carregando...</p>
          ) : aniversariantes.length === 0 ? (
            <p className="empty">Nenhum aniversariante encontrado</p>
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
