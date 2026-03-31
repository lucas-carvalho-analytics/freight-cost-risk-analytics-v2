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
COMPOSE_FILE = ROOT / "docker-compose.demo.yml"
DEMO_PORT = os.environ.get("SMOKE_TEST_DEMO_PORT", "18080")
TIMEOUT_SECONDS = int(os.environ.get("SMOKE_TEST_TIMEOUT_SECONDS", "240"))


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


def main() -> int:
    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "demo",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "freight_analytics",
            "JWT_SECRET_KEY": "demo-smoke-test-secret-with-32-plus-characters",
            "JWT_ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            "LOG_LEVEL": "INFO",
            "DEMO_PORT": DEMO_PORT,
            "COMPOSE_PROJECT_NAME": env.get("COMPOSE_PROJECT_NAME", "freight-smoke-test"),
        }
    )

    try:
        up_result = run_compose("up", "--build", "-d", env=env)
        if up_result.returncode != 0:
            sys.stderr.write(up_result.stdout)
            sys.stderr.write(up_result.stderr)
            return up_result.returncode

        wait_for_html(f"http://127.0.0.1:{DEMO_PORT}/")
        wait_for_json(f"http://127.0.0.1:{DEMO_PORT}/api/v1/health", "ok")
        wait_for_json(f"http://127.0.0.1:{DEMO_PORT}/api/v1/ready", "ready")

        print("Demo stack smoke test passed.")
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
