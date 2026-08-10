# 📝 Exemplos de Requisições API

## 🔐 Autenticação

### Registrar Empresa

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Café Premium",
    "email": "gerente@cafe.com",
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
    "email": "gerente@cafe.com"
  }
}
```

### Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "gerente@cafe.com",
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
    "email": "gerente@cafe.com"
  }
}
```

Salve o `access_token` para as próximas requisições!

---

## 👥 Clientes

### Criar Cliente

```bash
TOKEN="seu_access_token_aqui"

curl -X POST "http://localhost:8000/clientes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "telefone": "11999999999",
    "email": "joao@email.com"
  }'
```

### Listar Clientes

```bash
TOKEN="seu_access_token_aqui"

# Listar todos
curl -X GET "http://localhost:8000/clientes" \
  -H "Authorization: Bearer $TOKEN"

# Com filtros
curl -X GET "http://localhost:8000/clientes?page=1&limit=50&search=João" \
  -H "Authorization: Bearer $TOKEN"
```

### Obter Detalhes do Cliente

```bash
TOKEN="seu_access_token_aqui"

curl -X GET "http://localhost:8000/clientes/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 Pontos

### Adicionar Pontos

```bash
TOKEN="seu_access_token_aqui"

curl -X POST "http://localhost:8000/clientes/1/pontos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pontos": 100,
    "tipo": "entrada",
    "descricao": "Compra de café"
  }'
```

**Response:**

```json
{
  "success": true,
  "message": "Pontos movimentados com sucesso",
  "transaction": {
    "id": 1,
    "pontos": 100,
    "tipo": "entrada",
    "descricao": "Compra de café",
    "created_at": "2026-04-11T10:30:00"
  },
  "customer": {
    "id": 1,
    "nome": "João Silva",
    "pontos": 100
  }
}
```

### Resgatar Pontos

```bash
TOKEN="seu_access_token_aqui"

curl -X POST "http://localhost:8000/clientes/1/pontos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pontos": 50,
    "tipo": "saida",
    "descricao": "Resgate - Bebida grátis"
  }'
```

### Histórico de Transações

```bash
TOKEN="seu_access_token_aqui"

curl -X GET "http://localhost:8000/clientes/1/pontos/historico?page=1&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📦 Produtos

### Listar Produtos

```bash
TOKEN="seu_access_token_aqui"

curl -X GET "http://localhost:8000/produtos?page=1&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

### Criar Produto

```bash
TOKEN="seu_access_token_aqui"

curl -X POST "http://localhost:8000/produtos" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Café Expresso",
    "preco": 10.50,
    "categoria_id": 1
  }'
```

### Baixar Modelo Excel

```bash
TOKEN="seu_access_token_aqui"

curl -X GET "http://localhost:8000/produtos/template-excel" \
  -H "Authorization: Bearer $TOKEN" \
  --output produto_template.xlsx
```

### Importar Produtos Excel

```bash
TOKEN="seu_access_token_aqui"

curl -X POST "http://localhost:8000/produtos/importar-excel" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@produtos.xlsx"
```

### Exportar Produtos Excel

```bash
TOKEN="seu_access_token_aqui"

curl -X GET "http://localhost:8000/produtos/exportar-excel" \
  -H "Authorization: Bearer $TOKEN" \
  --output produtos_export.xlsx
```

---

## 📊 Dashboard

### Estatísticas

```bash
TOKEN="seu_access_token_aqui"

curl -X GET "http://localhost:8000/dashboard/stats" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "total_customers": 5,
    "total_points_distributed": 500,
    "total_points_redeemed": 150,
    "total_points_circulation": 350
  }
}
```

### Top Clientes

```bash
TOKEN="seu_access_token_aqui"

curl -X GET "http://localhost:8000/dashboard/top-customers?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔧 Usar com Postman

1. Crie uma collection no Postman
2. Em cada request, defina Authorization type como "Bearer Token"
3. No campo Token, use: `{{access_token}}`
4. Após fazer login, copie o token retornado e defina em "Pre-request Script":

```javascript
pm.environment.set("access_token", pm.response.json().data.access_token);
```

---

## 💻 Usar com Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "gerente@cafe.com",
    "senha": "senha123"
})

token = response.json()["data"]["access_token"]

# Headers com token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Listar clientes
response = requests.get(f"{BASE_URL}/clientes", headers=headers)
print(response.json())

# Adicionar pontos
response = requests.post(f"{BASE_URL}/clientes/1/pontos", headers=headers, json={
    "pontos": 100,
    "tipo": "entrada",
    "descricao": "Compra"
})
print(response.json())
```

---

## 💡 Dicas

- Sempre inclua o Bearer token em todas as requisições (exceto auth/register e auth/login)
- O sistema valida `company_id` automaticamente baseado no token
- Não é possível ter saldo negativo de pontos
- Todas as transações são imutáveis (apenas leitura)

---

**Pronto! Agora você tem tudo para começar a testar a API.** 🚀
