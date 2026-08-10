#!/usr/bin/env python3
import os
import sys

# Diagnóstico de encoding e caminhos

print("=== DIAGNOSTICO ===\n")

# 1. Checar default encoding
print(f"1. Default Encoding: {sys.getdefaultencoding()}")
print(f"   Filesystem Encoding: {sys.getfilesystemencoding()}\n")

# 2. Verificar PATH
import app.config as config_module

print(f"2. Config Module ({config_module.__file__}):")
print(f"   DATABASE_URL type: {type(config_module.settings.database_url)}")
print(f"   DATABASE_URL value: {repr(config_module.settings.database_url)}")
print(f"   DATABASE_URL bytes: {config_module.settings.database_url.encode('utf-8')}\n")

# 3. Tentar parsear
from urllib.parse import urlparse
url = config_module.settings.database_url
print(f"3. Parsing URL:")
try:
    parsed = urlparse(url)
    print(f"   scheme: {parsed.scheme}")
    print(f"   user: {parsed.username}")
    print(f"   password: {repr(parsed.password)}")
    print(f"   host: {parsed.hostname}")
    print(f"   port: {parsed.port}")
    print(f"   db: {parsed.path}")
except Exception as e:
    print(f"   ERROR: {e}\n")

print("\nSe tudo acima OK, o problema está no psycopg2 ao conectar.")
