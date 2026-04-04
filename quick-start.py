#!/usr/bin/env python3
"""
quick-start.py — Setup completo do sistema com 1 comando.

Funciona em Linux, macOS e Windows.
Uso: python quick-start.py
"""
from __future__ import annotations

import os
import platform
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ── Configuração ─────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.demo.yml"
ENV_EXAMPLE = PROJECT_ROOT / "deploy" / "demo.env.example"
ENV_FILE = PROJECT_ROOT / "deploy" / "demo.env"
DATASET_GENERATOR = PROJECT_ROOT / "gerar_dataset_logistica_pe.py"
BACKEND_DATA_DIR = PROJECT_ROOT / "backend" / "data"

DEMO_EMAIL = "admin@demo.local"
DEMO_PASSWORD = "demo1234"
HEALTH_TIMEOUT = 150  # segundos
HEALTH_INTERVAL = 4   # segundos entre tentativas

OS_NAME = platform.system()  # "Linux", "Darwin", "Windows"


# ── Helpers ──────────────────────────────────────────────────

def info(msg: str) -> None:
    print(f"\n\033[1;34m▸ {msg}\033[0m")


def ok(msg: str) -> None:
    print(f"\033[1;32m✅ {msg}\033[0m")


def warn(msg: str) -> None:
    print(f"\033[1;33m⚠  {msg}\033[0m")


