import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal
from app.models import Company, User
from app.routes import admin, auth, customers, points, products, dashboard, promotions, reports, mobile, integrations, meta_webhook, master_reports
from app.config import settings
from app.services.auth_service import AuthService

logger = logging.getLogger("uvicorn.error")

# Inicializa app ANTES de criar tabelas (para evitar erro)
app = FastAPI(
    title="Fidelidade Total - Sistema de Fidelização",
    description="Fidelidade Total - Sistema de Fidelização com Pontos",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bootstrap opcional; o schema deve existir após `alembic upgrade head`.
try:
    logger.info(
        "[MASTER_BOOTSTRAP] configuracao email=%s password=%s",
        bool(settings.master_email),
        bool(settings.master_password),
    )
    if settings.master_email and settings.master_password:
        db = SessionLocal()
        try:
            company = db.query(Company).filter(Company.nome == "Master").first()
            if not company:
                company = Company(nome="Master", plano="enterprise", ativo=True)
                db.add(company)
                db.flush()
                logger.info("[MASTER_BOOTSTRAP] empresa_master criada company_id=%s", company.id)
            else:
                logger.info(
                    "[MASTER_BOOTSTRAP] empresa_master localizada company_id=%s ativo=%s read_only=%s",
                    company.id,
                    company.ativo,
                    company.read_only,
                )

            user = db.query(User).filter(User.email == settings.master_email).first()
            senha_hash = AuthService.hash_password(settings.master_password)
            if not user:
                user = User(
                    email=settings.master_email,
                    senha_hash=senha_hash,
                    company_id=company.id,
                    role="master",
                    ativo=True,
                )
                db.add(user)
                logger.info("[MASTER_BOOTSTRAP] usuario_master novo")
            else:
                logger.info(
                    "[MASTER_BOOTSTRAP] usuario_master localizado user_id=%s company_id_anterior=%s "
                    "role_anterior=%s ativo_anterior=%s",
                    user.id,
                    user.company_id,
                    user.role,
                    user.ativo,
                )
                user.senha_hash = senha_hash
                user.company_id = company.id
                user.role = "master"
                user.ativo = True
            db.commit()
            db.refresh(user)
            db.refresh(company)
            logger.info(
                "[MASTER_BOOTSTRAP] concluido user_id=%s company_id=%s role=%s usuario_ativo=%s "
                "empresa_ativa=%s read_only=%s hash_atualizado=true",
                user.id,
                user.company_id,
                user.role,
                user.ativo,
                company.ativo,
                company.read_only,
            )
        finally:
            db.close()
    else:
        logger.warning("[MASTER_BOOTSTRAP] ignorado: MASTER_EMAIL ou MASTER_PASSWORD ausente")
except Exception as e:
    logger.exception("[MASTER_BOOTSTRAP] falhou antes da inicializacao da API")
    raise RuntimeError("Falha no bootstrap; confirme as migracoes e os secrets") from e

# Routes
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(points.router)
app.include_router(products.router)
app.include_router(dashboard.router)
app.include_router(promotions.router)
app.include_router(reports.router)
app.include_router(mobile.router)
app.include_router(integrations.router)
app.include_router(meta_webhook.router)
app.include_router(admin.router)
app.include_router(master_reports.router)

@app.get("/")
def root():
    """Health check"""
    return {
        "status": "ok",
        "api": "Fidelidade Total",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
