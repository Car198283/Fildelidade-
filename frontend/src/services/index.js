import api from "./api";

// ========== AUTH ==========

export const authService = {
  register: (companyName, email, password) =>
    api.post("/auth/register", {
      company_name: companyName,
      email,
      senha: password,
    }),

  login: (email, password) =>
    api.post("/auth/login", { email, senha: password }),
};

export const adminService = {
  me: () => api.get("/admin/me"),

  companies: () => api.get("/admin/companies"),

  updateCompany: (id, data) => api.put(`/admin/companies/${id}`, data),

  users: (companyId = null) =>
    api.get("/admin/users", { params: { company_id: companyId } }),

  createUser: (data) => api.post("/admin/users", data),

  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
};

// ========== CUSTOMERS ==========

export const customerService = {
  list: (page = 1, limit = 50, search = "") =>
    api.get("/clientes", { params: { page, limit, search } }),

  get: (id) => api.get(`/clientes/${id}`),

  getDetalhes: (id) => api.get(`/clientes/${id}/detalhes`),

  create: (data) => api.post("/clientes", data),

  createRegistrationLink: () => api.post("/clientes/registro-link"),

  publicRegistration: (data) => api.post("/clientes/cadastro-publico", data),

  update: (id, data) => api.put(`/clientes/${id}`, data),

  delete: (id) => api.delete(`/clientes/${id}`),
};

// ========== POINTS ==========

export const pointsService = {
  moviment: (customerId, data) =>
    api.post(`/clientes/${customerId}/pontos`, data),

  history: (customerId, page = 1, limit = 50) =>
    api.get(`/clientes/${customerId}/pontos/historico`, {
      params: { page, limit },
    }),
};

// ========== PRODUCTS ==========

export const productService = {
  list: (page = 1, limit = 50, search = "", categoriaId = null) =>
    api.get("/produtos", {
      params: { page, limit, search, categoria_id: categoriaId },
    }),

  get: (id) => api.get(`/produtos/${id}`),

  create: (data) => api.post("/produtos", data),

  update: (id, data) => api.put(`/produtos/${id}`, data),

  delete: (id) => api.delete(`/produtos/${id}`),

  importExcel: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post("/produtos/importar-excel", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  downloadTemplate: () =>
    api.get("/produtos/template-excel", { responseType: "blob" }),

  exportExcel: () =>
    api.get("/produtos/exportar-excel", { responseType: "blob" }),
};

// ========== PROMOTIONS ==========

export const promotionService = {
  getConfig: () => api.get("/promocoes/config"),

  listConfigs: () => api.get("/promocoes/configs"),

  createConfig: (data) => api.post("/promocoes/config", data),

  updateConfig: (id, data) => api.put(`/promocoes/config/${id}`, data),
};

// ========== DASHBOARD ==========

export const dashboardService = {
  stats: () => api.get("/dashboard/stats"),

  topCustomers: (limit = 10) =>
    api.get("/dashboard/top-customers", { params: { limit } }),

  topProducts: (limit = 10) =>
    api.get("/dashboard/produtos-mais-vendidos", { params: { limit } }),

  customerConsumedProducts: (customerId, limit = 50) =>
    api.get(`/dashboard/clientes/${customerId}/produtos-consumidos`, {
      params: { limit },
    }),

  clientesPremiadosCompleto: (limit = 50) =>
    api.get("/dashboard/clientes-premiados-completo", { params: { limit } }),

  aniversariantes: (limit = 50, mes = null) =>
    api.get("/dashboard/aniversariantes", { params: { limit, mes } }),

  aniversariantesDia: (limit = 50) =>
    api.get("/dashboard/aniversariantes-dia", { params: { limit } }),

  clientesQuasePremiados: (
    limit = 50,
    percentualMin = 80,
    percentualMax = 99.9,
  ) =>
    api.get("/dashboard/clientes-quase-premiados", {
      params: {
        limit,
        percentual_min: percentualMin,
        percentual_max: percentualMax,
      },
    }),

  downloadAniversariantesPdf: () =>
    api.get("/dashboard/relatorio-pdf-aniversariantes", {
      responseType: "blob",
    }),

  downloadPremiadosPdf: () =>
    api.get("/dashboard/relatorio-pdf-premiados", {
      responseType: "blob",
    }),

  downloadInativosPdf: () =>
    api.get("/dashboard/relatorio-pdf-inativos", {
      responseType: "blob",
    }),
};
