import { useEffect, useMemo, useState } from "react";
import { promotionService } from "../services";
import "./PromotionConfig.css";

const common = {
  id: null, ativo: false, nome: "", data_inicio: "", data_fim: "", acumulavel: true,
  prioridade: 0, limite_por_cliente: "", limite_total: "", valor_minimo_compra: 0,
  recompensa_tipo: "pontos", recompensa_valor: "", motivo_alteracao: "Configuracao inicial",
  condicao_campo: "", condicao_operador: "", condicao_valor: "",
};
const initialPromotions = {
  quantidade: { ...common, tipo: "quantidade", title: "Por quantidade", subtitle: "A cada X compras, ganhe Y pontos", quantidade_produtos: 10, pontos_por_quantidade: 1, valor_gasto: null, pontos_por_valor: null, percentual: null, descricao: "A cada 10 compras, ganhe 1 ponto." },
  valor: { ...common, tipo: "valor", title: "Por valor gasto", subtitle: "A cada R$ X gastos, ganhe Y pontos", quantidade_produtos: null, pontos_por_quantidade: null, valor_gasto: 100, pontos_por_valor: 10, percentual: null, descricao: "A cada R$ 100 gastos, ganhe 10 pontos." },
  personalizada: { ...common, tipo: "personalizada", title: "Personalizada", subtitle: "Monte uma condicao especial", quantidade_produtos: null, pontos_por_quantidade: null, valor_gasto: null, pontos_por_valor: null, percentual: null, descricao: "Campanha especial para clientes elegiveis.", condicao_campo: "valor_compra", condicao_operador: ">=", condicao_valor: 100 },
};
const promotionOrder = ["quantidade", "valor", "personalizada"];
const numberOrNull = (value) => value === "" || value == null ? null : Number(value);
const localDate = (value) => value ? String(value).slice(0, 16) : "";

function normalizePromotion(item) {
  const base = initialPromotions[item.tipo];
  if (!base) return null;
  return {
    ...base, ...item,
    nome: item.nome ?? base.nome,
    condicao_campo: item.condicao_campo ?? base.condicao_campo,
    condicao_operador: item.condicao_operador ?? base.condicao_operador,
    condicao_valor: item.condicao_valor ?? base.condicao_valor,
    data_inicio: localDate(item.data_inicio), data_fim: localDate(item.data_fim),
    motivo_alteracao: "Atualizacao da campanha",
  };
}
function buildPayload(item) {
  return {
    tipo: item.tipo, ativo: item.ativo, nome: item.nome || item.title,
    quantidade_produtos: numberOrNull(item.quantidade_produtos), pontos_por_quantidade: numberOrNull(item.pontos_por_quantidade),
    valor_gasto: numberOrNull(item.valor_gasto), pontos_por_valor: numberOrNull(item.pontos_por_valor), percentual: numberOrNull(item.percentual),
    descricao: item.descricao.trim(), data_inicio: item.data_inicio || null, data_fim: item.data_fim || null,
    acumulavel: item.acumulavel, prioridade: Number(item.prioridade || 0), limite_por_cliente: numberOrNull(item.limite_por_cliente),
    limite_total: numberOrNull(item.limite_total), valor_minimo_compra: numberOrNull(item.valor_minimo_compra),
    recompensa_tipo: item.recompensa_tipo, recompensa_valor: numberOrNull(item.recompensa_valor),
    condicao_campo: item.condicao_campo || null, condicao_operador: item.condicao_operador || null,
    condicao_valor: numberOrNull(item.condicao_valor), produtos_elegiveis: null, categorias_elegiveis: null,
    motivo_alteracao: item.motivo_alteracao.trim(),
  };
}

