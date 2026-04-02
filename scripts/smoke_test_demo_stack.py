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
SMOKE_ORIGEM = "Smoke Origin"
SMOKE_DESTINO_A = "Smoke Destination A"
SMOKE_DESTINO_B = "Smoke Destination B"
SMOKE_TRANSPORTADORA = "Smoke Carrier"
SMOKE_TIPO_VEICULO = "Truck"


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


def seed_shipments(env: dict[str, str]) -> None:
    seed_code = """
from datetime import date
from decimal import Decimal

from app.db.session import SessionLocal
from app.models.shipment import Shipment

with SessionLocal() as session:
    session.query(Shipment).filter(
        Shipment.transportadora == "Smoke Carrier"
    ).delete(synchronize_session=False)

    shipments = [
        Shipment(
            data_embarque=date(2024, 1, 10),
            origem="Smoke Origin",
            destino="Smoke Destination A",
            valor_carga=Decimal("10000.00"),
            tipo_veiculo="Truck",
            transportadora="Smoke Carrier",
            taxa_ad_valorem_pct=Decimal("1.00"),
            frete_peso=Decimal("150.00"),
            ocorrencia="OK",
            tem_ocorrencia=False,
            ad_valorem=Decimal("100.00"),
        ),
        Shipment(
            data_embarque=date(2024, 1, 11),
            origem="Smoke Origin",
            destino="Smoke Destination B",
            valor_carga=Decimal("12000.00"),
            tipo_veiculo="Truck",
            transportadora="Smoke Carrier",
            taxa_ad_valorem_pct=Decimal("1.00"),
            frete_peso=Decimal("200.00"),
            ocorrencia="Atraso",
            tem_ocorrencia=True,
            ad_valorem=Decimal("120.00"),
        ),
    ]
    session.add_all(shipments)
    session.commit()
print("shipments seeded")
""".strip()

    result = compose_exec(env, "python", "-c", seed_code)
    if result.returncode != 0:
        raise RuntimeError(
            f"failed to seed smoke shipments:\n{result.stdout}\n{result.stderr}"
        )


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

    unauthorized_kpi = request_json(
        f"{base_url}/api/v1/kpis/frete-total",
        expected_status=401,
    )
    if unauthorized_kpi.get("message") != "Not authenticated.":
        raise RuntimeError(f"unexpected unauthorized KPI payload: {unauthorized_kpi}")

    frete_total_payload = request_json(
        f"{base_url}/api/v1/kpis/frete-total?origem=Smoke%20Origin",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if frete_total_payload != {
        "metric": "frete_total",
        "value": 350.0,
        "shipment_count": 2,
    }:
        raise RuntimeError(f"unexpected KPI payload: {frete_total_payload}")

    filtros_payload = request_json(
        f"{base_url}/api/v1/filtros/origens",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if SMOKE_ORIGEM not in filtros_payload.get("items", []):
        raise RuntimeError(f"unexpected filter payload: {filtros_payload}")


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
        seed_shipments(env)
        run_authenticated_checks(base_url)

        print("Demo stack protected KPI smoke test passed.")
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
