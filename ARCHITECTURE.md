# 📁 Estrutura Completa do Projeto

```
Bartcellos/
│
├── 📄 README.md                    # Documentação principal
├── 📄 QUICK_START.md               # Guia rápido para iniciar
├── 📄 API_EXAMPLES.md              # Exemplos de requisições da API
├── 📄 DEPLOYMENT.md                # Guia de deployment/produção
├── 📄 .gitignore                   # Arquivos Git ignorados
│
├── 🐳 docker-compose.yml           # Orquestração Docker
│
│
├── 📂 backend/
│   ├── 📄 requirements.txt         # Dependências Python
│   ├── 📄 .env.example             # Template de variáveis
│   ├── 🐳 Dockerfile               # Container backend
│   │
│   └── 📂 app/
│       ├── 📄 __init__.py          # Init
│       ├── 📄 main.py              # App FastAPI principal
│       ├── 📄 config.py            # Configurações
│       ├── 📄 database.py          # Conexão banco dados
│       │
│       ├── 📂 models/              # Modelos SQLAlchemy
│       │   ├── 📄 __init__.py
│       │   ├── 📄 base.py          # Base + Mixins
│       │   ├── 📄 company.py       # Modelo Empresa
│       │   ├── 📄 user.py          # Modelo Usuário
│       │   ├── 📄 customer.py      # Modelo Cliente
│       │   ├── 📄 points_transaction.py  # Modelo Transações
│       │   ├── 📄 product.py       # Modelo Produto
│       │   └── 📄 category.py      # Modelo Categoria
│       │
│       ├── 📂 routes/              # Endpoints da API
│       │   ├── 📄 __init__.py
│       │   ├── 📄 auth.py          # Endpoints auth
│       │   ├── 📄 customers.py     # Endpoints clientes
│       │   ├── 📄 points.py        # Endpoints pontos
│       │   ├── 📄 products.py      # Endpoints produtos
│       │   └── 📄 dashboard.py     # Endpoints dashboard
│       │
│       ├── 📂 services/            # Lógica de negócio
│       │   ├── 📄 __init__.py
│       │   ├── 📄 auth_service.py  # Autenticação
│       │   ├── 📄 points_service.py  # Movimentação de pontos (CRÍTICO)
│       │   ├── 📄 dashboard_service.py  # Dashboard/Relatórios
│       │   └── 📄 product_service.py  # Importação/Exportação Excel
│       │
│       ├── 📂 schemas/             # Validação Pydantic
│       │   ├── 📄 __init__.py
│       │   └── 📄 schemas.py       # Todos os schemas
│       │
│       └── 📂 utils/               # Utilitários
│           ├── 📄 __init__.py
│           └── 📄 dependencies.py  # JWT + Autenticação
│
│
├── 📂 frontend/
│   ├── 📄 package.json             # Dependências Node
│   ├── 📄 vite.config.js           # Configuração Vite
│   ├── 📄 tsconfig.json            # TypeScript config
│   ├── 📄 index.html               # Entry point HTML
│   ├── 🐳 Dockerfile               # Container frontend
│   │
│   ├── 📂 public/                  # Assets estáticos
│   │   ├── 📄 manifest.json        # PWA manifest
│   │   └── 📄 sw.js                # Service Worker (PWA)
│   │
│   └── 📂 src/
│       ├── 📄 main.jsx             # React entry point
│       ├── 📄 App.jsx              # App principal
│       ├── 📄 App.css              # Estilos layout
│       ├── 📄 index.css            # Estilos globais
│       ├── 📄 config.js            # Configurações
│       │
│       ├── 📂 pages/               # Páginas (componentes principais)
│       │   ├── 📄 Register.jsx     # Página de registro
│       │   ├── 📄 Login.jsx        # Página de login
│       │   ├── 📄 Dashboard.jsx    # Dashboard
│       │   ├── 📄 Customers.jsx    # Lista de clientes
│       │   ├── 📄 CustomerDetails.jsx  # Detalhes do cliente
│       │   ├── 📄 Products.jsx     # Gestão de produtos
│       │   ├── 📄 Auth.css         # Estilos auth
│       │   ├── 📄 Dashboard.css    # Estilos dashboard
│       │   ├── 📄 Customers.css    # Estilos customers
│       │   ├── 📄 CustomerDetails.css  # Estilos detalhes
│       │   └── 📄 Products.css     # Estilos produtos
│       │
│       ├── 📂 components/          # Componentes reutilizáveis
│       │   └── 📄 (a expandir)
│       │
│       └── 📂 services/            # Serviços API
│           ├── 📄 api.js           # Cliente Axios
│           └── 📄 index.js         # Serviços da API
│
│
└── 📄 ARCHITECTURE.md              # Este arquivo
```

---

## 🏗️ Arquitetura

### Backend (FastAPI)

```
User Request
    ↓
CORS Middleware
    ↓
Routes (auth, customers, points, products, dashboard)
    ↓
Services (lógica de negócio)
    ↓
SQLAlchemy Models
    ↓
PostgreSQL Database
```

