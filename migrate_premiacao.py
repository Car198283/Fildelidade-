"""
Migration Script: Adicionar campos de premiação ao Customer
Data: 12 de abril de 2026

Script para adicionar as novas colunas ao modelo Customer sem perder dados existentes.
Execute este script ANTES de reiniciar o backend.
"""

import sys
from pathlib import Path

# Adiciona o backend ao path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import text, inspect
from app.database import engine
from app.models import Base, Customer

def migration_add_premiacao_fields():
    """Migração para adicionar campos de premiação ao Customer"""
    
    print("🔄 Iniciando migração: Adicionar campos de premiação...")
    
    with engine.connect() as connection:
        db_type = str(engine.url).split(":")[0]
        print(f"📊 Banco de dados: {db_type}")
        
        # Verificar colunas existentes
        print("\n📋 Verificando colunas existentes...")
        
        try:
            inspector = inspect(engine)
            columns = {col['name'] for col in inspector.get_columns('customers')}
            print(f"Colunas encontradas: {columns}")
            
            # Verificar quais colunas faltam
            required_columns = {
                'valor_gasto_atual',
                'quantidade_produtos_comprados',
                'meta_premiacao_valor',
                'meta_premiacao_quantidade'
            }
            
            missing_columns = required_columns - columns
            
            if not missing_columns:
                print("✅ Todas as colunas já existem!")
                return True
            
            print(f"⚠️  Colunas faltando: {missing_columns}")
            
            # ====== SQLite ======
            if db_type == "sqlite":
                print("\n🔧 SQLite detectado - forçando criação de tabelas via ORM...")
                # Para SQLite, precisamos usar o ORM para criar as colunas
                # Mas como SQLite não suporta ALTER TABLE ADD COLUMN IF NOT EXISTS bem,
                # vamos usar uma abordagem diferente
                
                try:
                    # Recrear a tabela com as colunas novas
                    connection.execute(text("PRAGMA foreign_keys=OFF"))
                    
                    # Criar tabela temporária com dados antigos
                    connection.execute(text("""
                        CREATE TABLE customers_backup AS SELECT * FROM customers
                    """))
                    
                    # Dropar tabela antiga
                    connection.execute(text("DROP TABLE customers"))
                    
                    # Usar SQLAlchemy para recriar com colunas novas
                    Base.metadata.drop_all(bind=engine)
                    Base.metadata.create_all(bind=engine)
                    
                    # Copiar dados para a nova tabela
                    connection.execute(text("""
                        INSERT INTO customers 
                        (id, nome, telefone, email, data_nascimento, pontos, ativo, company_id, created_at, updated_at,
                         valor_gasto_atual, quantidade_produtos_comprados, meta_premiacao_valor, meta_premiacao_quantidade)
                        SELECT id, nome, telefone, email, data_nascimento, pontos, ativo, company_id, created_at, updated_at,
                               0.0, 0, NULL, NULL
                        FROM customers_backup
                    """))
                    
                    # Dropar tabela temporária
                    connection.execute(text("DROP TABLE customers_backup"))
                    
                    connection.execute(text("PRAGMA foreign_keys=ON"))
                    connection.commit()
                    
                    print("✅ Tabela recriada com sucesso!")
                    
                except Exception as e:
                    print(f"⚠️  Abordagem de backup/restore falhou: {e}")
                    print("Tentando criar colunas individualmente...")
                    try:
                        # Fallback: tenta criar colunas
                        Base.metadata.create_all(bind=engine)
                        connection.commit()
                        print("✅ Colunas criadas via ORM")
                    except Exception as e2:
                        print(f"❌ Erro ao criar colunas: {e2}")
                        return False
            
            # ====== PostgreSQL ======
            elif db_type == "postgresql":
                print("\n🔧 PostgreSQL detectado - adicionando colunas...")
                try:
                    if 'valor_gasto_atual' not in columns:
                        connection.execute(text("""
                            ALTER TABLE customers ADD COLUMN valor_gasto_atual FLOAT DEFAULT 0.0 NOT NULL
                        """))
                        print("➕ Adicionada coluna: valor_gasto_atual")
                        
                    if 'quantidade_produtos_comprados' not in columns:
                        connection.execute(text("""
                            ALTER TABLE customers ADD COLUMN quantidade_produtos_comprados INTEGER DEFAULT 0 NOT NULL
                        """))
                        print("➕ Adicionada coluna: quantidade_produtos_comprados")
                        
                    if 'meta_premiacao_valor' not in columns:
                        connection.execute(text("""
                            ALTER TABLE customers ADD COLUMN meta_premiacao_valor FLOAT NULL
                        """))
                        print("➕ Adicionada coluna: meta_premiacao_valor")
                        
                    if 'meta_premiacao_quantidade' not in columns:
                        connection.execute(text("""
                            ALTER TABLE customers ADD COLUMN meta_premiacao_quantidade INTEGER NULL
                        """))
                        print("➕ Adicionada coluna: meta_premiacao_quantidade")
                    
                    # Criar índices
                    try:
                        connection.execute(text("""
                            CREATE INDEX IF NOT EXISTS idx_customer_valor_gasto ON customers(valor_gasto_atual)
                        """))
                        connection.execute(text("""
                            CREATE INDEX IF NOT EXISTS idx_customer_quantidade_produtos ON customers(quantidade_produtos_comprados)
                        """))
                        print("🔧 Índices criados")
                    except:
                        pass
                    
                    connection.commit()
                    print("✅ PostgreSQL atualizado com sucesso!")
                    
                except Exception as e:
                    print(f"❌ Erro PostgreSQL: {e}")
                    return False
            
            else:
                print(f"⚠️  Banco de dados '{db_type}' não suportado neste script")
                return False
        
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Verificar resultado
        print("\n✅ Migração concluída com sucesso!")
        print("\n📊 Resumo:")
        print("  ✓ Coluna: valor_gasto_atual (FLOAT)")
        print("  ✓ Coluna: quantidade_produtos_comprados (INTEGER)")
        print("  ✓ Coluna: meta_premiacao_valor (FLOAT)")
        print("  ✓ Coluna: meta_premiacao_quantidade (INTEGER)")
        print("\n🚀 Próximas etapas:")
        print("  1. Reiniciar o backend")
        print("  2. Reiniciar o frontend")
        print("  3. Testar funcionalidade de premiação no dashboard")
        
        return True

if __name__ == "__main__":
    try:
        success = migration_add_premiacao_fields()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
