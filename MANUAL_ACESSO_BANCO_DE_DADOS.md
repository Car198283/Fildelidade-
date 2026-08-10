# Manual - Acesso ao Banco de Dados

Este manual explica como localizar, abrir, copiar e consultar o banco de dados do sistema Fidelidade Total.

## 1. Banco Usado Pelo Sistema

O banco ativo do sistema fica em:

```text
C:\Users\caduf\OneDrive\Desktop\Fidelidade\bartcellos_loyalty.db
```

Este e o banco que o backend usa atualmente.

Existe outro banco dentro da pasta `backend`:

```text
C:\Users\caduf\OneDrive\Desktop\Fidelidade\backend\bartcellos_loyalty.db
```

Mas o sistema atual esta configurado para usar o banco da pasta principal, nao o da pasta `backend`.

## 2. Ferramenta Recomendada

Use o programa **DB Browser for SQLite**.

Site:

```text
https://sqlitebrowser.org/
```

Depois de instalar:

1. Abra o DB Browser for SQLite.
2. Clique em **Open Database**.
3. Selecione:

```text
C:\Users\caduf\OneDrive\Desktop\Fidelidade\bartcellos_loyalty.db
```

4. Clique na aba **Browse Data** para ver os dados.

## 3. Fazer Backup Antes de Mexer

Antes de editar qualquer coisa, copie o arquivo:

```text
bartcellos_loyalty.db
```

Para uma pasta de backup, por exemplo:

```text
C:\Users\caduf\OneDrive\Desktop\Backup_Fidelidade\
```

Sugestao de nome:

```text
bartcellos_loyalty_backup_2026_08_10.db
```

Nunca edite o banco sem backup.

## 4. Principais Tabelas

### companies

Guarda as empresas cadastradas.

Campos importantes:

- `id`
- `nome`
- `plano`
- `ativo`

### users

Guarda usuarios de login.

Campos importantes:

- `id`
- `email`
- `senha_hash`
- `company_id`
- `role`
- `ativo`

Atencao: a senha nao aparece em texto normal. Ela fica salva como hash.

### customers

Guarda os clientes.

Campos importantes:

- `id`
- `nome`
- `telefone`
- `email`
- `data_nascimento`
- `pontos`
- `ativo`
- `company_id`

### products

Guarda os produtos.

Campos importantes:

- `id`
- `nome`
- `preco`
- `categoria_id`
- `company_id`

### points_transactions

Guarda o historico de pontos.

Campos importantes:

- `id`
- `customer_id`
- `company_id`
- `product_id`
- `product_nome`
- `pontos`
- `tipo`
- `descricao`
- `created_at`

Tipos:

- `entrada`: pontos adicionados
- `saida`: pontos resgatados

### whatsapp_messages

Guarda a fila de mensagens para integracao com n8n/WhatsApp.

Campos importantes:

- `id`
- `company_id`
- `customer_id`
- `tipo`
- `telefone`
- `cliente_nome`
- `mensagem`
- `status`
- `provider_message_id`
- `erro`
- `created_at`
- `sent_at`

Status comuns:

- `pendente`
- `enviado`
- `erro`
- `cancelado`

## 5. Consultas SQL Uteis

### Ver empresas

```sql
SELECT * FROM companies;
```

### Ver usuarios

```sql
SELECT id, email, company_id, role, ativo FROM users;
```

### Ver clientes ativos

```sql
SELECT id, nome, telefone, email, pontos
FROM customers
WHERE ativo = 1
ORDER BY nome;
```

### Ver pontos de um cliente

```sql
SELECT id, nome, telefone, pontos
FROM customers
WHERE nome LIKE '%Carlos%';
```

### Ver historico de pontos

```sql
SELECT
  pt.id,
  c.nome AS cliente,
  pt.product_nome AS produto,
  pt.pontos,
  pt.tipo,
  pt.descricao,
  pt.created_at
FROM points_transactions pt
JOIN customers c ON c.id = pt.customer_id
ORDER BY pt.created_at DESC;
```

### Ver produtos mais consumidos

```sql
SELECT
  product_nome,
  COUNT(*) AS vendas,
  SUM(pontos) AS pontos
FROM points_transactions
WHERE tipo = 'entrada'
  AND product_nome IS NOT NULL
GROUP BY product_nome
ORDER BY vendas DESC;
```

### Ver aniversariantes do mes

```sql
SELECT nome, telefone, data_nascimento
FROM customers
WHERE ativo = 1
  AND strftime('%m', data_nascimento) = strftime('%m', 'now')
ORDER BY strftime('%d', data_nascimento);
```

### Ver mensagens pendentes para WhatsApp

```sql
SELECT id, telefone, cliente_nome, mensagem, status
FROM whatsapp_messages
WHERE status = 'pendente'
ORDER BY created_at;
```

## 6. Cuidados Importantes

- Nao altere `senha_hash` manualmente.
- Nao apague clientes direto do banco; prefira marcar `ativo = 0`.
- Nao altere pontos direto na tabela `customers`, porque isso deixa o historico errado.
- Para pontos, use sempre o sistema ou a API, pois ela registra em `points_transactions`.
- Antes de apagar qualquer dado, faca backup.

## 7. Acesso Pelo n8n

O mais seguro e o n8n acessar a API do sistema, nao o arquivo SQLite diretamente.

API local:

```text
http://localhost:8000
```

Endpoints principais para WhatsApp:

```text
POST /integracoes/n8n/whatsapp/fila/gerar
GET  /integracoes/n8n/whatsapp/fila/pendentes
PUT  /integracoes/n8n/whatsapp/fila/{message_id}/status
```

Veja o manual:

```text
MANUAL_N8N_WHATSAPP.md
```

