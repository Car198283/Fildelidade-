#!/usr/bin/env python3
import psycopg2
import sys

print("Analisando erro de encoding...\n")

# Byte 0xe7 é 'ç' em Latin-1
PROBLEMATIC_BYTE = b'\xe7'  # ç em Latin-1

try:
    # Tenta com Latin1
    print("1. Tentando com client_encoding='LATIN1':")
    conn = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        user="postgres",
        password="postgres",
        database="postgres",
        client_encoding="LATIN1"
    )
    print("✅ Conexão bem-sucedida com LATIN1!")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    result = cur.fetchone()
    print(f"Versão PostgreSQL: {result}")
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {type(e).__name__}: {e}\n")
    
    print("2. Analisando erro:")
    print(f"   O byte 0xe7 é 'ç' em Latin-1")
    print(f"   Pode estar em uma mensagem de erro do PostgreSQL")
    print(f"   Posição 72 sugere estar em um caminho ou msg de Status\n")
    
    print("3. Possíveis causas:")
    print("   a) PostgreSQL instalado em caminho com 'ç' (ex: Usuário 'São Paulo')")
    print("   b) Locale do sistema em ISO-8859-1 em vez de UTF-8")
    print("   c) Nome de usuário ou senha com caracteres especiais")
