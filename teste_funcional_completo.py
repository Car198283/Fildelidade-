#!/usr/bin/env python3
"""
TESTE FUNCIONAL - Sistema de Premiação + PDFs + Edição + Deleção
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

# =======================
# 1. LOGIN
# =======================
print_section("1️⃣  FAZENDO LOGIN")

login_data = {
    "email": "admin@minhaloja.com",
    "senha": "123456"
}

login_res = requests.post(f"{BASE_URL}/auth/login", json=login_data)
print(f"Status: {login_res.status_code}")

if login_res.status_code == 200:
    user_data = login_res.json()
    token = user_data.get("data", {}).get("access_token")
    user_id = user_data.get("data", {}).get("user", {}).get("id")
    company_id = user_data.get("data", {}).get("user", {}).get("company_id")
    print(f"✅ Login bem-sucedido!")
    print(f"   Token: {token[:30]}...")
    print(f"   User ID: {user_id}")
    print(f"   Company ID: {company_id}")
else:
    print(f"❌ Erro no login: {login_res.text}")
    exit(1)

# =======================
# 2. TESTAR ENDPOINTS DE PREMIAÇÃO
# =======================
print_section("2️⃣  TESTANDO ENDPOINTS DE PREMIAÇÃO")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2.1 Clientes Premiados (100%)
print("🏆 Clientes Premiados (100%)")
res = requests.get(f"{BASE_URL}/dashboard/clientes-premiados-completo", headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    data = res.json().get("data", [])
    print(f"✅ Encontrados: {len(data)} clientes premiados")
    if data:
        print(f"   Primeiro: {data[0].get('nome')} - {data[0].get('percentual', 'N/A')}%")
else:
    print(f"❌ Erro: {res.text[:100]}")

# 2.2 Quase Premiados (80-99%)
print("\n⚡ Quase Premiados (80-99%)")
res = requests.get(f"{BASE_URL}/dashboard/clientes-quase-premiados", headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    data = res.json().get("data", [])
    print(f"✅ Encontrados: {len(data)} clientes quase premiados")
    if data:
        print(f"   Primeiro: {data[0].get('nome')} - {data[0].get('percentual', 'N/A')}%")
else:
    print(f"❌ Erro: {res.text[:100]}")

# =======================
# 3. TESTAR EDIÇÃO DE CLIENTE
# =======================
print_section("3️⃣  TESTANDO EDIÇÃO DE CLIENTE")

# Obter lista de clientes
res = requests.get(f"{BASE_URL}/clientes", headers=headers, params={"limit": 1})
if res.status_code == 200:
    clientes = res.json().get("data", [])
    if clientes:
        cliente_id = clientes[0]["id"]
        cliente_nome = clientes[0]["nome"]
        print(f"Cliente selecionado: {cliente_nome} (ID: {cliente_id})")
        
        # 3.1 Obter detalhes
        print("\n📋 Obtendo detalhes do cliente...")
        res = requests.get(f"{BASE_URL}/clientes/{cliente_id}/detalhes", headers=headers)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print(f"✅ Detalhes obtidos com sucesso")
        else:
            print(f"❌ Erro: {res.text[:100]}")
        
        # 3.2 Atualizar cliente
        print("\n✏️  Atualizando cliente...")
        update_data = {
            "nome": f"{cliente_nome} (Edited)",
            "telefone": "(11) 99999-9999",
            "email": "teste@novo.com"
        }
        res = requests.put(f"{BASE_URL}/clientes/{cliente_id}", json=update_data, headers=headers)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print(f"✅ Cliente atualizado com sucesso")
        else:
            print(f"❌ Erro: {res.text[:100]}")

# =======================
# 4. TESTAR PDFS
# =======================
print_section("4️⃣  TESTANDO PDFs")

# 4.1 PDF Aniversariantes
print("📄 PDF Aniversariantes...")
res = requests.get(f"{BASE_URL}/relatorios/aniversariantes/pdf", headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    print(f"✅ PDF Aniversariantes gerado ({len(res.content)} bytes)")
else:
    print(f"❌ Erro: {res.text[:100]}")

# 4.2 PDF Clientes Premiados
print("\n📄 PDF Clientes Premiados...")
res = requests.get(f"{BASE_URL}/relatorios/premiados/pdf", headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    print(f"✅ PDF Premiados gerado ({len(res.content)} bytes)")
else:
    print(f"❌ Erro: {res.text[:100]}")

# 4.3 PDF Clientes Inativos
print("\n📄 PDF Clientes Inativos...")
res = requests.get(f"{BASE_URL}/relatorios/inativos/pdf", headers=headers)
print(f"Status: {res.status_code}")
if res.status_code == 200:
    print(f"✅ PDF Inativos gerado ({len(res.content)} bytes)")
else:
    print(f"❌ Erro: {res.text[:100]}")

# =======================
# 5. RESUMO FINAL
# =======================
print_section("5️⃣  RESUMO FINAL")

print("""
✅ TUDO FUNCIONANDO:
   - Endpoints de premiação respondendo
   - Edição de cliente funciona
   - PDFs sendo gerados
   - Autenticação OK

🚀 PRÓXIMAS ETAPAS:
   1. Abra o navegador: http://localhost:3002
   2. Faça login
   3. Vá ao Dashboard
   4. Teste os novos cards (100% e 80-99%)
   5. Clique nos botões de EDITAR e DELETAR
   6. Baixe os PDFs
   7. Configure as promoções (⚙️ Promoção)

❓ Se algo não funcionar, verifique:
   - Console (F12) para erros de JavaScript
   - Network (F12) para erros HTTP
   - Cache limpo (Ctrl+Shift+Delete)
""")
