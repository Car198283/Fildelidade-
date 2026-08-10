# ⚡ Guia Rápido - Como Rodar o Bartcellos

## 🚀 Opção 1: Desenvolvimento Local (Recomendado para Desenvolvimento)

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Git

### Passo a Passo

#### 1️⃣ Configurar Banco de Dados

```bash
# Acesse PostgreSQL (Windows)
psql -U postgres

# Ou (Linux/Mac)
sudo -u postgres psql
```

No prompt do PostgreSQL:

```sql
CREATE DATABASE bartcellos_loyalty;
CREATE USER bartcellos WITH PASSWORD 'sua_senha_aqui';
ALTER ROLE bartcellos SET client_encoding TO 'utf8';
ALTER ROLE bartcellos SET default_transaction_isolation TO 'read committed';
ALTER ROLE bartcellos SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE bartcellos_loyalty TO bartcellos;
\q
```

#### 2️⃣ Backend

```bash
# Navegue até a pasta backend
cd backend

# Crie arquivo .env
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac

# EDITE .env com seus dados:
# DATABASE_URL=postgresql://bartcellos:sua_senha_aqui@localhost:5432/bartcellos_loyalty

# Crie ambiente virtual
python -m venv venv

# Ative
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt

# Rode servidor
python -m uvicorn app.main:app --reload

# ✅ Backend disponível em http://localhost:8000
# 📚 API Docs em http://localhost:8000/docs
```

#### 3️⃣ Frontend (Em novo terminal)

```bash
# Navegue até frontend
cd frontend

# Instale dependências
npm install

# Rode servidor
npm run dev

# ✅ Frontend disponível em http://localhost:3000
```

---

## 🐳 Opção 2: Docker (Recomendado para Produção)

### Pré-requisitos

- Docker
- Docker Compose

### Começo Rápido

```bash
# Na raiz do projeto
docker-compose up -d

# Aguarde alguns segundos...

# ✅ Backend: http://localhost:8000
# ✅ Frontend: http://localhost:3000
# ✅ Banco: localhost:5432

# Ver logs
docker-compose logs -f backend

# Parar
docker-compose down

# Remover volumes (limpar dados)
docker-compose down -v
```

---

## 📱 Primeiros Passos

### 1. Registre sua Empresa

Acesse http://localhost:3000 ou clique em "Criar Conta"

**Dados de teste:**

```
Empresa: Minha Loja
Email: admin@loja.com
Senha: senha123
```

### 2. Faça Login

Use os mesmos dados acima.

### 3. Crie alguns Clientes

Vá para **Clientes** → **Novo Cliente**

### 4. Adicione Pontos

Clique em um cliente → **Adicionar Pontos**

### 5. Importe Produtos

Vá para **Produtos** → **Importar Excel**

---

## 🐛 Troubleshooting

### Erro: `ModuleNotFoundError: No module named 'fastapi'`

```bash
# Verifique se venv está ativado
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstale
pip install -r requirements.txt
```

### Erro: `psycopg2.OperationalError`

```bash
# Verifique PostgreSQL está rodando
psql -U postgres

# Verifique DATABASE_URL no backend/.env
# Deve estar: postgresql://bartcellos:SENHA@localhost:5432/bartcellos_loyalty
```

### Erro: `CORS connection refused`

```bash
# Certifique-se que ambos estão rodando:
# Backend: http://localhost:8000
# Frontend: http://localhost:3000

# Verifique VITE_API_URL no frontend/.env
# Deve ser: http://localhost:8000
```

### Porta já em uso

```bash
# Windows - Encontre processo na porta
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Mate o processso
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

---

## 🔗 URLs Importantes

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Database:** localhost:5432 (user: bartcellos)

---

## 📚 Próximas Ações

- [ ] Registrar empresa
- [ ] Criar alguns clientes
- [ ] Testar sistema de pontos
- [ ] Importar produtos via Excel
- [ ] Explorar Dashboard
- [ ] Deploy em produção (Heroku, AWS, etc)

---

## 🆘 Precisa de Ajuda?

1. Verifique o README.md completo
2. Veja os logs: `docker-compose logs -f backend`
3. Abra DevTools (F12) no navegador para erros do frontend
4. Verifique a API Docs em http://localhost:8000/docs

---

**Pronto para começar! 🎉**
