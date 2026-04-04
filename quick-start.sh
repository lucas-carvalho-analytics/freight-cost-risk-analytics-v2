#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# quick-start.sh
# Sobe o sistema completo com 1 comando.
# Uso: bash quick-start.sh
# ============================================================

COMPOSE_FILE="docker-compose.demo.yml"
ENV_FILE="deploy/demo.env"
ENV_EXAMPLE="deploy/demo.env.example"
DEMO_EMAIL="admin@demo.local"
DEMO_PASSWORD="demo1234"
DEMO_PORT="${DEMO_PORT:-8080}"
HEALTH_TIMEOUT=120

# ── helpers ──────────────────────────────────────────────────

info()  { printf '\n\033[1;34m▸ %s\033[0m\n' "$1"; }
ok()    { printf '\033[1;32m✅ %s\033[0m\n' "$1"; }
warn()  { printf '\033[1;33m⚠  %s\033[0m\n' "$1"; }
fail()  { printf '\033[1;31m❌ %s\033[0m\n' "$1"; exit 1; }

compose() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

# ── 1. Pre-requisitos ────────────────────────────────────────

info "Verificando pré-requisitos..."

command -v docker >/dev/null 2>&1 || fail "Docker não encontrado. Instale em https://docs.docker.com/get-docker/"
docker compose version >/dev/null 2>&1 || fail "docker compose não encontrado. Atualize o Docker Desktop."
docker info >/dev/null 2>&1 || fail "Docker não está rodando. Inicie o Docker Desktop e tente novamente."

ok "Docker está instalado e rodando."

# ── 2. Arquivo de ambiente ───────────────────────────────────

info "Preparando arquivo de configuração..."

if [ -f "$ENV_FILE" ]; then
  warn "Arquivo $ENV_FILE já existe. Usando o existente."
else
  if [ ! -f "$ENV_EXAMPLE" ]; then
    fail "Arquivo $ENV_EXAMPLE não encontrado. Verifique a estrutura do projeto."
  fi

  # Gera JWT secret aleatório e seguro
  JWT_SECRET=$(openssl rand -base64 48 2>/dev/null || head -c 64 /dev/urandom | base64 | tr -d '\n')

  cp "$ENV_EXAMPLE" "$ENV_FILE"
  # Substitui o placeholder do JWT_SECRET_KEY
  if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SECRET}|" "$ENV_FILE"
  else
    sed -i "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT_SECRET}|" "$ENV_FILE"
  fi

  ok "Arquivo $ENV_FILE criado com secret seguro gerado automaticamente."
fi

# Lê a porta configurada
DEMO_PORT=$(grep -E '^DEMO_PORT=' "$ENV_FILE" | cut -d'=' -f2 || echo "8080")
DEMO_PORT="${DEMO_PORT:-8080}"

# ── 3. Subir o stack ─────────────────────────────────────────

info "Iniciando o sistema (isso pode levar alguns minutos na primeira vez)..."

compose up --build -d

ok "Containers iniciados."

# ── 4. Aguardar health checks ────────────────────────────────

info "Aguardando os serviços ficarem saudáveis..."

elapsed=0
while [ $elapsed -lt $HEALTH_TIMEOUT ]; do
  pg_health=$(compose ps postgres --format '{{.Health}}' 2>/dev/null || echo "")
  be_health=$(compose ps backend --format '{{.Health}}' 2>/dev/null || echo "")
  fe_health=$(compose ps frontend --format '{{.Health}}' 2>/dev/null || echo "")

  if [[ "$pg_health" == *"healthy"* ]] && [[ "$be_health" == *"healthy"* ]] && [[ "$fe_health" == *"healthy"* ]]; then
    ok "Todos os serviços estão saudáveis."
    break
  fi

  sleep 3
  elapsed=$((elapsed + 3))
  printf '.'
done

if [ $elapsed -ge $HEALTH_TIMEOUT ]; then
  echo ""
  warn "Timeout aguardando health checks. Verificando status atual..."
  compose ps
  fail "Os serviços não ficaram saudáveis em ${HEALTH_TIMEOUT}s. Verifique os logs com: docker compose --env-file $ENV_FILE -f $COMPOSE_FILE logs"
fi

# ── 5. Criar admin de demo ───────────────────────────────────

info "Criando usuário administrador de demonstração..."

compose exec -T backend python -m app.scripts.seed_admin \
  --email "$DEMO_EMAIL" \
  --full-name "Admin Demo" \
  --password "$DEMO_PASSWORD" \
  2>/dev/null || warn "Admin pode já existir (isso é normal se você já rodou este script antes)."

ok "Usuário de demonstração configurado."

# ── 6. Gerar e importar dataset ──────────────────────────────

info "Gerando dataset de demonstração..."

compose exec -T backend python -c "
import sys, os
sys.path.insert(0, '/app')
os.chdir('/app')

# Gera o CSV dentro do container
exec(open('/app/../gerar_dataset_logistica_pe.py', 'r').read() if os.path.exists('/app/../gerar_dataset_logistica_pe.py') else '')
" 2>/dev/null || true

# Tenta gerar no host e copiar para dentro
if ! compose exec -T backend test -f /app/data/dataset_operacoes_logisticas_pe.csv 2>/dev/null; then
  # Gera no host se Python estiver disponível
  if command -v python3 >/dev/null 2>&1; then
    python3 gerar_dataset_logistica_pe.py 2>/dev/null || true
    mkdir -p backend/data
    if [ -f dataset_operacoes_logisticas_pe.csv ]; then
      cp dataset_operacoes_logisticas_pe.csv backend/data/
      rm -f dataset_operacoes_logisticas_pe.csv
    fi
  else
    warn "Python3 não encontrado no host. O dashboard vai abrir sem dados de demonstração."
    warn "Você pode importar dados depois seguindo o tutorial em docs/tutorial-usuario-final.md"
  fi
fi

# Importa se o arquivo existe
if compose exec -T backend test -f /app/data/dataset_operacoes_logisticas_pe.csv 2>/dev/null; then
  info "Importando dados para o banco..."
  compose exec -T backend python -m app.scripts.import_shipments /app/data/dataset_operacoes_logisticas_pe.csv 2>&1 || true
  ok "Dados de demonstração importados."
elif [ -f backend/data/dataset_operacoes_logisticas_pe.csv ]; then
  info "Importando dados para o banco..."
  compose exec -T backend python -m app.scripts.import_shipments /app/data/dataset_operacoes_logisticas_pe.csv 2>&1 || true
  ok "Dados de demonstração importados."
fi

# ── 7. Resultado final ───────────────────────────────────────

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf '\033[1;32m'
echo "  ✅  Sistema pronto!"
printf '\033[0m'
echo ""
echo "  Abra no navegador:"
echo "    http://127.0.0.1:${DEMO_PORT}"
echo ""
echo "  Login:"
echo "    E-mail:  ${DEMO_EMAIL}"
echo "    Senha:   ${DEMO_PASSWORD}"
echo ""
echo "  Comandos úteis:"
echo "    Parar:      docker compose --env-file $ENV_FILE -f $COMPOSE_FILE down"
echo "    Subir:      docker compose --env-file $ENV_FILE -f $COMPOSE_FILE up -d"
echo "    Ver logs:   docker compose --env-file $ENV_FILE -f $COMPOSE_FILE logs -f"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