export default function PromotionConfig() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [promotions, setPromotions] = useState(initialPromotions);
  const [history, setHistory] = useState([]);
  const [statusMessage, setStatusMessage] = useState("");
  const [simulation, setSimulation] = useState({ compras: 10, valor_compra: 100 });
  const [simulationResult, setSimulationResult] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [configs, audit] = await Promise.all([promotionService.listConfigs(), promotionService.history()]);
        const loaded = configs.data.data.reduce((acc, item) => {
          const normalized = normalizePromotion(item);
          if (normalized && !acc[normalized.tipo].id) acc[normalized.tipo] = normalized;
          return acc;
        }, structuredClone(initialPromotions));
        setPromotions(loaded); setHistory(audit.data.data || []);
      } catch (err) { console.error(err); setStatusMessage("Nao foi possivel carregar todos os dados de promocoes."); }
      finally { setLoading(false); }
    };
    loadData();
  }, []);

  const activePromotions = useMemo(() => promotionOrder.filter((tipo) => promotions[tipo].ativo), [promotions]);
  const updatePromotion = (tipo, changes) => { setPromotions((current) => ({ ...current, [tipo]: { ...current[tipo], ...changes } })); setStatusMessage(""); };
  const applyTemplate = (template) => {
    const templates = {
      retorno: ["quantidade", { nome: "Volte 10 vezes", quantidade_produtos: 10, pontos_por_quantidade: 1, descricao: "A cada 10 compras, ganhe 1 ponto.", ativo: true }],
      ticket: ["valor", { nome: "Bonus por valor", valor_gasto: 100, pontos_por_valor: 10, descricao: "A cada R$ 100 gastos, ganhe 10 pontos.", ativo: true }],
      vip: ["personalizada", { nome: "Cliente VIP", condicao_campo: "valor_compra", condicao_operador: ">=", condicao_valor: 300, descricao: "Beneficio especial em compras a partir de R$ 300.", recompensa_valor: 30, ativo: true }],
    };
    const [tipo, values] = templates[template]; updatePromotion(tipo, values);
  };
  const salvarPromocoes = async () => {
    const invalid = promotionOrder.find((tipo) => promotions[tipo].ativo && (!promotions[tipo].descricao.trim() || !promotions[tipo].motivo_alteracao.trim()));
    if (invalid) return alert("Preencha a descricao e o motivo da alteracao das promocoes ativas.");
    const summary = activePromotions.map((tipo) => promotions[tipo].nome || promotions[tipo].title).join(", ") || "nenhuma";
    if (!window.confirm(`Confirma salvar? Promocoes ativas: ${summary}.`)) return;
    try {
      setSaving(true); const saved = { ...promotions };
      for (const tipo of promotionOrder) {
        const item = saved[tipo]; const payload = buildPayload(item);
        const response = item.id ? await promotionService.updateConfig(item.id, payload) : await promotionService.createConfig(payload);
        saved[tipo] = normalizePromotion(response.data.data);
      }
      setPromotions(saved); setStatusMessage("Promocoes salvas e registradas no historico.");
      const audit = await promotionService.history(); setHistory(audit.data.data || []);
    } catch (err) { console.error(err); alert(err.response?.data?.detail || "Erro ao salvar promocoes"); }
    finally { setSaving(false); }
  };
  const simulate = async () => {
    try { const response = await promotionService.simulate({ compras: Number(simulation.compras), valor_compra: Number(simulation.valor_compra) }); setSimulationResult(response.data.data); }
    catch (err) { alert(err.response?.data?.detail || "Nao foi possivel simular."); }
  };
  if (loading) return <div className="loading">Carregando...</div>;

  return <div className="promotion-config">
    <h1>Promocoes</h1>
    <div className="template-bar"><div><strong>Modelos rapidos</strong><span> Comece com uma regra pronta e personalize.</span></div><div><button onClick={() => applyTemplate("retorno")}>Frequencia</button><button onClick={() => applyTemplate("ticket")}>Valor gasto</button><button onClick={() => applyTemplate("vip")}>Cliente VIP</button></div></div>
    <div className="config-container">
      <section className="section">
        <div className="section-header"><div><h2>Regras da campanha</h2><p>Defina vigencia, limites e prioridade. Regras nao acumulaveis interrompem as seguintes.</p></div><button className="btn btn-primary" onClick={salvarPromocoes} disabled={saving}>{saving ? "Salvando..." : "Revisar e salvar"}</button></div>
        <div className="promotion-grid">
          {promotionOrder.map((tipo) => { const p = promotions[tipo]; return <article key={tipo} className={`promotion-card ${p.ativo ? "active" : ""}`}>
            <div className="promotion-card-header"><div><h3>{p.title}</h3><p>{p.subtitle}</p></div><label className="switch"><input type="checkbox" checked={p.ativo} onChange={(e) => updatePromotion(tipo, { ativo: e.target.checked })}/><span /></label></div>
            <Field label="Nome da campanha" value={p.nome} onChange={(v) => updatePromotion(tipo, { nome: v })}/>
            {tipo === "quantidade" && <div className="input-row compact"><Field label="Numero de compras" type="number" value={p.quantidade_produtos} onChange={(v) => updatePromotion(tipo, { quantidade_produtos: v })}/><Field label="Pontos ganhos" type="number" value={p.pontos_por_quantidade} onChange={(v) => updatePromotion(tipo, { pontos_por_quantidade: v })}/></div>}
            {tipo === "valor" && <div className="input-row compact"><Field label="A cada valor (R$)" type="number" value={p.valor_gasto} onChange={(v) => updatePromotion(tipo, { valor_gasto: v })}/><Field label="Pontos ganhos" type="number" value={p.pontos_por_valor} onChange={(v) => updatePromotion(tipo, { pontos_por_valor: v })}/></div>}
            {tipo === "personalizada" && <div className="input-row compact"><SelectField label="Quando" value={p.condicao_campo} onChange={(v) => updatePromotion(tipo, { condicao_campo: v })} options={[["valor_compra","Valor da compra"],["quantidade_compras","Quantidade de compras"]]}/><SelectField label="Operador" value={p.condicao_operador} onChange={(v) => updatePromotion(tipo, { condicao_operador: v })} options={[[">=","Maior ou igual"],["=","Igual"],["<=","Menor ou igual"]]}/><Field label="Valor" type="number" value={p.condicao_valor} onChange={(v) => updatePromotion(tipo, { condicao_valor: v })}/></div>}
            <Field label="Descricao para a equipe" textarea value={p.descricao} onChange={(v) => updatePromotion(tipo, { descricao: v })}/>
            <details><summary>Vigencia, limites e controle</summary><div className="advanced-grid">
              <Field label="Inicio" type="datetime-local" value={p.data_inicio} onChange={(v) => updatePromotion(tipo, { data_inicio: v })}/><Field label="Fim" type="datetime-local" value={p.data_fim} onChange={(v) => updatePromotion(tipo, { data_fim: v })}/>
              <Field label="Compra minima (R$)" type="number" value={p.valor_minimo_compra} onChange={(v) => updatePromotion(tipo, { valor_minimo_compra: v })}/><Field label="Prioridade" type="number" value={p.prioridade} onChange={(v) => updatePromotion(tipo, { prioridade: v })}/>
              <Field label="Limite por cliente" type="number" value={p.limite_por_cliente} onChange={(v) => updatePromotion(tipo, { limite_por_cliente: v })}/><Field label="Limite total" type="number" value={p.limite_total} onChange={(v) => updatePromotion(tipo, { limite_total: v })}/>
              <label className="check-field"><input type="checkbox" checked={p.acumulavel} onChange={(e) => updatePromotion(tipo, { acumulavel: e.target.checked })}/> Pode acumular com outras regras</label>
            </div></details>
            <Field label="Motivo da alteracao (auditoria)" value={p.motivo_alteracao} onChange={(v) => updatePromotion(tipo, { motivo_alteracao: v })}/>
          </article>; })}
        </div>
        <div className="active-summary"><strong>Ativas agora:</strong> {activePromotions.length ? activePromotions.map((t) => promotions[t].nome || promotions[t].title).join(", ") : "nenhuma promocao ativa"}</div>
        {statusMessage && <p className="status-message">{statusMessage}</p>}
      </section>
      <section className="section two-columns"><div><h2>Simulador antes de publicar</h2><div className="input-row"><Field label="Compras do cliente" type="number" value={simulation.compras} onChange={(v) => setSimulation({ ...simulation, compras: v })}/><Field label="Valor da compra (R$)" type="number" value={simulation.valor_compra} onChange={(v) => setSimulation({ ...simulation, valor_compra: v })}/><button className="btn btn-secondary" onClick={simulate}>Simular regras salvas</button></div>{simulationResult && <div className="simulation-result"><strong>Resultado: {simulationResult.pontos_totais} ponto(s)</strong>{simulationResult.regras.map((r) => <span key={r.id}>{r.nome}: {r.pontos}</span>)}</div>}</div>
        <div><h2>Historico recente</h2>{history.length ? <ul className="history-list">{history.slice(0, 6).map((item) => <li key={item.id}><strong>{item.acao}</strong> da promocao #{item.promotion_id}<span>{item.motivo} · {new Date(item.created_at).toLocaleString("pt-BR")}</span></li>)}</ul> : <p className="empty-state">O historico aparecera depois do primeiro salvamento.</p>}</div></section>
      <section className="section info"><h2>Como as regras funcionam</h2><ul><li><strong>Quantidade:</strong> premia a frequencia de compras do cliente.</li><li><strong>Valor:</strong> transforma faixas de gasto em pontos.</li><li><strong>Personalizada:</strong> registra condicoes especiais de campanha.</li><li><strong>Seguranca:</strong> todas as mudancas guardam usuario, empresa, data e motivo.</li></ul></section>
    </div>
  </div>;
}

function Field({ label, value, onChange, type = "text", textarea = false }) { return <div className="form-field"><label>{label}</label>{textarea ? <textarea rows="3" value={value ?? ""} onChange={(e) => onChange(e.target.value)}/> : <input type={type} min={type === "number" ? "0" : undefined} step={type === "number" ? "any" : undefined} value={value ?? ""} onChange={(e) => onChange(e.target.value)}/>}</div>; }
function SelectField({ label, value, onChange, options }) { return <div className="form-field"><label>{label}</label><select value={value ?? ""} onChange={(e) => onChange(e.target.value)}>{options.map(([key, text]) => <option key={key} value={key}>{text}</option>)}</select></div>; }
