import { useEffect, useMemo, useState } from "react";
import { promotionService } from "../services";
import "./PromotionConfig.css";

const initialPromotions = {
  quantidade: {
    id: null,
    tipo: "quantidade",
    title: "Por quantidade",
    subtitle: "A cada X compras, ganhe produto(s)",
    ativo: false,
    quantidade_produtos: 10,
    pontos_por_quantidade: 1,
    valor_gasto: null,
    pontos_por_valor: null,
    percentual: null,
    descricao: "A cada 10 compras, ganhe 1 produto.",
  },
  valor: {
    id: null,
    tipo: "valor",
    title: "Por valor gasto",
    subtitle: "A cada R$ X gasto, ganhe Y pontos",
    ativo: false,
    quantidade_produtos: null,
    pontos_por_quantidade: null,
    valor_gasto: 100,
    pontos_por_valor: 10,
    percentual: null,
    descricao: "A cada R$ 100 gastos, ganhe 10 pontos.",
  },
  personalizada: {
    id: null,
    tipo: "personalizada",
    title: "Personalizada",
    subtitle: "Descreva sua propria promocao",
    ativo: false,
    quantidade_produtos: null,
    pontos_por_quantidade: null,
    valor_gasto: null,
    pontos_por_valor: null,
    percentual: null,
    descricao: "Descreva sua propria promocao.",
  },
};

const promotionOrder = ["quantidade", "valor", "personalizada"];

function normalizePromotion(promocao) {
  const tipo = promocao.tipo;
  const base = initialPromotions[tipo];

  if (!base) return null;

  return {
    ...base,
    id: promocao.id,
    ativo: Boolean(promocao.ativo),
    quantidade_produtos:
      promocao.quantidade_produtos ?? base.quantidade_produtos,
    pontos_por_quantidade:
      promocao.pontos_por_quantidade ?? base.pontos_por_quantidade,
    valor_gasto: promocao.valor_gasto ?? base.valor_gasto,
    pontos_por_valor: promocao.pontos_por_valor ?? base.pontos_por_valor,
    percentual: promocao.percentual ?? base.percentual,
    descricao: promocao.descricao ?? base.descricao,
  };
}

function buildPayload(promocao) {
  return {
    tipo: promocao.tipo,
    quantidade_produtos:
      promocao.quantidade_produtos === null
        ? null
        : Number(promocao.quantidade_produtos),
    pontos_por_quantidade:
      promocao.pontos_por_quantidade === null
        ? null
        : Number(promocao.pontos_por_quantidade),
    valor_gasto:
      promocao.valor_gasto === null ? null : Number(promocao.valor_gasto),
    pontos_por_valor:
      promocao.pontos_por_valor === null
        ? null
        : Number(promocao.pontos_por_valor),
    percentual:
      promocao.percentual === null ? null : Number(promocao.percentual),
    descricao: promocao.descricao.trim(),
    ativo: promocao.ativo,
  };
}

