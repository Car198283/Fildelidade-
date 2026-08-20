import { useEffect, useMemo, useState } from "react";
import { adminService } from "../services";
import "./MasterReports.css";

const reportTypes = [
  ["compras", "Compras"], ["clientes", "Clientes"], ["pontos", "Pontos"],
  ["premiacoes", "Premiações"], ["produtos", "Produtos"], ["empresas", "Empresas"], ["usuarios", "Usuários"],
];

export default function MasterReports() {
  const [companies, setCompanies] = useState([]);
  const [filters, setFilters] = useState({ report_type: "compras", company_id: "", start_date: "", end_date: "" });
  const [preview, setPreview] = useState({ columns: [], rows: [], total: 0 });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const params = useMemo(() => ({
    report_type: filters.report_type,
    company_id: filters.company_id || undefined,
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  }), [filters]);

  useEffect(() => {
    adminService.companies().then((response) => setCompanies(response.data?.data || []));
  }, []);

  const loadPreview = async () => {
    if (filters.start_date && filters.end_date && filters.start_date > filters.end_date) {
      setMessage("A data inicial deve ser anterior à data final.");
      return;
    }
    setLoading(true); setMessage("");
    try {
      const response = await adminService.reportPreview(params);
      setPreview(response.data?.data || { columns: [], rows: [], total: 0 });
    } catch (error) {
      setMessage(error.response?.data?.detail || "Não foi possível gerar a prévia.");
    } finally { setLoading(false); }
  };

  const download = async (format) => {
    setLoading(true); setMessage("");
    try {
      const response = await adminService.exportReport({ ...params, format });
      const disposition = response.headers["content-disposition"] || "";
      const match = disposition.match(/filename="?([^";]+)"?/i);
      const filename = match?.[1] || `relatorio_${filters.report_type}.${format}`;
      const url = URL.createObjectURL(response.data);
      const link = document.createElement("a"); link.href = url; link.download = filename;
      document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url);
      setMessage(`Relatório ${format.toUpperCase()} gerado com sucesso.`);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Não foi possível exportar o relatório.");
    } finally { setLoading(false); }
  };

  return <div className="master-reports-page">
    <header><h1>Central de Relatórios</h1><p>Consulte e exporte dados gerenciais de todas as empresas.</p></header>
    {message && <div className="reports-message">{message}</div>}

    <section className="reports-filters">
      <label>Tipo de relatório<select value={filters.report_type} onChange={(e) => setFilters({ ...filters, report_type: e.target.value })}>{reportTypes.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
      <label>Empresa<select value={filters.company_id} onChange={(e) => setFilters({ ...filters, company_id: e.target.value })}><option value="">Todas as empresas</option>{companies.map((company) => <option key={company.id} value={company.id}>{company.nome}</option>)}</select></label>
      <label>Data inicial<input type="date" value={filters.start_date} onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}/></label>
      <label>Data final<input type="date" value={filters.end_date} onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}/></label>
      <div className="reports-actions"><button onClick={loadPreview} disabled={loading}>Visualizar</button><button className="excel" onClick={() => download("xlsx")} disabled={loading}>Exportar Excel</button><button className="pdf" onClick={() => download("pdf")} disabled={loading}>Exportar PDF</button></div>
    </section>

    <section className="reports-preview">
      <div className="preview-heading"><h2>Prévia dos dados</h2><span>{preview.total} registro(s){preview.total > 100 ? " · exibindo os primeiros 100" : ""}</span></div>
      {!preview.rows.length ? <p className="empty-preview">Escolha os filtros e clique em Visualizar.</p> : <div className="reports-table-wrap"><table><thead><tr>{preview.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{preview.rows.map((row, index) => <tr key={index}>{preview.columns.map((column) => <td key={column}>{typeof row[column] === "boolean" ? (row[column] ? "Sim" : "Não") : String(row[column] ?? "")}</td>)}</tr>)}</tbody></table></div>}
    </section>
  </div>;
}
