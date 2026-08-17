"""
Script para popular o banco de dados com dados de teste
Execute DEPOIS de mover o projeto para C:\Bartcellos:
  cd C:\Bartcellos
  python backend\seed_db.py
"""
import sys
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, Company
from app.services.auth_service import AuthService

def seed_database():
    """Cria tabelas e insere dados de teste"""
    
    # Cria todas as tabelas
    print("✅ Tabelas criadas")
    
    db = SessionLocal()
    
    try:
        # Verifica se já existe a empresa
        existing_company = db.query(Company).filter(Company.nome == "Minha Loja").first()
        if existing_company:
            print("ℹ️  Empresa 'Minha Loja' já existe")
            # Remove usuários antigos
            db.query(User).filter(User.company_id == existing_company.id).delete()
            db.commit()
        else:
            existing_company = None
        
        # Cria empresa
        company = Company(
            nome="Minha Loja",
            plano="free",
            ativo=True
        )
        db.add(company)
        db.flush()
        print(f"✅ Empresa criada: {company.nome}")
        
        # Cria usuário de teste
        hashed_password = AuthService.hash_password("123456")
        user = User(
            email="admin@loja.com",
            senha_hash=hashed_password,
            company_id=company.id,
            role="admin",
            ativo=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Usuário criado:")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Company ID: {company.id}")
        print()
        print("🔐 Credenciais de teste:")
        print("   Email: admin@loja.com")
        print("   Senha: 123456")
        print()
        print("✅ Banco de dados populado com sucesso!")
        print()
        print("📝 Próximo passo:")
        print("   1. Abra http://localhost:3000/login")
        print("   2. Use as credenciais acima para fazer login")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao popular banco: {str(e)}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
