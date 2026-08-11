from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import SessionLocal, engine, ensure_runtime_schema
from app.models import Base, Company, User
from app.routes import admin, auth, customers, points, products, dashboard, promotions, reports, mobile, integrations
from app.config import settings
from app.services.auth_service import AuthService

# Inicializa app ANTES de criar tabelas (para evitar erro)
app = FastAPI(
    title="Fidelidade Total - Sistema de Fidelização",
    description="Fidelidade Total - Sistema de Fidelização com Pontos",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria tabelas na inicialização
try:
    Base.metadata.create_all(bind=engine)
    ensure_runtime_schema()
    if settings.master_email and settings.master_password:
        db = SessionLocal()
        try:
            company = db.query(Company).filter(Company.nome == "Master").first()
            if not company:
                company = Company(nome="Master", plano="enterprise", ativo=True)
                db.add(company)
                db.flush()

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
            else:
                user.senha_hash = senha_hash
                user.company_id = company.id
                user.role = "master"
                user.ativo = True
            db.commit()
        finally:
            db.close()
except Exception as e:
    print(f"[AVISO] Erro ao criar tabelas: {e}")
    print("[INFO] Tabelas podem já existir ou banco de dados pode estar indisponível")

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
app.include_router(admin.router)

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
