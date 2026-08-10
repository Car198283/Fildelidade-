# Deploy no Render

Este projeto esta preparado para subir no Render com:

- `fidelidade-api`: backend FastAPI
- `fidelidade-web`: frontend React/Vite
- `fidelidade-db`: banco PostgreSQL

## Passos

1. Coloque esta pasta em um repositorio no GitHub.
2. Acesse `https://dashboard.render.com/`.
3. Clique em **New** > **Blueprint**.
4. Selecione o repositorio do projeto.
5. Confirme o arquivo `render.yaml`.
6. Aguarde criar os tres recursos.
7. Abra o servico `fidelidade-api` e copie a URL publica real.
8. Abra o servico `fidelidade-web` e ajuste `VITE_API_URL` para a URL real do backend.
9. Faca **Manual Deploy** do `fidelidade-web`.

## Primeiro acesso

Depois do deploy, abra:

`https://SEU-FRONTEND.onrender.com/register`

Cadastre a empresa e o usuario administrador. Depois acesse:

`https://SEU-FRONTEND.onrender.com/captura`

## Observacao

O `render.yaml` usa inicialmente:

`https://fidelidade-api.onrender.com`

Se o Render criar outro nome/URL para o backend, atualize `VITE_API_URL` no painel do frontend.
