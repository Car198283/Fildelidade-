import { useState, useEffect } from "react";
import { productService } from "../services";
import "./Products.css";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [importProgress, setImportProgress] = useState("");

  useEffect(() => {
    fetchProducts();
  }, [page, search]);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const response = await productService.list(page, 50, search);
      setProducts(response.data.data);
      setTotal(response.data.total);
    } catch (err) {
      console.error("Erro ao buscar produtos", err);
    } finally {
      setLoading(false);
    }
  };

  const handleImportExcel = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImportProgress("Processando arquivo...");

    try {
      const response = await productService.importExcel(file);
      const result = response.data.data;

      setImportProgress(
        `✅ Importação concluída!\nImportados: ${result.importados}\nAtualizados: ${result.atualizados}`,
      );

      setTimeout(() => setImportProgress(""), 3000);
      fetchProducts();
    } catch (err) {
      const errors = err.response?.data?.erros || ["Erro ao importar"];
      setImportProgress(`❌ Erro:\n${errors.join("\n")}`);
      setTimeout(() => setImportProgress(""), 5000);
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const { data: blob } = await productService.downloadTemplate();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "produto_template.xlsx";
      a.click();
    } catch (err) {
      console.error("Erro ao baixar template", err);
    }
  };

  const handleExportExcel = async () => {
    try {
      const { data: blob } = await productService.exportExcel();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "produtos_export.xlsx";
      a.click();
    } catch (err) {
      console.error("Erro ao exportar", err);
    }
  };

  return (
    <div className="products">
      <h1>📦 Gestão de Produtos</h1>

      <div className="excel-controls">
        <button className="btn-secondary" onClick={handleDownloadTemplate}>
          📥 Baixar Modelo Excel
        </button>

        <label className="btn-primary">
          📤 Importar Excel
          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={handleImportExcel}
            style={{ display: "none" }}
          />
        </label>

        <button className="btn-secondary" onClick={handleExportExcel}>
          💾 Exportar Excel
        </button>
      </div>

      {importProgress && (
        <div className="progress-message">
          {importProgress.split("\n").map((line, idx) => (
            <div key={idx}>{line}</div>
          ))}
        </div>
      )}

      <div className="search-box">
        <input
          type="text"
          placeholder="🔍 Buscar produtos..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
      </div>

      {loading ? (
        <div className="loading">Carregando...</div>
      ) : (
        <>
          <table className="products-table">
            <thead>
              <tr>
                <th>Nome</th>
                <th>Categoria</th>
                <th>Preço</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td>{product.nome}</td>
                  <td>{product.categoria || "-"}</td>
                  <td className="price">R$ {product.preco.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="pagination">
            <p>
              Mostrando {products.length} de {total} produtos
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
                disabled={products.length < 50}
              >
                Próximo →
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
