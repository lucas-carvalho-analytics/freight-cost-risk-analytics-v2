@echo off
chcp 65001 >nul 2>&1
title Freight Cost Risk Analytics - Instalador

echo.
echo ══════════════════════════════════════════════════════════════
echo   Freight Cost Risk Analytics — Instalador Windows
echo ══════════════════════════════════════════════════════════════
echo.
echo   Este instalador vai preparar o sistema na sua maquina.
echo   Ele verifica os programas necessarios e configura tudo.
echo.
echo ──────────────────────────────────────────────────────────────

:: ── Verificar Python ────────────────────────────────────────

echo.
echo   [1/3] Verificando Python...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   ❌ Python nao encontrado.
    echo.
    echo   O Python e necessario para executar o instalador.
    echo   Vamos abrir a pagina de download para voce.
    echo.
    echo   IMPORTANTE: Marque a opcao "Add Python to PATH"
    echo   durante a instalacao.
    echo.
    start https://www.python.org/downloads/
    echo   📥 Link: https://www.python.org/downloads/
    echo.
    echo   Depois de instalar o Python, feche esta janela
    echo   e execute o instalador novamente.
    echo.
    pause
    exit /b 1
)

echo   ✅ Python encontrado.

:: ── Verificar Docker ────────────────────────────────────────

echo.
echo   [2/3] Verificando Docker...

where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   ❌ Docker nao encontrado.
    echo.
    echo   O Docker e necessario para rodar o sistema.
    echo   Vamos abrir a pagina de download para voce.
    echo.
    start https://docs.docker.com/desktop/install/windows-install/
    echo   📥 Link: https://docs.docker.com/desktop/install/windows-install/
    echo.
    echo   Depois de instalar o Docker Desktop:
    echo   1. Reinicie o computador se pedido
    echo   2. Abra o Docker Desktop
    echo   3. Aguarde ele iniciar completamente
    echo   4. Execute o instalador novamente
    echo.
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   ⚠  Docker esta instalado, mas nao esta rodando.
    echo.
    echo   Abra o Docker Desktop e aguarde ele iniciar.
    echo   Depois execute o instalador novamente.
    echo.
    pause
    exit /b 1
)

echo   ✅ Docker instalado e rodando.

:: ── Verificar Git ───────────────────────────────────────────

echo.
echo   [3/3] Verificando Git...

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   ❌ Git nao encontrado.
    echo.
    echo   O Git e necessario para baixar o projeto.
    echo   Vamos abrir a pagina de download para voce.
    echo.
    start https://git-scm.com/downloads
    echo   📥 Link: https://git-scm.com/downloads
    echo.
    echo   Depois de instalar o Git, execute o instalador novamente.
    echo.
    pause
    exit /b 1
)

echo   ✅ Git encontrado.

:: ── Todos os requisitos OK ──────────────────────────────────

echo.
echo ──────────────────────────────────────────────────────────────
echo   ✅ Todos os programas necessarios estao instalados!
echo ──────────────────────────────────────────────────────────────

:: ── Verificar se estamos no diretório do projeto ────────────

echo.
if exist "quick-start.py" (
    echo   Projeto encontrado no diretorio atual.
    echo   Iniciando instalacao automatica...
    echo.
    python quick-start.py
) else if exist "freight-cost-risk-analytics-v2\quick-start.py" (
    echo   Projeto encontrado na subpasta.
    echo   Iniciando instalacao automatica...
    echo.
    cd freight-cost-risk-analytics-v2
    python quick-start.py
) else (
    echo   Baixando o projeto...
    echo.
    git clone https://github.com/lucas-carvalho-analytics/freight-cost-risk-analytics-v2.git
    if %errorlevel% neq 0 (
        echo.
        echo   ❌ Falha ao baixar o projeto.
        echo   Verifique sua conexao com a internet.
        echo.
        pause
        exit /b 1
    )
    cd freight-cost-risk-analytics-v2
    echo.
    echo   Iniciando instalacao automatica...
    echo.
    python quick-start.py
)
