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
import webbrowser
import getpass
from pathlib import Path

# ── Configuração ─────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent
COMPOSE_FILE = PROJECT_ROOT / "docker-compose.demo.yml"
ENV_EXAMPLE = PROJECT_ROOT / "deploy" / "demo.env.example"
ENV_FILE = PROJECT_ROOT / "deploy" / "demo.env"
DATASET_GENERATOR = PROJECT_ROOT / "gerar_dataset_logistica_pe.py"
BACKEND_DATA_DIR = PROJECT_ROOT / "backend" / "data"

DEMO_EMAIL = ""
DEMO_PASSWORD = ""
LOCAL_HOSTNAME = "freight-analytics.local"
HEALTH_TIMEOUT = 150  # segundos
HEALTH_INTERVAL = 4   # segundos entre tentativas

OS_NAME = platform.system()  # "Linux", "Darwin", "Windows"


# ── Helpers ──────────────────────────────────────────────────

COLORS = os.environ.get("NO_COLOR") is None

def _c(code: str, msg: str) -> str:
    return f"\033[{code}m{msg}\033[0m" if COLORS else msg

def banner(msg: str) -> None:
    print(f"\n{_c('1;36', '═' * 60)}")
    print(f"  {_c('1;37', msg)}")
    print(f"{_c('1;36', '═' * 60)}")

def step(num: int, msg: str) -> None:
    print(f"\n{_c('1;36', f'[{num}/8]')} {_c('1;37', msg)}")

def info(msg: str) -> None:
    print(f"  {_c('1;34', '▸')} {msg}")

def ok(msg: str) -> None:
    print(f"  {_c('1;32', '✅')} {msg}")

def warn(msg: str) -> None:
    print(f"  {_c('1;33', '⚠ ')} {msg}")

def fail(msg: str) -> None:
    print(f"  {_c('1;31', '❌')} {msg}")
    print()
    input("  Pressione Enter para sair...")
    sys.exit(1)

def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)

def compose_cmd() -> list[str]:
    return [
        "docker", "compose",
        "--env-file", str(ENV_FILE),
        "-f", str(COMPOSE_FILE),
    ]

def compose_run(*args: str, **kwargs) -> subprocess.CompletedProcess:
    return run([*compose_cmd(), *args], **kwargs)


# ── 0. Configurar credenciais ────────────────────────────────

def configure_credentials() -> None:
    global DEMO_EMAIL, DEMO_PASSWORD
    print()
    step(0, "Configuração de Login (Segurança)")
    
    default_email = "comexhebron26@freight-analytics.com"
    email_input = input(f"  {_c('1;37', 'E-mail')} [{default_email}]: ").strip()
    DEMO_EMAIL = email_input if email_input else default_email

    while True:
        pw_input = getpass.getpass(f"  {_c('1;37', 'Senha')}: ").strip()
        if len(pw_input) >= 6:
            DEMO_PASSWORD = pw_input
            break
        else:
            warn("A senha deve ter pelo menos 6 caracteres.")
    
    ok(f"Credenciais configuradas para {DEMO_EMAIL}.")


# ── 1. Detecção do sistema operacional ───────────────────────

def show_os_info() -> None:
    step(1, "Detectando sistema operacional")

    os_labels = {"Windows": "Windows", "Darwin": "macOS", "Linux": "Linux"}
    label = os_labels.get(OS_NAME, OS_NAME)
    info(f"Sistema: {label} ({platform.machine()})")
    ok(f"{label} detectado. Todos os comandos serão adaptados automaticamente.")


# ── 2. Verificação de pré-requisitos ────────────────────────

def open_url(url: str) -> None:
    """Abre URL no navegador padrão."""
    try:
        webbrowser.open(url)
    except Exception:
        pass


def check_prerequisites() -> None:
    step(2, "Verificando pré-requisitos")

    # Docker
    info("Verificando Docker...")
    if shutil.which("docker") is None:
        warn("Docker não encontrado no sistema.")
        print()
        print(f"  {_c('1;37', 'O Docker é necessário para rodar o sistema.')}")
        print(f"  {_c('1;37', 'Vamos abrir a página de download para você.')}")
        print()

        docker_urls = {
            "Windows": "https://docs.docker.com/desktop/install/windows-install/",
            "Darwin": "https://docs.docker.com/desktop/install/mac-install/",
            "Linux": "https://docs.docker.com/engine/install/",
        }
        url = docker_urls.get(OS_NAME, "https://docs.docker.com/get-docker/")
        open_url(url)
        print(f"  📥 Link: {url}")
        print()
        fail(
            "Instale o Docker, reinicie o computador se necessário,\n"
            "     e depois execute este script novamente."
        )

    result = run(["docker", "compose", "version"])
    if result.returncode != 0:
        fail(
            "docker compose não encontrado.\n"
            "     Atualize o Docker Desktop para a versão mais recente."
        )

    result = run(["docker", "info"])
    if result.returncode != 0:
        warn("Docker está instalado mas não está rodando.")
        print()
        print(f"  {_c('1;37', 'Abra o Docker Desktop e aguarde ele iniciar.')}")
        print(f"  {_c('1;37', 'Depois execute este script novamente.')}")
        fail("Docker precisa estar rodando para continuar.")

    ok("Docker instalado e rodando.")

    # Git
    info("Verificando Git...")
    if shutil.which("git") is None:
        warn("Git não encontrado.")
        open_url("https://git-scm.com/downloads")
        print(f"  📥 Link: https://git-scm.com/downloads")
        fail("Instale o Git e execute este script novamente.")
    ok("Git disponível.")


