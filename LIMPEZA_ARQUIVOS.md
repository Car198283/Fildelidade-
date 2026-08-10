📋 ARQUIVOS PARA DELETAR - ANÁLISE COMPLETA

=== 🔴 SCRIPTS DE DEBUG/TEST (DESNECESSÁRIOS - PODEM SER REMOVIDOS) ===

1. debug_cliente.py - Script antigo de debug, não tem uso
2. debug_connection.py - Script antigo de debug, não tem uso
3. debug_token.py - Script antigo de debug de token JWT
4. debug_token_new.py - Script duplicado de debug de token
5. diagnostico_env.bat - Script antigo de diagnóstico ambiente
6. diagnostico_mobile.py - Script antigo de diagnóstico mobile
7. diagnostico_premiacao.py - Script de diagnóstico, funcionalidade integrada em teste_funcional_completo.py
8. test_auth.py - Script antigo de teste de autenticação
9. test_auth_api.py - Script duplicado de teste de autenticação
10. test_complete.py - Script antigo de teste completo
11. test_fidelidade_total.py - Script antigo de teste fidelidade
12. test_integrated_debug.py - Script antigo de teste integrated
13. test_login_debug.py - Script antigo de teste login
14. test_psycopg2_direct.py - Script antigo de teste PostgreSQL
15. test_psycopg2_kwargs.py - Script duplicado de teste PostgreSQL

TOTAL: 15 arquivos de debug/test para deletar

=== 🔴 SCRIPTS DE INICIALIZAÇÃO DUPLICADOS ===

1. run_new.bat - Versão antiga de run.bat
2. run.ps1 - Script PowerShell obsoleto (use run.bat)
3. run.sh - Script Linux/Mac obsoleto (Windows é priority)
4. run_backend.py - Script antigo de inicialização backend
5. start_pisthi.py - Script antigo de teste

TOTAL: 5 scripts duplicados (manter apenas run.bat)

=== 🔴 DOCUMENTAÇÃO DUPLICADA/DESNECESSÁRIA ===

1. CHANGELOG_FIDELIDADE_TOTAL_v2.1.md - Versão antiga de changelog
2. CHANGELOG_v2.0.md - Versão antiga de changelog (manter apenas CHANGELOG_PREMIACAO_v1.0.md)
3. README_V2_SUMMARY.txt - Versão antiga de README
4. COMO_RODAR.md - Documentação antiga
5. SOLUCAO_LOGIN.md - Documentação específica resolvida
6. SISTEMA_FUNCIONANDO.md - Documentação específica resolvida
7. PROXIMOS_PASSOS.md - Documentação específica resolvida
8. 00_COMECE_AQUI.txt - Redundante com QUICK_START.md
9. START_AQUI.md - Redundante com QUICK_START.md
10. QUICK_REFERENCE.txt - Documentação genérica não más precisamente necessária
11. ERRO_NODE_NAO_INSTALADO.md - Documentação específica de erro resolvi
12. CORRIGIR_PATH_WINDOWS.md - Documentação específica resolvi
13. INSTALE_PRE_REQUISITOS.md - Informação já em README.md
14. MOBILE_CAPTURE_GUIDE.md - Pode manter se for usar mobile

TOTAL: Pode deletar 13 documentos (manter: README.md, ARCHITECTURE.md, API_EXAMPLES.md, PROJECT_SUMMARY.md, DEPLOYMENT.md, RESUMO_PWA_MOBILE.md, CHANGELOG_PREMIACAO_v1.0.md)

=== 🔴 SCRIPTS DE SETUP JÁ EXECUTADOS ===

1. criar_credenciais_padrao.py - Script setup, já foi executado
2. create_tables.sql - Script setup, já foi executado (via ORM agora)
3. setup.py - Script setup, já foi executado
4. MOVER_PARA_C_DRIVE.bat - Script setup específico, não mais necessário

TOTAL: 4 scripts para deletar

=== 🟡 ARQUIVO CONFIG ===

1. package-lock.json - Pode ser regenerado (npm install), mas é bom manter

=== 📊 RESUMO GERAL ===

Total de arquivos para DELETAR: 37

- Scripts Debug/Test: 15
- Scripts Duplicados: 5
- Documentação Redundante: 13
- Scripts Setup: 4

Mantém:
✅ run.bat (único!)
✅ README.md
✅ ARCHITECTURE.md
✅ API_EXAMPLES.md
✅ PROJECT_SUMMARY.md
✅ DEPLOYMENT.md
✅ RESUMO_PWA_MOBILE.md
✅ CHANGELOG_PREMIACAO_v1.0.md
✅ docker-compose.yml
✅ .gitignore
✅ bartcellos_loyalty.db
✅ backend/ (pasta)
✅ frontend/ (pasta)
✅ migrations/ (pasta)
✅ teste_funcional_completo.py (teste novo, funcional)
✅ migrate_premiacao.py (necessário para migrations)

=== 🔥 COMANDO PARA DELETAR TUDO (PowerShell) ===

# Deletar arquivos de debug (15 arquivos)

Remove-Item debug*\*.py
Remove-Item diagnostico_env.bat, diagnostico_mobile.py, diagnostico_premiacao.py
Remove-Item test*\*.py

# Deletar scripts duplicados

Remove-Item run_new.bat, run.ps1, run.sh, run_backend.py, start_pisthi.py

# Deletar documentação redundante

Remove-Item CHANGELOG_v2.0.md, CHANGELOG_FIDELIDADE_TOTAL_v2.1.md, README_V2_SUMMARY.txt
Remove-Item COMO_RODAR.md, SOLUCAO_LOGIN.md, SISTEMA_FUNCIONANDO.md
Remove-Item PROXIMOS_PASSOS.md, 00_COMECE_AQUI.txt, START_AQUI.md
Remove-Item QUICK_REFERENCE.txt, ERRO_NODE_NAO_INSTALADO.md, CORRIGIR_PATH_WINDOWS.md
Remove-Item INSTALE_PRE_REQUISITOS.md

# Deletar scripts setup

Remove-Item criar_credenciais_padrao.py, create_tables.sql, setup.py, MOVER_PARA_C_DRIVE.bat

AÇÃO RECOMENDADA:
1️⃣ Execute os comandos PowerShell acima
2️⃣ Sobrará apenas o essencial
3️⃣ Projeto mais limpo e organizado
4️⃣ Nenhuma funcionalidade perdida
