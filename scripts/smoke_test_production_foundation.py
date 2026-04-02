from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "docker-compose.production-foundation.yml"
PRODUCTION_PORT = os.environ.get("SMOKE_TEST_PRODUCTION_PORT", "18081")
TIMEOUT_SECONDS = int(os.environ.get("SMOKE_TEST_TIMEOUT_SECONDS", "300"))


def run_compose(*args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), *args],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


def wait_for_json(url: str, expected_status: str) -> None:
    deadline = time.time() + TIMEOUT_SECONDS
    last_error: str | None = None

    while time.time() < deadline:
        try:
            with urlopen(url, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if payload.get("status") == expected_status:
                    return
                last_error = f"unexpected payload: {payload}"
        except (OSError, ValueError, URLError) as exc:
            last_error = str(exc)
        time.sleep(2)

    raise RuntimeError(f"timed out waiting for {url}: {last_error}")


def wait_for_html(url: str) -> None:
    deadline = time.time() + TIMEOUT_SECONDS
    last_error: str | None = None

    while time.time() < deadline:
        try:
            with urlopen(url, timeout=5) as response:
                content_type = response.headers.get("Content-Type", "")
                body = response.read().decode("utf-8")
                if response.status == 200 and "text/html" in content_type and "<div id=\"root\">" in body:
                    return
                last_error = f"unexpected response: status={response.status}, content_type={content_type}"
        except (OSError, URLError) as exc:
            last_error = str(exc)
        time.sleep(2)

    raise RuntimeError(f"timed out waiting for frontend root {url}: {last_error}")


def wait_for_text(url: str, expected_body: str) -> None:
    deadline = time.time() + TIMEOUT_SECONDS
    last_error: str | None = None

    while time.time() < deadline:
        try:
            with urlopen(url, timeout=5) as response:
                body = response.read().decode("utf-8").strip()
                if response.status == 200 and body == expected_body:
                    return
                last_error = f"unexpected response: status={response.status}, body={body!r}"
        except (OSError, URLError) as exc:
            last_error = str(exc)
        time.sleep(2)

    raise RuntimeError(f"timed out waiting for {url}: {last_error}")


def load_compose_services(env: dict[str, str]) -> dict[str, dict[str, object]]:
    result = run_compose("ps", "-a", "--format", "json", env=env)
    if result.returncode != 0:
        raise RuntimeError(f"failed to inspect compose services:\n{result.stdout}\n{result.stderr}")

    output = result.stdout.strip()
    if not output:
        raise RuntimeError("compose ps returned no service data")

    if output.startswith("["):
        services = json.loads(output)
    else:
        services = [json.loads(line) for line in output.splitlines() if line.strip()]

    return {str(service["Service"]): service for service in services}


def assert_service_state(services: dict[str, dict[str, object]], service_name: str) -> dict[str, object]:
    service = services.get(service_name)
    if service is None:
        raise RuntimeError(f"service {service_name!r} not found in compose ps output: {services}")
    return service


def check_runtime_and_migration_flow(env: dict[str, str]) -> None:
    deadline = time.time() + TIMEOUT_SECONDS
    last_services: dict[str, dict[str, object]] | None = None

    while time.time() < deadline:
        services = load_compose_services(env)
        last_services = services

        migrate = assert_service_state(services, "migrate")
        backend = assert_service_state(services, "backend")
        frontend = assert_service_state(services, "frontend")
        postgres = assert_service_state(services, "postgres")

        migrate_state = str(migrate.get("State", "")).lower()
        migrate_exit_code = int(migrate.get("ExitCode", 1))
        backend_state = str(backend.get("State", "")).lower()
        backend_health = str(backend.get("Health", "")).lower()
        frontend_state = str(frontend.get("State", "")).lower()
        frontend_health = str(frontend.get("Health", "")).lower()
        postgres_state = str(postgres.get("State", "")).lower()
        postgres_health = str(postgres.get("Health", "")).lower()

        if (
            migrate_state == "exited"
            and migrate_exit_code == 0
            and backend_state == "running"
            and backend_health == "healthy"
            and frontend_state == "running"
            and frontend_health == "healthy"
            and postgres_state == "running"
            and postgres_health == "healthy"
        ):
            return

        time.sleep(2)

    raise RuntimeError(f"unexpected production foundation service state: {last_services}")


def main() -> int:
    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "production",
            "APP_NAME": "freight_cost_risk_analytics",
            "APP_VERSION": "0.1.0",
            "API_V1_PREFIX": "/api/v1",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "production-smoke-test-strong-password",
            "POSTGRES_DB": "freight_analytics",
            "JWT_SECRET_KEY": "production-smoke-test-secret-with-32-plus-characters",
            "JWT_ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            "LOG_LEVEL": "info",
            "WEB_CONCURRENCY": "2",
            "PRODUCTION_PORT": PRODUCTION_PORT,
            "COMPOSE_PROJECT_NAME": env.get(
                "COMPOSE_PROJECT_NAME", "freight-production-smoke-test"
            ),
        }
    )

    try:
        up_result = run_compose("up", "--build", "-d", env=env)
        if up_result.returncode != 0:
            sys.stderr.write(up_result.stdout)
            sys.stderr.write(up_result.stderr)
            return up_result.returncode

        base_url = f"http://127.0.0.1:{PRODUCTION_PORT}"

        wait_for_html(f"{base_url}/")
        wait_for_text(f"{base_url}/healthz", "ok")
        wait_for_json(f"{base_url}/api/v1/health", "ok")
        wait_for_json(f"{base_url}/api/v1/ready", "ready")
        check_runtime_and_migration_flow(env)

        print("Production foundation smoke test passed.")
        return 0
    except Exception as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        ps_result = run_compose("ps", env=env)
        logs_result = run_compose("logs", "--tail", "100", env=env)
        sys.stderr.write(ps_result.stdout)
        sys.stderr.write(ps_result.stderr)
        sys.stderr.write(logs_result.stdout)
        sys.stderr.write(logs_result.stderr)
        return 1
    finally:
        down_result = run_compose("down", "-v", env=env)
        if down_result.returncode != 0:
            sys.stderr.write(down_result.stdout)
            sys.stderr.write(down_result.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
