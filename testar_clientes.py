import requests
import json

# Tentar ambos os usuários
usuarios = [
    {'email': 'cadufcostajf@gmail.com', 'senha': '123456'},
    {'email': 'admin@minhaloja.com', 'senha': '123456'},
]

for user in usuarios:
    print(f"\n🔐 Tentando: {user['email']}")
    login_data = {'email': user['email'], 'senha': user['senha']}
    login_res = requests.post('http://127.0.0.1:8000/auth/login', json=login_data)

    if login_res.status_code == 200:
        token = login_res.json()['data']['access_token']
        print('✅ Login OK!')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Teste: Listar clientes
        print("📋 GET /clientes")
        res = requests.get('http://127.0.0.1:8000/clientes', headers=headers)
        print(f"Status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            print(f"Clientes: {len(data.get('data', []))}")
            for cliente in data.get('data', [])[:2]:
                print(f"  - {cliente.get('nome')}")
        break
    else:
        print(f"❌ Erro: {login_res.text[:100]}")

