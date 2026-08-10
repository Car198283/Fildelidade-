from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, ensure_runtime_schema
from app.models import Base
from app.routes import auth, customers, points, products, dashboard, promotions, reports, mobile, integrations
from app.config import settings

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
