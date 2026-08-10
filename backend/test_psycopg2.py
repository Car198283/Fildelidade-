#!/usr/bin/env python3
import psycopg2

print("Testando conexão psycopg2...\n")

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres",  # Connect to default DB first
        client_encoding="UTF8"
    )
    print("✅ Conexão bem-sucedida!")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(f"Versão PostgreSQL: {cur.fetchone()}")
    conn.close()
except psycopg2.OperationalError as e:
    print(f"❌ Erro Operacional: {e}")
except psycopg2.Error as e:
    print(f"❌ Erro psycopg2: {type(e).__name__}: {e}")
except UnicodeDecodeError as e:
    print(f"❌ Erro de Encoding: {e}")
    print(f"   Posição: {e.start}-{e.end}")
    print(f"   Byte problemático: 0x{e.object[e.start]:02x}")
except Exception as e:
    print(f"❌ Outro erro: {type(e).__name__}: {e}")
