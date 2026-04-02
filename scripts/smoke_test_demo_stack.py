from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "docker-compose.demo.yml"
DEMO_PORT = os.environ.get("SMOKE_TEST_DEMO_PORT", "18080")
TIMEOUT_SECONDS = int(os.environ.get("SMOKE_TEST_TIMEOUT_SECONDS", "240"))
ADMIN_EMAIL = "smoke-admin@example.com"
ADMIN_PASSWORD = "SmokeTest123!"
ADMIN_FULL_NAME = "Smoke Test Admin"


def run_compose(*args: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), *args],
        cwd=ROOT,
        env=env,
        check=False,
        text=True,
        capture_output=True,
    )


def compose_exec(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "exec", "-T", "backend", *args],
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


def request_json(
    url: str,
    *,
    method: str = "GET",
    data: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    expected_status: int = 200,
) -> dict[str, object]:
    encoded_data = None
    request_headers = headers.copy() if headers else {}

    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    request = Request(url, data=encoded_data, headers=request_headers, method=method)

    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if response.status != expected_status:
                raise RuntimeError(
                    f"unexpected status for {url}: {response.status}, payload={payload}"
                )
            return payload
    except HTTPError as exc:
        payload = json.loads(exc.read().decode("utf-8"))
        if exc.code != expected_status:
            raise RuntimeError(
                f"unexpected error status for {url}: {exc.code}, payload={payload}"
            ) from exc
        return payload


def seed_admin(env: dict[str, str]) -> None:
    seed_code = """
from sqlalchemy import select
from app.auth.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User

email = "smoke-admin@example.com"
password = "SmokeTest123!"
full_name = "Smoke Test Admin"

with SessionLocal() as session:
    user = session.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            is_active=True,
        )
        session.add(user)
    else:
        user.full_name = full_name
        user.password_hash = hash_password(password)
        user.is_active = True
    session.commit()
print("admin seeded")
""".strip()

    result = compose_exec(env, "python", "-c", seed_code)
    if result.returncode != 0:
        raise RuntimeError(f"failed to seed admin:\n{result.stdout}\n{result.stderr}")


def run_authenticated_checks(base_url: str) -> None:
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
    }
    invalid_login_payload = {
        "email": ADMIN_EMAIL,
        "password": "wrong-password",
    }

    invalid_login = request_json(
        f"{base_url}/api/v1/auth/login",
        method="POST",
        data=invalid_login_payload,
        expected_status=401,
    )
    if invalid_login.get("message") != "Invalid credentials.":
        raise RuntimeError(f"unexpected invalid login payload: {invalid_login}")

    unauthorized_me = request_json(
        f"{base_url}/api/v1/auth/me",
        expected_status=401,
    )
    if unauthorized_me.get("message") != "Not authenticated.":
        raise RuntimeError(f"unexpected unauthorized /me payload: {unauthorized_me}")

    login_result = request_json(
        f"{base_url}/api/v1/auth/login",
        method="POST",
        data=login_payload,
    )
    access_token = str(login_result.get("access_token", ""))
    if not access_token:
        raise RuntimeError(f"missing access token in login response: {login_result}")

    me_payload = request_json(
        f"{base_url}/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if me_payload.get("email") != ADMIN_EMAIL:
        raise RuntimeError(f"unexpected /me payload: {me_payload}")


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

        base_url = f"http://127.0.0.1:{DEMO_PORT}"

        wait_for_html(f"{base_url}/")
        wait_for_json(f"{base_url}/api/v1/health", "ok")
        wait_for_json(f"{base_url}/api/v1/ready", "ready")
        seed_admin(env)
        run_authenticated_checks(base_url)

        print("Demo stack authenticated smoke test passed.")
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
