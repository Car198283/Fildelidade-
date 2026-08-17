# Integracao WhatsApp com n8n

## Variaveis secretas

Configure no Render e no n8n; nunca grave os valores no Git:

- `N8N_WEBHOOK_SECRET`: mesmo valor (minimo 32 caracteres) na API e no n8n.
- `FIDELIDADE_API_URL`: URL publica da API, sem barra final.
- `FIDELIDADE_COMPANY_ID`: empresa que o workflow processa.
- `WHATSAPP_SEND_URL`: endpoint do provedor escolhido.
- `WHATSAPP_API_TOKEN`: token do provedor WhatsApp.

Cada empresa deve ter um workflow ou credencial/identificador de empresa explicitamente configurado.

## Fluxo

1. O administrador gera a campanha em **WhatsApp** no sistema.
2. O n8n chama `POST /integracoes/n8n/whatsapp/fila/consumir` com os headers `X-N8N-Secret` e `X-Company-Id`.
3. A API reserva as mensagens como `processando` e incrementa a tentativa de forma transacional.
4. O n8n envia ao provedor.
5. O n8n chama `POST /integracoes/n8n/whatsapp/fila/{id}/callback` com `enviado` ou `erro`.
6. Erros recuperaveis voltam para `pendente` com espera exponencial ate `max_attempts`.

## Contrato do callback

```json
{
  "status": "enviado",
  "provider_message_id": "identificador-do-provedor",
  "erro": null
}
```

Status aceitos: `enviado`, `entregue`, `lido`, `erro` e `cancelado`.

Importe `n8n/fidelidade_whatsapp_queue.json` e adapte apenas o corpo do node **Enviar no provedor** ao contrato do provedor escolhido. O workflow nao contem credenciais.