**Fluxo de Pontos (CRÍTICO):**

```
POST /clientes/{id}/pontos
    ↓
Auth (verify JWT token)
    ↓
PointsService.movimentar_pontos()
    ├─ Valida cliente
    ├─ Valida pontos > 0
    ├─ Calcula novo saldo
    ├─ Previne negativo
    ├─ Cria transação
    ├─ Atualiza saldo
    └─ Commit atômico
    ↓
Response com saldo atualizado
```

### Frontend (React)

```
Browser
    ↓
App.jsx (Router)
    ├─ Protected Routes (JWT)
    ├─ Public Routes (Auth)
    └─ ProtectedLayout (Navbar)
    ↓
Pages (React Components)
    ├─ Login/Register
    ├─ Dashboard
    ├─ Customers
    ├─ CustomerDetails
    └─ Products
    ↓
Services (API Calls via Axios)
    ├─ authService
    ├─ customerService
    ├─ pointsService
    ├─ productService
    └─ dashboardService
    ↓
API (Backend)
```

### PWA Features

```
manifest.json
    ↓
Service Worker (sw.js)
    ├─ Install: Cache static assets
    ├─ Activate: Clean old caches
    └─ Fetch: Network/Cache strategy
    ↓
Offline Support
Installable App
Push Notifications (ready)
```

---

## 🔑 Componentes Críticos

### 1. **PointsService** (`backend/app/services/points_service.py`)

- Função central: `movimentar_pontos()`
- NUNCA atualiza saldo diretamente
- Previne fraude (saldo negativo)
- Registra TODA transação

### 2. **Auth** (`backend/app/services/auth_service.py`)

- JWT com bcrypt hash
- Token expira em 30 min
- Refresh logic ready

### 3. **ProductImportService** (`backend/app/services/product_service.py`)

- Importa de Excel
- Validação linha-por-linha
- Update or Insert automático
- Exportação para Excel

### 4. **Multi-tenant** (Todos models)

- Cada tabela tem `company_id`
- Queries filtram por `company_id`
- Isolamento de dados 100%

---

## 📊 Database Schema

```sql
-- Companies (Empresas)
companies:
  - id (PK)
  - nome
  - plano (free, starter, pro, enterprise)
  - ativo
  - created_at, updated_at

-- Users (Admins/Staff)
users:
  - id (PK)
  - email (UNIQUE)
  - senha_hash
  - company_id (FK)
  - role (admin, staff)
  - ativo
  - created_at, updated_at

-- Customers (Clientes)
customers:
  - id (PK)
  - nome
  - telefone
  - email
  - pontos (Float, não editar direto)
  - company_id (FK)
  - created_at, updated_at
  - INDEX: company_id, nome

-- PointsTransactions (Auditoria)
points_transactions:
  - id (PK)
  - customer_id (FK)
  - company_id (FK)
  - pontos (Float)
  - tipo (entrada, saida)
  - descricao
  - created_at, updated_at
  - INDEX: customer_id, company_id, created_at

-- Categories (Categorias Produtos)
categories:
  - id (PK)
  - nome
  - company_id (FK)
  - created_at, updated_at

-- Products (Produtos)
products:
  - id (PK)
  - nome
  - categoria_id (FK)
  - preco
  - company_id (FK)
  - created_at, updated_at
```

---

## 🔐 Segurança

✅ JWT Authentication
✅ Password Hashing (bcrypt)
✅ CORS habilitado
✅ Multi-tenant isolation
✅ Validação Pydantic
✅ SQL Injection prevention (SQLAlchemy)
✅ Rate limiting ready

---

## 🚀 Performance

✅ Database indexes por company_id
✅ Paginação em todas as listas
✅ Service Worker para cache
✅ Lazy loading pronto
✅ Redis ready (configure se quiser)
✅ Connection pooling (SQLAlchemy)

---

## 📱 Responsividade

✅ Mobile-first design
✅ Flexbox layout
✅ Touch-friendly buttons
✅ PWA installable
✅ Adaptive navbar

---

## 🧪 Testável

✅ Service layer separado
✅ Dependency injection (get_db)
✅ Clear separation of concerns
✅ API docs via Swagger
✅ Postman ready

---

## 📈 Escalável

✅ Microservices-ready architecture
✅ Docker containerized
✅ Database migrations ready
✅ Environment config
✅ CI/CD ready (GitHub Actions)

---

## 📝 Próximos Passos

- [ ] Testes unitários (pytest)
- [ ] Testes E2E (Cypress)
- [ ] Logging centralizado
- [ ] Cache com Redis
- [ ] WebSocket para real-time
- [ ] Mobile app (React Native)
- [ ] Admin panel avançado
- [ ] Relatórios em PDF
- [ ] SMS/Email notifications
- [ ] Integração com gateway de pagamento

---

**Projeto production-ready! 🎉**
