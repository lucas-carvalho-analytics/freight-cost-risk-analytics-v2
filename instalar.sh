#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════
#  Freight Cost Risk Analytics — Instalador Linux / macOS
#  Uso: bash instalar.sh  (ou duplo-clique se tiver permissão)
# ══════════════════════════════════════════════════════════════
set -euo pipefail

info()  { printf '\n  \033[1;34m▸\033[0m %s\n' "$1"; }
ok()    { printf '  \033[1;32m✅\033[0m %s\n' "$1"; }
warn()  { printf '  \033[1;33m⚠ \033[0m %s\n' "$1"; }
fail()  { printf '  \033[1;31m❌\033[0m %s\n' "$1"; echo; read -rp "  Pressione Enter para sair..."; exit 1; }

REPO_URL="https://github.com/lucas-carvalho-analytics/freight-cost-risk-analytics-v2.git"
REPO_DIR="freight-cost-risk-analytics-v2"

echo ""
echo "  ══════════════════════════════════════════════════════════"
echo "    Freight Cost Risk Analytics — Instalador"
echo "  ══════════════════════════════════════════════════════════"
echo ""
echo "    Este instalador vai preparar o sistema na sua máquina."
echo "    Ele verifica os programas necessários e configura tudo."
echo ""
echo "  ──────────────────────────────────────────────────────────"

# ── 1. Verificar Python ──────────────────────────────────────

info "[1/3] Verificando Python..."

PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    warn "Python não encontrado."
    echo ""
    echo "    O Python é necessário para executar o instalador."
    echo ""

    if [[ "$(uname)" == "Darwin" ]]; then
        echo "    No macOS, instale com:"
        echo "      brew install python3"
        echo ""
        echo "    Ou baixe em: https://www.python.org/downloads/"
        python3 -c "import webbrowser; webbrowser.open('https://www.python.org/downloads/')" 2>/dev/null || true
    else
        echo "    No Ubuntu/Debian:"
        echo "      sudo apt install python3"
        echo ""
        echo "    No Fedora/RHEL:"
        echo "      sudo dnf install python3"
        echo ""
        echo "    Ou baixe em: https://www.python.org/downloads/"
    fi
    echo ""
    fail "Instale o Python e execute este instalador novamente."
fi

ok "Python encontrado ($PYTHON_CMD)."

# ── 2. Verificar Docker ──────────────────────────────────────

info "[2/3] Verificando Docker..."

if ! command -v docker &>/dev/null; then
    warn "Docker não encontrado."
    echo ""
    echo "    O Docker é necessário para rodar o sistema."
    echo ""

    if [[ "$(uname)" == "Darwin" ]]; then
        URL="https://docs.docker.com/desktop/install/mac-install/"
    else
        URL="https://docs.docker.com/engine/install/"
    fi

    echo "    📥 Link: $URL"
    $PYTHON_CMD -c "import webbrowser; webbrowser.open('$URL')" 2>/dev/null || true
    echo ""
    fail "Instale o Docker e execute este instalador novamente."
fi

if ! docker info &>/dev/null; then
    warn "Docker está instalado mas não está rodando."
    echo ""
    echo "    Inicie o Docker Desktop e aguarde ele ficar pronto."
    echo "    Depois execute este instalador novamente."
    echo ""
    fail "Docker precisa estar rodando."
fi

ok "Docker instalado e rodando."

# ── 3. Verificar Git ─────────────────────────────────────────

info "[3/3] Verificando Git..."

if ! command -v git &>/dev/null; then
    warn "Git não encontrado."
    echo ""
    echo "    📥 Link: https://git-scm.com/downloads"
    echo ""
    $PYTHON_CMD -c "import webbrowser; webbrowser.open('https://git-scm.com/downloads')" 2>/dev/null || true
    fail "Instale o Git e execute este instalador novamente."
fi

ok "Git encontrado."

# ── Todos os requisitos OK ───────────────────────────────────

echo ""
echo "  ──────────────────────────────────────────────────────────"
ok "Todos os programas necessários estão instalados!"
echo "  ──────────────────────────────────────────────────────────"

# ── Encontrar ou baixar o projeto ────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/quick-start.py" ]; then
    info "Projeto encontrado. Iniciando instalação automática..."
    cd "$SCRIPT_DIR"
    $PYTHON_CMD quick-start.py
elif [ -f "quick-start.py" ]; then
    info "Projeto encontrado. Iniciando instalação automática..."
    $PYTHON_CMD quick-start.py
elif [ -d "$REPO_DIR" ] && [ -f "$REPO_DIR/quick-start.py" ]; then
    info "Projeto encontrado na subpasta. Iniciando..."
    cd "$REPO_DIR"
    $PYTHON_CMD quick-start.py
else
    info "Baixando o projeto..."
    git clone "$REPO_URL" || fail "Falha ao baixar. Verifique sua conexão."
    cd "$REPO_DIR"
    info "Iniciando instalação automática..."
    $PYTHON_CMD quick-start.py
fi