export default function PromotionConfig() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [promotions, setPromotions] = useState(initialPromotions);
  const [statusMessage, setStatusMessage] = useState("");

  useEffect(() => {
    const carregarPromocoes = async () => {
      try {
        const response = await promotionService.listConfigs();
        const loadedPromotions = response.data.data.reduce(
          (acc, promocao) => {
            const normalized = normalizePromotion(promocao);

            if (normalized && !acc[normalized.tipo].id) {
              acc[normalized.tipo] = normalized;
            }

            return acc;
          },
          { ...initialPromotions },
        );

        setPromotions(loadedPromotions);
      } catch (err) {
        if (err.response?.status !== 404) {
          console.error("Erro ao carregar promocoes", err);
          setStatusMessage("Nao foi possivel carregar as promocoes.");
        }
      } finally {
        setLoading(false);
      }
    };

    carregarPromocoes();
  }, []);

  const activePromotions = useMemo(
    () => promotionOrder.filter((tipo) => promotions[tipo].ativo),
    [promotions],
  );

  const updatePromotion = (tipo, changes) => {
    setPromotions((current) => ({
      ...current,
      [tipo]: {
        ...current[tipo],
        ...changes,
      },
    }));
    setStatusMessage("");
  };

  const salvarPromocoes = async () => {
    const invalidPromotion = promotionOrder.find((tipo) => {
      const promocao = promotions[tipo];
      return promocao.ativo && !promocao.descricao.trim();
    });

    if (invalidPromotion) {
      alert("Preencha a descricao da promocao ativa.");
      return;
    }

    try {
      setSaving(true);
      setStatusMessage("");

      const savedPromotions = { ...promotions };

      for (const tipo of promotionOrder) {
        const promocao = savedPromotions[tipo];
        const payload = buildPayload(promocao);
        const response = promocao.id
          ? await promotionService.updateConfig(promocao.id, payload)
          : await promotionService.createConfig(payload);

        savedPromotions[tipo] = normalizePromotion(response.data.data);
      }

      setPromotions(savedPromotions);
      setStatusMessage("Promocoes salvas com sucesso.");
    } catch (err) {
      console.error("Erro ao salvar promocoes", err);
      alert(err.response?.data?.detail || "Erro ao salvar promocoes");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="loading">Carregando...</div>;

  return (
    <div className="promotion-config">
      <h1>Promocoes</h1>

      <div className="config-container">
        <div className="section">
          <div className="section-header">
            <div>
              <h2>Acoes</h2>
              <p>
                Ative uma promocao, duas ou as tres ao mesmo tempo. Todas as
                promocoes ligadas ficam valendo juntas.
              </p>
            </div>

            <button
              className="btn btn-primary"
              onClick={salvarPromocoes}
              disabled={saving}
            >
              {saving ? "Salvando..." : "Salvar promocoes"}
            </button>
          </div>

          <div className="promotion-grid">
            {promotionOrder.map((tipo) => {
              const promocao = promotions[tipo];

              return (
                <div
                  key={tipo}
                  className={`promotion-card ${promocao.ativo ? "active" : ""}`}
                >
                  <div className="promotion-card-header">
                    <div>
                      <h3>{promocao.title}</h3>
                      <p>{promocao.subtitle}</p>
                    </div>

                    <label className="switch">
                      <input
                        type="checkbox"
                        checked={promocao.ativo}
                        onChange={(e) =>
                          updatePromotion(tipo, { ativo: e.target.checked })
                        }
                      />
                      <span></span>
                    </label>
                  </div>

                  {tipo === "quantidade" && (
                    <div className="input-row compact">
                      <div className="form-field">
                        <label>Compras/produtos</label>
                        <input
                          type="number"
                          min="1"
                          value={promocao.quantidade_produtos}
                          onChange={(e) =>
                            updatePromotion(tipo, {
                              quantidade_produtos: e.target.value,
                            })
                          }
                        />
                      </div>

                      <div className="form-field">
                        <label>Produto(s) ganhos</label>
                        <input
                          type="number"
                          min="1"
                          step="1"
                          value={promocao.pontos_por_quantidade}
                          onChange={(e) =>
                            updatePromotion(tipo, {
                              pontos_por_quantidade: e.target.value,
                            })
                          }
                        />
                      </div>
                    </div>
                  )}

                  {tipo === "valor" && (
                    <div className="input-row compact">
                      <div className="form-field">
                        <label>Valor gasto (R$)</label>
                        <input
                          type="number"
                          min="1"
                          step="10"
                          value={promocao.valor_gasto}
                          onChange={(e) =>
                            updatePromotion(tipo, {
                              valor_gasto: e.target.value,
                            })
                          }
                        />
                      </div>

                      <div className="form-field">
                        <label>Pontos ganhos</label>
                        <input
                          type="number"
                          min="1"
                          step="1"
                          value={promocao.pontos_por_valor}
                          onChange={(e) =>
                            updatePromotion(tipo, {
                              pontos_por_valor: e.target.value,
                            })
                          }
                        />
                      </div>
                    </div>
                  )}

                  <div className="form-field full-width">
                    <label>Descricao</label>
                    <textarea
                      value={promocao.descricao}
                      onChange={(e) =>
                        updatePromotion(tipo, { descricao: e.target.value })
                      }
                      rows="3"
                    ></textarea>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="active-summary">
            <strong>Ativas agora:</strong>{" "}
            {activePromotions.length
              ? activePromotions
                  .map((tipo) => promotions[tipo].title.toLowerCase())
                  .join(", ")
              : "nenhuma promocao ativa"}
          </div>

          {statusMessage && <p className="status-message">{statusMessage}</p>}
        </div>

        <div className="section info">
          <h2>Como fica a regra</h2>
          <ul>
            <li>
              <strong>Promocao 1:</strong> A cada 10 compras, ou o numero que
              voce editar, o cliente ganha produto(s).
            </li>
            <li>
              <strong>Promocao 2:</strong> A cada valor gasto cadastrado, o
              cliente ganha os pontos definidos.
            </li>
            <li>
              <strong>Promocao 3:</strong> Use a descricao para cadastrar uma
              regra personalizada.
            </li>
            <li>
              <strong>Juntas:</strong> Se duas ou tres estiverem ativas, todas
              ficam valendo ao mesmo tempo.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
