a# Manual - Integracao n8n com WhatsApp

Este projeto agora tem uma fila de WhatsApp no banco de dados para o n8n consumir.

## Ideia do Fluxo

1. O sistema gera mensagens pendentes no banco.
2. O n8n busca mensagens pendentes.
3. O n8n envia pelo provedor de WhatsApp.
4. O n8n marca a mensagem como enviada ou erro.

Assim o n8n nao precisa mexer direto no SQLite.

## Login Para o n8n

Primeiro faca login pela API:

`POST http://localhost:8000/auth/login`

Body:

```json
{
  "email": "cadufcostajf@gmail.com",
  "senha": "123456"
}
```

Pegue o campo:

`data.access_token`

Nos proximos requests, envie o header:

`Authorization: Bearer SEU_TOKEN`

## Gerar Fila de Mensagens

Endpoint:

`POST http://localhost:8000/integracoes/n8n/whatsapp/fila/gerar`

Headers:

`Authorization: Bearer SEU_TOKEN`

Body para aniversariantes:

```json
{
  "tipo": "aniversario",
  "mensagem_template": "Ola {nome}, feliz aniversario! A equipe agradece sua preferencia."
}
```

Body para clientes premiados:

```json
{
  "tipo": "premio",
  "mensagem_template": "Ola {nome}, voce tem {pontos} pontos e ja pode resgatar seu premio."
}
```

Body para um cliente especifico:

```json
{
  "tipo": "manual",
  "customer_id": 5,
  "mensagem_template": "Ola {nome}, obrigado pela visita!"
}
```

Variaveis disponiveis no texto:

- `{nome}`
- `{telefone}`
- `{pontos}`

## Buscar Mensagens Pendentes

Endpoint:

`GET http://localhost:8000/integracoes/n8n/whatsapp/fila/pendentes?limit=20`

Resposta:

```json
{
  "success": true,
  "total": 1,
  "data": [
    {
      "id": 1,
      "customer_id": 5,
      "tipo": "premio",
      "telefone": "5532987012526",
      "cliente_nome": "Carlos Eduardo",
      "mensagem": "Ola Carlos Eduardo, voce tem 10 pontos e ja pode resgatar seu premio.",
      "status": "pendente"
    }
  ]
}
```

O n8n deve enviar `telefone` e `mensagem` para o provedor de WhatsApp.

## Marcar Como Enviada

Endpoint:

`PUT http://localhost:8000/integracoes/n8n/whatsapp/fila/1/status`

Body:

```json
{
  "status": "enviado",
  "provider_message_id": "ID_RETORNADO_PELO_WHATSAPP"
}
```

## Marcar Como Erro

Endpoint:

`PUT http://localhost:8000/integracoes/n8n/whatsapp/fila/1/status`

Body:

```json
{
  "status": "erro",
  "erro": "Telefone invalido ou envio recusado"
}
```

## Status Recomendados

- `pendente`
- `enviado`
- `erro`
- `cancelado`

## Observacoes

- O telefone e convertido para formato brasileiro com DDI `55` quando tiver 10 ou 11 digitos.
- O sistema nao envia WhatsApp sozinho. Ele prepara a fila para o n8n.
- Voce pode usar WhatsApp Cloud API, Evolution API, Z-API, Twilio ou outro provedor no n8n.

