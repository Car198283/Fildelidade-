# 🚀 Deployment e Produção

## 🏭 Checklist Pré-Produção

- [ ] Alterar `SECRET_KEY` em ambiente de produção
- [ ] Alterar `DEBUG = False`
- [ ] Configurar CORS apenas para domínios conhecidos
- [ ] Usar HTTPS em produção
- [ ] Configurar variáveis de ambiente seguras
- [ ] Fazer backup do banco de dados
- [ ] Testar todos os endpoints
- [ ] Configurar renovação de SSL
- [ ] Configurar SMTP para emails
- [ ] Configurar backups automáticos

---

## ☁️ Deploy na Heroku

### 1. Instale Heroku CLI

```bash
# Windows
choco install heroku-cli

# Mac
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Login

```bash
heroku login
```

### 3. Crie Aplicações

```bash
# Backend
heroku create seu-app-backend
# Exemplo: heroku create bartcellos-api

# Frontend
heroku create seu-app-frontend
# Exemplo: heroku create bartcellos-web
```

### 4. Adicione PostgreSQL

```bash
# No backend
heroku addons:create heroku-postgresql:hobby-dev -a seu-app-backend
```

### 5. Configure Variáveis

```bash
heroku config:set SECRET_KEY="sua-chave-super-segura" -a seu-app-backend
heroku config:set DEBUG=False -a seu-app-backend
heroku config:set ALGORITHM=HS256 -a seu-app-backend
```

### 6. Deploy Backend

```bash
cd backend

# Crie Procfile
echo "web: python -m uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Push
git push heroku main
```

### 7. Deploy Frontend

```bash
cd frontend

# Atualize .env
VITE_API_URL=https://seu-app-backend.herokuapp.com

# Faça build
npm run build

# Crie Procfile
echo "web: npm run preview" > Procfile

# Push
git push heroku main
```

---

## 🐳 Deploy com Docker (AWS ECS, DigitalOcean, etc)

### Build Images

```bash
docker build -t bartcellos-backend:latest ./backend
docker build -t bartcellos-frontend:latest ./frontend
docker build -t bartcellos-postgres:latest ./postgres
```

### Push para Docker Hub

```bash
# Backend
docker tag bartcellos-backend:latest seu-usuario/bartcellos-backend:latest
docker push seu-usuario/bartcellos-backend:latest

# Frontend
docker tag bartcellos-frontend:latest seu-usuario/bartcellos-frontend:latest
docker push seu-usuario/bartcellos-frontend:latest
```

### Deploy na DigitalOcean App Platform

1. Conecte seu repositório GitHub
2. Selecione `docker-compose.yml`
3. Configure variáveis de ambiente
4. Deploy!

---

## 🔐 Segurança

### Variáveis de Ambiente Produção

```env
# Backend
DATABASE_URL=postgresql://user:password@prod-db:5432/name
SECRET_KEY=gerar-com-secrets.token_urlsafe(32)
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com
CORS_ORIGINS=https://seu-dominio.com

# Frontend
VITE_API_URL=https://api.seu-dominio.com
```

### Renovação de Certificado SSL

```bash
# Usando Let's Encrypt com Certbot
sudo certbot renew --dry-run

# Automático com cron
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 Monitoramento

### Sentry (Error Tracking)

```bash
# Instale
pip install sentry-sdk

# Configure no backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="seu-sentry-dsn",
    integrations=[FastApiIntegration()]
)
```

### Prometheus (Metrics)

```bash
# Instale
pip install prometheus-client

# Use no main.py
from prometheus_client import Counter, Histogram
```

### DataDog (Logging)

```bash
# Configure variáveis
export DD_API_KEY="seu-key"
export DD_SITE="datadoghq.com"
```

---

## 🚦 CI/CD com GitHub Actions

Crie `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Deploy to Heroku Backend
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: seu-app-backend
          heroku_email: seu@email.com
          appdir: backend

      - name: Deploy to Heroku Frontend
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: seu-app-frontend
          heroku_email: seu@email.com
          appdir: frontend
```

---

## 💾 Backup do Banco

### PgDump (PostgreSQL)

```bash
# Backup
pg_dump -U bartcellos -h localhost bartcellos_loyalty > backup.sql

# Restore
psql -U bartcellos -h localhost bartcellos_loyalty < backup.sql
```

### Automático com Cron

```bash
# Crie script backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U bartcellos -h localhost bartcellos_loyalty > /backups/backup_$DATE.sql
```

Adicione ao cron:

```bash
crontab -e

# Backup diário às 2am
0 2 * * * /path/to/backup.sh
```

---

## 🎯 Performance

### Cache (Redis)

```bash
# Instale
pip install redis

# Use no backend
from redis import Redis
redis_client = Redis(host='localhost', port=6379)
```

### CDN para Frontend

1. Configure CloudFlare
2. Aponte domínio para CloudFlare
3. Ative cache

### Otimização de Imagens

```bash
# Instale Pillow
pip install Pillow

# Use em produtos
from PIL import Image
```

---

## 📱 PWA em Produção

Certifique-se que:

- ✅ `manifest.json` está servido com MIME type correto
- ✅ Service Worker está registrado
- ✅ HTTPS está habilitado
- ✅ Icons estão otimizados

---

## 🔗 Recursos Úteis

- [Heroku Docs](https://devcenter.heroku.com/)
- [DigitalOcean Docs](https://docs.digitalocean.com/)
- [AWS ECS](https://aws.amazon.com/ecs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Docker Docs](https://docs.docker.com/)

---

**Parabéns! Seu app está pronto para produção!** 🎉