# ── 3. Criação do arquivo de ambiente ────────────────────────

def setup_env_file() -> str:
    step(3, "Preparando configuração")

    if ENV_FILE.exists():
        info(f"Arquivo {ENV_FILE.name} já existe. Usando o existente.")
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
        ok("Configuração criada com chave de segurança gerada automaticamente.")

    # Lê a porta configurada
    port = "8080"
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("DEMO_PORT="):
            port = line.split("=", 1)[1].strip() or "8080"
            break

    return port


# ── 4. Subir o stack ─────────────────────────────────────────

def start_stack() -> None:
    step(4, "Iniciando os serviços")
    info("Isso pode levar alguns minutos na primeira vez...")

    result = compose_run("up", "--build", "-d")
    if result.returncode != 0:
        print(result.stderr)
        fail("Falha ao iniciar os containers. Verifique o Docker e tente novamente.")

    ok("Todos os containers foram iniciados.")


# ── 5. Aguardar health checks ────────────────────────────────

def wait_for_health() -> None:
    step(5, "Aguardando os serviços ficarem prontos")

    services = ["postgres", "backend", "frontend"]
    elapsed = 0

    while elapsed < HEALTH_TIMEOUT:
        all_healthy = True
        status_line = []
        for svc in services:
            result = compose_run("ps", svc, "--format", "{{.Health}}")
            health = result.stdout.strip().lower()
            is_healthy = "healthy" in health
            icon = _c('1;32', '●') if is_healthy else _c('1;33', '○')
            status_line.append(f"{icon} {svc}")
            if not is_healthy:
                all_healthy = False

        # Mostra progresso na mesma linha
        print(f"\r  {'  '.join(status_line)}  [{elapsed}s]", end="", flush=True)

        if all_healthy:
            print()
            ok("Todos os serviços estão saudáveis e prontos.")
            return

        time.sleep(HEALTH_INTERVAL)
        elapsed += HEALTH_INTERVAL

    print()
    fail(
        f"Os serviços não ficaram prontos em {HEALTH_TIMEOUT}s.\n"
        f"     Verifique os logs: docker compose --env-file {ENV_FILE} -f {COMPOSE_FILE} logs"
    )


# ── 6. Criar admin de demo ──────────────────────────────────

def seed_admin() -> None:
    step(6, "Criando usuário de acesso")

    result = compose_run(
        "exec", "-T", "backend",
        "python", "-m", "app.scripts.seed_admin",
        "--email", DEMO_EMAIL,
        "--full-name", "Operador Freight",
        "--password", DEMO_PASSWORD,
    )

    if result.returncode != 0 and "already" not in result.stdout.lower():
        if "updated" in result.stdout.lower() or "created" in result.stdout.lower():
            pass
        else:
            info("Usuário pode já existir (normal ao rodar novamente).")

    ok(f"Usuário configurado: {DEMO_EMAIL}")


# ── 7. Gerar e importar dataset ──────────────────────────────

def setup_demo_data() -> None:
    step(7, "Carregando dados de demonstração")

    csv_name = "dataset_operacoes_logisticas_pe.csv"
    csv_in_data = BACKEND_DATA_DIR / csv_name
    csv_in_root = PROJECT_ROOT / csv_name

    if csv_in_data.exists():
        info("Dataset já existe.")
    else:
        if DATASET_GENERATOR.exists():
            info("Gerando 5.000 registros de operações logísticas...")
            result = run(
                [sys.executable, str(DATASET_GENERATOR)],
                cwd=str(PROJECT_ROOT),
            )
            if result.returncode == 0 and csv_in_root.exists():
                BACKEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
                shutil.move(str(csv_in_root), str(csv_in_data))
                ok("Dataset gerado.")
            else:
                warn("Não foi possível gerar o dataset. O dashboard abrirá sem dados.")
                return
        else:
            warn(f"Gerador de dados não encontrado. O dashboard abrirá sem dados.")
            return

    info("Importando para o banco de dados...")
    result = compose_run(
        "exec", "-T", "backend",
        "python", "-m", "app.scripts.import_shipments",
        f"/app/data/{csv_name}",
    )

    if result.returncode == 0:
        for line in result.stdout.strip().splitlines():
            print(f"    {line}")
        ok("Dados importados com sucesso.")
    else:
        warn("Importação retornou com aviso. Os dados podem já estar no banco.")


