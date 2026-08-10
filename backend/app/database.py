from sqlalchemy import create_engine
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
import os

# Determinar qual URL usar baseado em DB_TYPE
database_url = settings.get_database_url()
db_info = settings.get_database_info()

print(f"\n[DATABASE] Usando: {db_info}")

# Configurações específicas por tipo de banco
if settings.db_type.lower() == "postgresql":
    # PostgreSQL - com pool e timeouts
    engine = create_engine(
        database_url,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600
    )
else:
    # SQLite - com check_same_thread=False para suportar múltiplas threads
    # Criar diretório se não existir
    sqlite_dir = os.path.dirname(settings.sqlite_path)
    if sqlite_dir and not os.path.exists(sqlite_dir):
        os.makedirs(sqlite_dir, exist_ok=True)
    
    engine = create_engine(
        database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Session:
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_runtime_schema():
    """Aplica pequenas migracoes compativeis com bancos SQLite existentes."""
    inspector = inspect(engine)
    if "points_transactions" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("points_transactions")}
    with engine.begin() as conn:
        if "product_id" not in columns:
            conn.execute(text("ALTER TABLE points_transactions ADD COLUMN product_id INTEGER"))
        if "product_nome" not in columns:
            conn.execute(text("ALTER TABLE points_transactions ADD COLUMN product_nome VARCHAR(255)"))