def fail(msg: str) -> None:
    print(f"\033[1;31m❌ {msg}\033[0m")
    sys.exit(1)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Executa comando e retorna o resultado."""
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def compose_cmd() -> list[str]:
    """Retorna o comando base do docker compose para este projeto."""
    return [
        "docker", "compose",
        "--env-file", str(ENV_FILE),
        "-f", str(COMPOSE_FILE),
    ]


def compose_run(*args: str, **kwargs) -> subprocess.CompletedProcess:
    """Executa docker compose com os argumentos fornecidos."""
    return run([*compose_cmd(), *args], **kwargs)


# ── 1. Detecção do sistema operacional ───────────────────────

def show_os_info() -> None:
    info(f"Sistema operacional detectado: {OS_NAME} ({platform.platform()})")

    if OS_NAME == "Windows":
        ok("Windows detectado. Usando comandos compatíveis.")
    elif OS_NAME == "Darwin":
        ok("macOS detectado.")
    elif OS_NAME == "Linux":
        ok("Linux detectado.")
    else:
        warn(f"Sistema '{OS_NAME}' não testado. Continuando mesmo assim...")


# ── 2. Verificação de pré-requisitos ────────────────────────

def check_docker() -> None:
    info("Verificando Docker...")

    if shutil.which("docker") is None:
        fail(
            "Docker não encontrado.\n"
            "   Instale em: https://docs.docker.com/get-docker/"
        )

    result = run(["docker", "compose", "version"])
    if result.returncode != 0:
        fail(
            "docker compose não encontrado.\n"
            "   Atualize o Docker Desktop para a versão mais recente."
        )

    result = run(["docker", "info"])
    if result.returncode != 0:
        fail(
            "Docker não está rodando.\n"
            "   Inicie o Docker Desktop e tente novamente."
        )

    ok("Docker está instalado e rodando.")


# ── 3. Criação do arquivo de ambiente ────────────────────────

def setup_env_file() -> str:
    """Cria deploy/demo.env se não existir. Retorna a porta configurada."""
    info("Preparando arquivo de configuração...")

    if ENV_FILE.exists():
        warn(f"Arquivo {ENV_FILE.name} já existe. Usando o existente.")
    else:
        if not ENV_EXAMPLE.exists():
            fail(f"Arquivo {ENV_EXAMPLE.name} não encontrado. Verifique a estrutura do projeto.")

        jwt_secret = secrets.token_urlsafe(48)
        content = ENV_EXAMPLE.read_text(encoding="utf-8")
        content = content.replace(
            "JWT_SECRET_KEY=replace-with-a-long-random-secret-for-demo",
            f"JWT_SECRET_KEY={jwt_secret}",
        )

        ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
        ENV_FILE.write_text(content, encoding="utf-8")
        ok(f"Arquivo {ENV_FILE.name} criado com secret seguro gerado automaticamente.")

    # Lê a porta configurada
    port = "8080"
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("DEMO_PORT="):
            port = line.split("=", 1)[1].strip() or "8080"
            break

    return port


# ── 4. Subir o stack ─────────────────────────────────────────

def start_stack() -> None:
    info("Iniciando o sistema (pode levar alguns minutos na primeira vez)...")

    result = compose_run("up", "--build", "-d")
    if result.returncode != 0:
        print(result.stderr)
        fail("Falha ao iniciar os containers. Verifique o Docker e tente novamente.")

    ok("Containers iniciados.")


# ── 5. Aguardar health checks ────────────────────────────────

def wait_for_health() -> None:
    info("Aguardando os serviços ficarem saudáveis...")

    services = ["postgres", "backend", "frontend"]
    elapsed = 0

    while elapsed < HEALTH_TIMEOUT:
        all_healthy = True
        for svc in services:
            result = compose_run("ps", svc, "--format", "{{.Health}}")
            health = result.stdout.strip().lower()
            if "healthy" not in health:
                all_healthy = False
                break

        if all_healthy:
            ok("Todos os serviços estão saudáveis.")
            return

        time.sleep(HEALTH_INTERVAL)
        elapsed += HEALTH_INTERVAL
        print(".", end="", flush=True)

    print()
    warn(f"Timeout ({HEALTH_TIMEOUT}s) aguardando health checks.")
    compose_run("ps")
    fail(
        "Os serviços não ficaram saudáveis a tempo.\n"
        f"   Veja os logs com: docker compose --env-file {ENV_FILE} -f {COMPOSE_FILE} logs"
    )


# ── 6. Criar admin de demo ──────────────────────────────────

def seed_admin() -> None:
    info("Criando usuário administrador de demonstração...")

    result = compose_run(
        "exec", "-T", "backend",
        "python", "-m", "app.scripts.seed_admin",
        "--email", DEMO_EMAIL,
        "--full-name", "Admin Demo",
        "--password", DEMO_PASSWORD,
    )

    if result.returncode != 0 and "already" not in result.stdout.lower():
        if "updated" in result.stdout.lower() or "created" in result.stdout.lower():
            pass  # seed_admin imprime "created" ou "updated" — ambos são OK
        else:
            warn("Admin pode já existir (isso é normal se você já rodou antes).")

    ok("Usuário de demonstração configurado.")


# ── 7. Gerar e importar dataset ──────────────────────────────

def setup_demo_data() -> None:
    info("Preparando dados de demonstração...")

    csv_name = "dataset_operacoes_logisticas_pe.csv"
    csv_in_data = BACKEND_DATA_DIR / csv_name
    csv_in_root = PROJECT_ROOT / csv_name

    # Se o CSV já está no backend/data, pula a geração
    if csv_in_data.exists():
        ok("Dataset já existe. Pulando geração.")
    else:
        # Tenta gerar usando o Python do host
        if DATASET_GENERATOR.exists():
            info("Gerando dataset de demonstração...")
            result = run(
                [sys.executable, str(DATASET_GENERATOR)],
                cwd=str(PROJECT_ROOT),
            )
            if result.returncode == 0 and csv_in_root.exists():
                BACKEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
                shutil.move(str(csv_in_root), str(csv_in_data))
                ok("Dataset gerado.")
            else:
                warn("Não foi possível gerar o dataset. O dashboard vai abrir sem dados de demonstração.")
                return
        else:
            warn(f"Arquivo {DATASET_GENERATOR.name} não encontrado. Pulando geração de dados.")
            return

    # Importa o dataset para o banco
    info("Importando dados para o banco...")
    result = compose_run(
        "exec", "-T", "backend",
        "python", "-m", "app.scripts.import_shipments",
        f"/app/data/{csv_name}",
    )

    if result.returncode == 0:
        # Mostra o resumo da importação
        for line in result.stdout.strip().splitlines():
            print(f"   {line}")
        ok("Dados de demonstração importados.")
    else:
        warn("Importação retornou com aviso. Veja os logs se necessário.")
        if result.stderr:
            print(f"   {result.stderr.strip()}")


# ── 8. Resultado final ──────────────────────────────────────

def print_summary(port: str) -> None:
    print()
    print("━" * 56)
    print("\033[1;32m  ✅  Sistema pronto!\033[0m")
    print()
    print("  Abra no navegador:")
    print(f"    http://127.0.0.1:{port}")
    print()
    print("  Login:")
    print(f"    E-mail:  {DEMO_EMAIL}")
    print(f"    Senha:   {DEMO_PASSWORD}")
    print()

    env = str(ENV_FILE)
    comp = str(COMPOSE_FILE)

    # Mostra comandos com caminhos relativos para ficar mais limpo
    try:
        env_rel = os.path.relpath(env)
        comp_rel = os.path.relpath(comp)
    except ValueError:
        env_rel = env
        comp_rel = comp

    print("  Comandos úteis:")
    print(f"    Parar:    docker compose --env-file {env_rel} -f {comp_rel} down")
    print(f"    Subir:    docker compose --env-file {env_rel} -f {comp_rel} up -d")
    print(f"    Logs:     docker compose --env-file {env_rel} -f {comp_rel} logs -f")
    print("━" * 56)
    print()


# ── Main ─────────────────────────────────────────────────────

def main() -> None:
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   Freight Cost Risk Analytics — Quick Start         ║")
    print("╚══════════════════════════════════════════════════════╝")

    show_os_info()
    check_docker()
    port = setup_env_file()
    start_stack()
    wait_for_health()
    seed_admin()
    setup_demo_data()
    print_summary(port)


if __name__ == "__main__":
    main()