# ── 8. Hostname local + abrir navegador ─────────────────────

def get_hosts_path() -> Path:
    if OS_NAME == "Windows":
        return Path(r"C:\Windows\System32\drivers\etc\hosts")
    return Path("/etc/hosts")


def setup_local_hostname(port: str) -> str:
    """Tenta configurar hostname local amigável. Retorna a URL final."""
    step(8, "Configurando acesso local")

    hosts_path = get_hosts_path()
    entry = f"127.0.0.1  {LOCAL_HOSTNAME}"
    url_custom = f"http://{LOCAL_HOSTNAME}:{port}"
    url_fallback = f"http://127.0.0.1:{port}"

    # Verifica se já está configurado
    try:
        hosts_content = hosts_path.read_text(encoding="utf-8", errors="ignore")
        if LOCAL_HOSTNAME in hosts_content:
            ok(f"Endereço {LOCAL_HOSTNAME} já configurado.")
            return url_custom
    except PermissionError:
        pass
    except Exception:
        pass

    # Tenta adicionar ao arquivo hosts
    info(f"Configurando endereço amigável: {LOCAL_HOSTNAME}")

    try:
        with open(hosts_path, "a", encoding="utf-8") as f:
            f.write(f"\n# Freight Analytics - adicionado por quick-start.py\n")
            f.write(f"{entry}\n")
        ok(f"Endereço {LOCAL_HOSTNAME} configurado com sucesso!")
        return url_custom
    except PermissionError:
        warn(f"Sem permissão para configurar {LOCAL_HOSTNAME}.")
        print()

        if OS_NAME == "Windows":
            print(f"  {_c('1;37', 'Para usar o endereço amigável, execute este comando')}")
            print(f"  {_c('1;37', 'em um Prompt de Comando COMO ADMINISTRADOR:')}")
            print()
            print(f"    echo {entry} >> C:\\Windows\\System32\\drivers\\etc\\hosts")
        else:
            print(f"  {_c('1;37', 'Para usar o endereço amigável, execute:')}")
            print()
            print(f"    echo '{entry}' | sudo tee -a /etc/hosts")

        print()
        info(f"Por enquanto, use: {url_fallback}")
        return url_fallback
    except Exception:
        info(f"Usando endereço padrão: {url_fallback}")
        return url_fallback


def open_browser(url: str) -> None:
    """Abre o navegador automaticamente."""
    info(f"Abrindo navegador em {url}...")
    time.sleep(2)  # Pequena pausa para garantir que o frontend está servindo
    try:
        webbrowser.open(url)
        ok("Navegador aberto.")
    except Exception:
        info("Não foi possível abrir o navegador automaticamente.")
        info(f"Acesse manualmente: {url}")


# ── Resultado final ─────────────────────────────────────────

def print_summary(url: str) -> None:
    try:
        env_rel = os.path.relpath(str(ENV_FILE))
        comp_rel = os.path.relpath(str(COMPOSE_FILE))
    except ValueError:
        env_rel = str(ENV_FILE)
        comp_rel = str(COMPOSE_FILE)

    print()
    print(_c('1;36', '━' * 60))
    print()
    print(f"  {_c('1;32', '✅  SISTEMA PRONTO!')}")
    print()
    print(f"  {_c('1;37', '🌐 Acesse no navegador:')}")
    print(f"     {_c('1;36', url)}")
    print()
    print(f"  {_c('1;37', '🔐 Login:')}")
    print(f"     E-mail:  {_c('1;33', DEMO_EMAIL)}")
    print(f"     Senha:   {_c('1;33', '******** (a que você definiu)')}")
    print()
    print(f"  {_c('1;37', '⚡ Comandos úteis:')}")
    print(f"     Parar:   docker compose --env-file {env_rel} -f {comp_rel} down")
    print(f"     Ligar:   docker compose --env-file {env_rel} -f {comp_rel} up -d")
    print(f"     Logs:    docker compose --env-file {env_rel} -f {comp_rel} logs -f")
    print()
    print(_c('1;36', '━' * 60))
    print()


# ── Main ─────────────────────────────────────────────────────

def main() -> None:
    banner("Freight Cost Risk Analytics — Instalação Automática")

    configure_credentials()
    show_os_info()
    check_prerequisites()
    port = setup_env_file()
    start_stack()
    wait_for_health()
    seed_admin()
    setup_demo_data()
    url = setup_local_hostname(port)

    print_summary(url)
    open_browser(url)

    if OS_NAME == "Windows":
        print()
        input("  Pressione Enter para fechar esta janela...")


if __name__ == "__main__":
    main()
