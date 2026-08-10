# 🎯 Bartcellos Loyalty - Sistema de Fidelização com Pontos

Plataforma SaaS production-ready para gerenciamento de pontos e fidelização de clientes.

## 📋 Índice

- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Rodando a Aplicação](#rodando-a-aplicação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)

---

## 🔧 Pré-requisitos

Certifique-se de ter instalado:

- **Python 3.11+** → [Download](https://www.python.org/downloads/)
- **PostgreSQL 13+** → [Download](https://www.postgresql.org/download/)
- **Node.js 18+** → [Download](https://nodejs.org/)
- **Git** → [Download](https://git-scm.com/)

### Verificar Instalações

```bash
# Python
python --version

# PostgreSQL
psql --version

# Node.js
node --version
npm --version
```

---

## 📦 Instalação

### 1. Clone o Repositório

```bash
cd c:\Users\caduf\OneDrive\Desktop\Bartcellos
```

### 2. Backend - Instalar Dependências

```bash
# Navegue para pasta backend
cd backend

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# No Windows:
venv\Scripts\activate

# No Linux/Mac:
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### 3. Frontend - Instalar Dependências

```bash
# Navegue para pasta frontend
cd ..\frontend

# Instale dependências
npm install
```

---

## ⚙️ Configuração

### 1. Banco de Dados

#### Criar Banco PostgreSQL

```bash
# Acesse PostgreSQL
psql -U postgres

# Dentro do psql:
CREATE DATABASE bartcellos_loyalty;
CREATE USER bartcellos WITH PASSWORD 'seu_password_aqui';
ALTER ROLE bartcellos SET client_encoding TO 'utf8';
ALTER ROLE bartcellos SET default_transaction_isolation TO 'read committed';
ALTER ROLE bartcellos SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE bartcellos_loyalty TO bartcellos;
\q
```

### 2. Variáveis de Ambiente - Backend

```bash
# Na pasta backend, crie arquivo .env
# Copie de .env.example
copy .env.example .env
```

**Edite `.backend/.env`:**

```env
# DATABASE
DATABASE_URL=postgresql://bartcellos:seu_password_aqui@localhost:5432/bartcellos_loyalty

# JWT
SECRET_KEY=sua-chave-secreta-super-segura-aqui-mude-em-producao
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# APP
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Variáveis de Ambiente - Frontend

Na pasta `frontend`, crie `.env`:

```env
VITE_API_URL=http://localhost:8000
```

---

## 🚀 Rodando a Aplicação

### Opção 1: Em Dois Terminais (Recomendado)

#### Terminal 1 - Backend

```bash
# Na pasta backend
cd backend

# Ative ambiente virtual
venv\Scripts\activate

# Rode servidor
python -m uvicorn app.main:app --reload

# Output esperado:
# Uvicorn running on http://127.0.0.1:8000
# Press CTRL+C to quit
```

#### Terminal 2 - Frontend

```bash
# Na pasta frontend (novo terminal)
cd frontend

# Rode servidor de desenvolvimento
npm run dev

# Output esperado:
# VITE v5.0.8  ready in 1234 ms
# ➜  Local:   http://localhost:3000/
# ➜  Press q to quit
```

### Opção 2: Docker (Produção)

```bash
# Na raiz do projeto
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

---

## 📝 Primeira Execução

### 1. Registrar Empresa

**Request:**

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Minha Empresa",
    "email": "admin@empresa.com",
    "password": "senha123"
  }'
```

**Response:**

```json
{
  "success": true,
  "message": "Empresa registrada com sucesso",
  "data": {
    "user_id": 1,
    "company_id": 1,
    "email": "admin@empresa.com"
  }
}
```

### 2. Fazer Login

**Request:**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@empresa.com",
    "senha": "senha123"
  }'
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "user_id": 1,
    "company_id": 1,
    "email": "admin@empresa.com"
  }
}
```

---

## 🌐 Acessar Interface

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Redoc:** http://localhost:8000/redoc

---

## 📁 Estrutura do Projeto

```
Bartcellos/
├── backend/
│   ├── app/
│   │   ├── models/          # Modelos SQLAlchemy
│   │   ├── routes/          # Endpoints da API
│   │   ├── services/        # Lógica de negócio
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── utils/           # Utilitários
│   │   ├── config.py        # Configurações
│   │   ├── database.py      # Conexão BD
│   │   └── main.py          # App FastAPI
│   ├── requirements.txt     # Dependências Python
│   ├── .env.example         # Template variáveis env
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/           # Páginas React
│   │   ├── components/      # Componentes reutilizáveis
│   │   ├── services/        # Serviços API
│   │   ├── config.js        # Configurações
│   │   └── App.jsx          # Componente raiz
│   ├── public/
│   │   ├── manifest.json    # PWA manifest
│   │   └── index.html
│   ├── package.json         # Dependências Node
│   ├── vite.config.js       # Configuração Vite
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

---

## 🔌 API Endpoints

### ✅ Autenticação

| Método | Endpoint         | Descrição                |
| ------ | ---------------- | ------------------------ |
| POST   | `/auth/register` | Registra empresa + admin |
| POST   | `/auth/login`    | Login de usuário         |

### 👥 Clientes

| Método | Endpoint         | Descrição         |
| ------ | ---------------- | ----------------- |
| POST   | `/clientes`      | Criar cliente     |
| GET    | `/clientes`      | Listar clientes   |
| GET    | `/clientes/{id}` | Detalhes cliente  |
| PUT    | `/clientes/{id}` | Atualizar cliente |

### 🎯 Pontos

| Método | Endpoint                          | Descrição            |
| ------ | --------------------------------- | -------------------- |
| POST   | `/clientes/{id}/pontos`           | Movimentar pontos    |
| GET    | `/clientes/{id}/pontos/historico` | Histórico transações |

### 📦 Produtos

| Método | Endpoint                   | Descrição           |
| ------ | -------------------------- | ------------------- |
| GET    | `/produtos`                | Listar produtos     |
| POST   | `/produtos`                | Criar produto       |
| POST   | `/produtos/importar-excel` | Importar de Excel   |
| GET    | `/produtos/template-excel` | Baixar modelo       |
| GET    | `/produtos/exportar-excel` | Exportar para Excel |

### 📊 Dashboard

| Método | Endpoint                   | Descrição    |
| ------ | -------------------------- | ------------ |
| GET    | `/dashboard/stats`         | Estatísticas |
| GET    | `/dashboard/top-customers` | Top clientes |

---

## 🧪 Exemplo Completo

### 1. Registrar Empresa

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Café Premium",
    "email": "gerente@cafe.com",
    "password": "senha123"
  }'
```

Copie o `access_token` retornado.

### 2. Criar Cliente

```bash
curl -X POST "http://localhost:8000/clientes" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "telefone": "11999999999",
    "email": "joao@email.com"
  }'
