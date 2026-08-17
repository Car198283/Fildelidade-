import { useEffect, useMemo, useState } from "react";
import { integrationService } from "../services";
import "./WhatsAppIntegration.css";

const templates = {
  aniversario: "Ola {nome}! Feliz aniversario! A equipe deseja um excelente dia para voce.",
  premio: "Ola {nome}! Voce ja possui {pontos} pontos e tem um premio esperando por voce.",
  manual: "Ola {nome}! Temos uma novidade especial para voce.",
};

export default function WhatsAppIntegration() {
  const [form, setForm] = useState({ tipo: "aniversario", mensagem_template: templates.aniversario, customer_id: "", scheduled_at: "", max_attempts: 3 });
  const [queue, setQueue] = useState([]);
  const [filter, setFilter] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => { const response = await integrationService.whatsappQueue(filter); setQueue(response.data.data || []); };
  useEffect(() => { load().catch(() => setMessage("Nao foi possivel carregar a fila.")); }, [filter]);
  const metrics = useMemo(() => queue.reduce((acc, item) => { acc[item.status] = (acc[item.status] || 0) + 1; return acc; }, {}), [queue]);

  const changeType = (tipo) => setForm({ ...form, tipo, mensagem_template: templates[tipo] });
  const generate = async (event) => {
    event.preventDefault();
    if (!window.confirm("Confirma gerar esta campanha? Repetir a mesma chave nao duplicara mensagens.")) return;
    try {
      setLoading(true); setMessage("");
      const key = `${form.tipo}-${form.scheduled_at || new Date().toISOString().slice(0, 10)}-${form.customer_id || "todos"}`;
      const response = await integrationService.generateWhatsAppQueue({ ...form, customer_id: form.customer_id ? Number(form.customer_id) : null, scheduled_at: form.scheduled_at || null, max_attempts: Number(form.max_attempts) }, key);
      setMessage(`${response.data.total} mensagem(ns) preparada(s).`); await load();
    } catch (error) { setMessage(error.response?.data?.detail || "Nao foi possivel gerar a campanha."); }
    finally { setLoading(false); }
  };

  return <div className="whatsapp-page"><header><h1>WhatsApp e n8n</h1><p>Prepare campanhas, acompanhe tentativas e deixe o n8n realizar os envios.</p></header>{message && <div className="whatsapp-message">{message}</div>}
    <section className="whatsapp-metrics">{[["Pendentes", metrics.pendente],["Processando", metrics.processando],["Enviadas", metrics.enviado],["Erros", metrics.erro]].map(([label, value]) => <article key={label}><span>{label}</span><strong>{value || 0}</strong></article>)}</section>
    <section className="whatsapp-panel"><h2>Nova campanha</h2><form onSubmit={generate}><label>Publico<select value={form.tipo} onChange={(e) => changeType(e.target.value)}><option value="aniversario">Aniversariantes</option><option value="premio">Clientes premiados</option><option value="manual">Todos ou cliente especifico</option></select></label><label>ID do cliente (opcional)<input type="number" min="1" value={form.customer_id} onChange={(e) => setForm({ ...form, customer_id: e.target.value })}/></label><label>Agendar para<input type="datetime-local" value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })}/></label><label>Maximo de tentativas<input type="number" min="1" max="10" value={form.max_attempts} onChange={(e) => setForm({ ...form, max_attempts: e.target.value })}/></label><label className="message-field">Mensagem<textarea rows="4" value={form.mensagem_template} onChange={(e) => setForm({ ...form, mensagem_template: e.target.value })} required/><small>Variaveis permitidas: {'{nome}'}, {'{telefone}'} e {'{pontos}'}.</small></label><button disabled={loading}>{loading ? "Gerando..." : "Gerar fila segura"}</button></form></section>
    <section className="whatsapp-panel"><div className="queue-header"><h2>Fila de mensagens</h2><select value={filter} onChange={(e) => setFilter(e.target.value)}><option value="">Todos os status</option><option value="pendente">Pendentes</option><option value="processando">Processando</option><option value="enviado">Enviadas</option><option value="erro">Erros definitivos</option></select></div><div className="queue-list">{queue.map((item) => <article key={item.id}><div><strong>{item.cliente_nome || item.telefone}</strong><span>{item.telefone} · {item.tipo}</span><small>{item.mensagem}</small></div><div><b className={`queue-status status-${item.status}`}>{item.status}</b><span>Tentativa {item.attempts}/{item.max_attempts}</span>{item.erro && <small>{item.erro}</small>}</div></article>)}{!queue.length && <p>Nenhuma mensagem encontrada.</p>}</div></section>
  </div>;
}
