# Integracao WhatsApp com n8n

## Variaveis secretas

Configure no Render e no n8n; nunca grave os valores no Git:

- `N8N_WEBHOOK_SECRET`: mesmo valor (minimo 32 caracteres) na API e no n8n.
- `FIDELIDADE_API_URL`: URL publica da API, sem barra final.
- `FIDELIDADE_COMPANY_ID`: empresa que o workflow processa.
- `META_GRAPH_API_URL`: URL versionada da Graph API informada pela Meta, por exemplo `https://graph.facebook.com/vXX.X`.
- `META_PHONE_NUMBER_ID`: Phone Number ID da empresa.
- `WHATSAPP_API_TOKEN`: token permanente do usuario de sistema da Meta.
- `META_WEBHOOK_VERIFY_TOKEN`: token aleatorio criado por voce e repetido no painel Meta.
- `META_APP_SECRET`: segredo do aplicativo Meta, usado para validar a assinatura dos eventos.

Cada empresa deve ter um workflow ou credencial/identificador de empresa explicitamente configurado.

## Fluxo

1. O administrador gera a campanha em **WhatsApp** no sistema.
2. O n8n chama `POST /integracoes/n8n/whatsapp/fila/consumir` com os headers `X-N8N-Secret` e `X-Company-Id`.
3. A API reserva as mensagens como `processando` e incrementa a tentativa de forma transacional.
4. O n8n envia ao provedor.
5. O n8n chama `POST /integracoes/n8n/whatsapp/fila/{id}/callback` com o ID retornado pela Meta.
6. A Meta chama `GET/POST /integracoes/meta/whatsapp/webhook`; a API valida o token/assinatura e atualiza `enviado`, `entregue`, `lido` ou `erro`.
7. Erros recuperaveis voltam para `pendente` com espera exponencial ate `max_attempts`.

## Contrato do callback

```json
{
  "status": "enviado",
  "provider_message_id": "identificador-do-provedor",
  "erro": null
}
```

Status aceitos: `enviado`, `entregue`, `lido`, `erro` e `cancelado`.

## Webhook na Meta

- Callback URL: `https://fidelidade-api-4tsn.onrender.com/integracoes/meta/whatsapp/webhook`
- Verify token: o valor secreto definido em `META_WEBHOOK_VERIFY_TOKEN`.
- Assine o campo `messages` do objeto `whatsapp_business_account`.

Importe `n8n/fidelidade_whatsapp_queue.json`. O node **Enviar no provedor** ja usa o corpo oficial de mensagem de texto da WhatsApp Cloud API. O workflow nao contem credenciais.
