#!/usr/bin/env python3
"""
Verificar dados no banco e testar endpoints
"""
import sqlite3
from pathlib import Path

db_path = Path("bartcellos_loyalty.db")

# Conectar ao banco
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("  VERIFICAÇÃO DO BANCO DE DADOS")
print("=" * 60)

# 1. Verificar clientes
print("\n1️⃣  CLIENTES NO BANCO:")
cursor.execute("SELECT COUNT(*) as count FROM customers WHERE ativo = 1")
total = cursor.fetchone()['count']
print(f"   Total de clientes ativos: {total}")

if total > 0:
    cursor.execute("""
        SELECT id, nome, pontos, valor_gasto_atual, quantidade_produtos_comprados 
        FROM customers 
        WHERE ativo = 1 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   - {row['nome']}: {row['pontos']} pontos")

# 2. Verificar empresas
print("\n2️⃣  EMPRESAS:")
cursor.execute("SELECT COUNT(*) as count FROM companies")
total = cursor.fetchone()['count']
print(f"   Total de empresas: {total}")

if total > 0:
    cursor.execute("SELECT id, nome FROM companies LIMIT 3")
    for row in cursor.fetchall():
        print(f"   - {row['nome']} (ID: {row['id']})")

# 3. Verificar usuários
print("\n3️⃣  USUÁRIOS:")
cursor.execute("SELECT COUNT(*) as count FROM users")
total = cursor.fetchone()['count']
print(f"   Total de usuários: {total}")

if total > 0:
    cursor.execute("SELECT id, email, company_id FROM users LIMIT 3")
    for row in cursor.fetchall():
        print(f"   - {row['email']} (Company: {row['company_id']})")

# 4. Verificar colunas de premiação
print("\n4️⃣  VERIFICAR COLUNAS DE PREMIAÇÃO:")
cursor.execute("PRAGMA table_info(customers)")
columns = [row[1] for row in cursor.fetchall()]
premiacao_cols = ['valor_gasto_atual', 'quantidade_produtos_comprados', 'meta_premiacao_valor', 'meta_premiacao_quantidade']
for col in premiacao_cols:
    status = "✅" if col in columns else "❌"
    print(f"   {status} {col}")

conn.close()

print("\n" + "=" * 60)
print("Se não há clientes, execute em Python:")
print("  python backend/seed_db.py")
print("=" * 60)