```

### 3. Adicionar Pontos

```bash
curl -X POST "http://localhost:8000/clientes/1/pontos" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "pontos": 100,
    "tipo": "entrada",
    "descricao": "Compra de café"
  }'
```

### 4. Resgatar Pontos

```bash
curl -X POST "http://localhost:8000/clientes/1/pontos" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "pontos": 50,
    "tipo": "saida",
    "descricao": "Resgate - Bebida grátis"
  }'
```

---

## 🐛 Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'fastapi'`

```bash
# Certifique-se que venv está ativado
venv\Scripts\activate

# Reinstale dependências
pip install -r requirements.txt
```

### Erro: `psycopg2.OperationalError`

```bash
# Verifique conexão PostgreSQL
psql -U bartcellos -d bartcellos_loyalty

# Verifique DATABASE_URL no .env
DATABASE_URL=postgresql://bartcellos:password@localhost:5432/bartcellos_loyalty
```

### Erro: `CORS error`

Backend e Frontend devem estar rodando juntos:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

### Porta já em uso

```bash
# Backend (encontre processo na porta 8000)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Frontend (encontre processo na porta 3000)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

## 🎯 Próximos Passos

1. ✅ **Frontend** - Implementar pages (Login, Dashboard, Customers, etc)
2. ✅ **PWA** - Adicionar service worker + manifest
3. ✅ **Testes** - Unit tests e E2E
4. ✅ **Deploy** - Heroku, AWS, DigitalOcean
5. ✅ **Monitoramento** - Sentry, Datadog

---

## 📞 Suporte

Para dúvidas:

- Backend Issue: Verifique logs em `http://localhost:8000/docs`
- Frontend Issue: Abra DevTools (F12) no navegador
- Database Issue: Conecte via `psql -U bartcellos -d bartcellos_loyalty`

---

**Versão:** 1.0.0  
**Última atualização:** Abril 2026
