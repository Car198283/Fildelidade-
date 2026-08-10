#!/usr/bin/env python3
"""
Criar usuários com senha padrão para testes
"""
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

db_path = Path("bartcellos_loyalty.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

senha_hash = generate_password_hash("123456")

print("=" * 60)
print("  ATUALIZANDO SENHA DOS USUÁRIOS")
print("=" * 60)

# Atualizar TODOS os usuários para senha "123456"
cursor.execute("UPDATE users SET senha_hash = ?", (senha_hash,))
print("✅ Todas as senhas atualizadas para: 123456")

conn.commit()

# Listar usuários
cursor.execute("SELECT id, email, company_id FROM users")
usuarios = cursor.fetchall()

print(f"\n✅ USUÁRIOS DISPONÍVEIS:")
for u in usuarios:
    cursor.execute("SELECT COUNT(*) FROM customers WHERE company_id = ?", (u[2],))
    total = cursor.fetchone()[0]
    print(f"   • {u[1]} (Company: {u[2]}, Clientes: {total})")

conn.close()

print("\n" + "=" * 60)
print("✅ Todos os usuários têm senha: 123456")
print("=" * 60)
