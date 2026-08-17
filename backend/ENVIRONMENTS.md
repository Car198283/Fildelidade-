# Configuração por ambiente

Use arquivos locais não versionados ou o secret manager da plataforma. O Git recebe apenas `.env.example`.

- `APP_ENV=development`: PostgreSQL local, logs de desenvolvimento opcionais.
- `APP_ENV=staging`: PostgreSQL isolado de homologação e `DEBUG=false`.
- `APP_ENV=production`: PostgreSQL de produção e `DEBUG=false`.
- `APP_ENV=test`: único ambiente que permite SQLite, somente para testes automatizados.

Variáveis obrigatórias: `DATABASE_URL` e `SECRET_KEY` (mínimo de 32 caracteres). Execute `alembic upgrade head` antes de iniciar a API. Em um banco legado já existente, faça backup antes da primeira migração.

Toda chamada de movimentação exige `Idempotency-Key` e um `motivo`. Repetir a mesma chave na mesma empresa retorna o lançamento original sem alterar novamente o saldo.
