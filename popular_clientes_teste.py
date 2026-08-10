#!/usr/bin/env python3
"""
Popolar clientes com pontos para teste
"""
import sqlite3
from pathlib import Path

db_path = Path("bartcellos_loyalty.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("  POPULANDO CLIENTES COM PONTOS DE TESTE")
print("=" * 60)

# Obter clientes
cursor.execute("SELECT id, nome FROM customers WHERE ativo = 1")
clientes = cursor.fetchall()

print(f"\n🎯 Atualizando {len(clientes)} clientes com pontos de teste...\n")

updates = [
    (100, "100% premiado"),
    (85, "85% - Quase premiado"),
    (75, "75% - Tentando"),
    (150, "150% - Super premiado")
]

for i, cliente in enumerate(clientes):
    pontos, descricao = updates[i % len(updates)]
    meta = 100  # Meta padrão é 100
    
    cursor.execute("""
        UPDATE customers 
        SET pontos = ?, meta_premiacao_quantidade = ?, meta_premiacao_valor = ?
        WHERE id = ?
    """, (pontos, meta, meta * 10, cliente['id']))
    
    percentual = (pontos / meta) * 100
    status = ""
    if percentual >= 100:
        status = "🏆 PREMIADO"
    elif percentual >= 80:
        status = "⚡ QUASE PREMIADO"
    else:
        status = "📊 PROGRESSO"
    
    print(f"✅ {cliente['nome']}")
    print(f"   └─ {pontos} pontos ({percentual}%) {status} - {descricao}\n")

conn.commit()

# Verificar resultado
print("\n" + "=" * 60)
print("  RESULTADO FINAL")
print("=" * 60)

cursor.execute("""
    SELECT nome, pontos, 
    CAST(pontos * 100.0 / 100 AS INTEGER) as percentual
    FROM customers 
    WHERE ativo = 1
    ORDER BY pontos DESC
""")

print("\nClientes após atualização:")
for row in cursor.fetchall():
    print(f"   {row['nome']}: {row['pontos']} pontos ({row['percentual']}%)")

conn.close()

print("\n" + "=" * 60)
print("✅ Clientes atualizados com sucesso!")
print("   Reabra o Dashboard para ver os cards aparecerem!")
print("=" * 60)
