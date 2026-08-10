@echo off
REM ====================================
REM FIDELIDADE TOTAL v2.1 - SCRIPT START
REM ====================================

setlocal enabledelayedexpansion

echo.
echo [94m============================================================[0m
echo [94m  FIDELIDADE TOTAL v2.1[0m
echo [94m  Iniciando aplicacao completa...[0m
echo [94m============================================================[0m
echo.

REM Verificar estrutura
if not exist "backend\" (
    echo [91m[ERRO] Execute esse script na raiz do projeto[0m
    echo.
    echo Exemplo:
    echo   cd c:\Users\caduf\OneDrive\Desktop\Bartcellos
    echo  
    
    echo.
    pause
    exit /b 1
)

echo [92m[OK] Estrutura de pastas encontrada[0m
echo.

REM ====================================
REM 1. Verificar Python
REM ====================================
echo [94m[1/2] Verificando Python...[0m
python --version >nul 2>&1
if errorlevel 1 (
    echo [91m[ERRO] Python nao encontrado![0m
    echo.
    echo Instale Python 3.11+ em: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [92m[OK] %PYTHON_VERSION%[0m

REM ====================================
REM 2. Verificar Node.js
REM ====================================
echo.
echo [94m[2/2] Verificando Node.js...[0m
node --version >nul 2>&1
if errorlevel 1 (
    echo [91m[ERRO] Node.js nao encontrado![0m
    echo.
    echo Instale Node.js 18+ em: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [92m[OK] Node %NODE_VERSION%[0m

REM ====================================
REM Instalar dependencias
REM ====================================
echo.
echo [93m[...] Instalando dependencias Python...[0m
cd backend
pip install -q -r requirements.txt
cd ..
echo [92m[OK] Dependencias Python instaladas[0m

echo [93m[...] Instalando dependencias Node.js...[0m
cd frontend
if not exist "node_modules" (
    echo [93mPrimeira execucao - podem levar alguns minutos...[0m
    call npm install --silent
)
cd ..
echo [92m[OK] Dependencias Node.js instaladas[0m

REM ====================================
REM Executar Migracao de Premiacao
REM ====================================
echo.
echo [94m[3/3] Executando migracao de premiacao...[0m
python migrate_premiacao.py
if errorlevel 1 (
    echo [91m[WARN] Migracao de premiacao nao completada[0m
    echo [93mVerifique o banco de dados manualmente[0m
) else (
    echo [92m[OK] Migracao de premiacao aplicada[0m
)

REM ====================================
REM Limpar Cache do Frontend
REM ====================================
echo.
echo [93m[...] Limpando cache do Frontend (Vite)...[0m
if exist "frontend\node_modules\.vite" (
    rmdir /s /q "frontend\node_modules\.vite" >nul 2>&1
)
if exist "frontend\.vite" (
    rmdir /s /q "frontend\.vite" >nul 2>&1
)
if exist "frontend\dist" (
    rmdir /s /q "frontend\dist" >nul 2>&1
)
echo [92m[OK] Cache limpo[0m

REM ====================================
REM Pronto para iniciar
REM ====================================
echo.
echo [92m============================================================[0m
echo [92m  TUDO PRONTO PARA INICIAR![0m
echo [92m============================================================[0m
echo.
echo [93mPressione qualquer tecla para continuar...[0m
echo.

pause

set LOCAL_IP=
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "$route = Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Sort-Object RouteMetric | Select-Object -First 1; if ($route) { Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $route.InterfaceIndex | Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } | Select-Object -First 1 -ExpandProperty IPAddress }"') do set LOCAL_IP=%%i
if "%LOCAL_IP%"=="" (
    set APP_URL=http://localhost:3003/?reset=20260518
    set PUBLIC_APP_URL=http://localhost:3003
) else (
    set APP_URL=http://%LOCAL_IP%:3003/?reset=20260518
    set PUBLIC_APP_URL=http://%LOCAL_IP%:3003
)

REM ====================================
REM Iniciar Backend
REM ====================================
echo.
echo [94m[INICIANDO] Backend em http://localhost:8000[0m
echo [93mAbrindo nova janela...[0m
echo.

start "Fidelidade Total - Backend" cmd /k "cd /d %CD% && python run_backend.py"

REM Aguardar backend inicializar
timeout /t 6 /nobreak >nul

REM ====================================
REM Iniciar Frontend
REM ====================================
echo [94m[INICIANDO] Frontend em http://localhost:3003[0m
echo [93mAbrindo nova janela...[0m
echo.

start "Fidelidade Total - Frontend" cmd /k "cd /d %CD%\frontend && set VITE_PUBLIC_APP_URL=%PUBLIC_APP_URL%&& npm.cmd run build && npm.cmd run preview -- --host 0.0.0.0 --port 3003"

REM Aguardar frontend inicializar
timeout /t 4 /nobreak >nul

REM ====================================
REM Abrir navegador
REM ====================================
echo [92m[OK] Tentando abrir navegador...[0m
start %APP_URL%

echo.
echo [92m============================================================[0m
echo [92m  APLICACAO INICIADA COM SUCESSO![0m
echo [92m============================================================[0m
echo.
echo [92mFrontend:   %APP_URL%[0m
echo [92mBackend:    http://localhost:8000[0m
echo [92mAPI Docs:   http://localhost:8000/docs[0m
echo [93mNo celular, use o mesmo endereco do Frontend acima na mesma rede Wi-Fi.[0m
echo.
echo [93mBanco de dados: bartcellos_loyalty.db (criado automaticamente)[0m
echo [93mPara parar: Feche as duas janelas abertas[0m
echo.

endlocal
