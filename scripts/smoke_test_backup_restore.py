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
DEMO_PORT = os.environ.get("SMOKE_TEST_DEMO_PORT", "18084")
TIMEOUT_SECONDS = int(os.environ.get("SMOKE_TEST_TIMEOUT_SECONDS", "300"))
SENTINEL_EMAIL = "backup-restore-smoke@example.com"
SENTINEL_FULL_NAME = "Backup Restore Smoke User"
SENTINEL_HASH = "backup-restore-smoke-hash"
SENTINEL_DUMP_PATH = ROOT / "backups" / "demo" / "backup-restore-smoke-validation.dump"


def run_command(
    args: list[str],
    *,
    env: dict[str, str],
    text: bool = True,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=text,
    )


def run_compose(*args: str, env: dict[str, str], text: bool = True) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[bytes]:
    return run_command(
        ["docker", "compose", "-f", str(COMPOSE_FILE), *args],
        env=env,
        text=text,
    )


def wait_for_ready(base_url: str) -> None:
    deadline = time.time() + TIMEOUT_SECONDS
    last_error: str | None = None

    while time.time() < deadline:
        try:
            with urlopen(f"{base_url}/api/v1/ready", timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if payload.get("status") == "ready":
                    return
                last_error = f"unexpected payload: {payload}"
        except (OSError, ValueError, URLError) as exc:
            last_error = str(exc)
        time.sleep(2)

    raise RuntimeError(f"timed out waiting for demo stack readiness: {last_error}")


def exec_psql(env: dict[str, str], sql: str, *, capture: bool = False) -> str:
    result = run_compose(
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        env["POSTGRES_USER"],
        "-d",
        env["POSTGRES_DB"],
        "-t",
        "-A",
        "-c",
        sql,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"psql command failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip() if capture else ""


def seed_sentinel_user(env: dict[str, str]) -> None:
    exec_psql(env, f"DELETE FROM users WHERE email = '{SENTINEL_EMAIL}';")
    exec_psql(
        env,
        " ".join(
            [
                "INSERT INTO users (email, full_name, password_hash, is_active)",
                f"VALUES ('{SENTINEL_EMAIL}', '{SENTINEL_FULL_NAME}', '{SENTINEL_HASH}', true);",
            ]
        ),
    )


def delete_sentinel_user(env: dict[str, str]) -> None:
    exec_psql(env, f"DELETE FROM users WHERE email = '{SENTINEL_EMAIL}';")


def sentinel_count(env: dict[str, str]) -> int:
    count = exec_psql(
        env,
        f"SELECT count(*) FROM users WHERE email = '{SENTINEL_EMAIL}';",
        capture=True,
    )
    return int(count)


def run_python_script(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return run_command([sys.executable, *args], env=env, text=True)


def validate_metadata_file() -> Path:
    if not SENTINEL_DUMP_PATH.is_file():
        raise RuntimeError(f"expected dump file not found: {SENTINEL_DUMP_PATH}")

    metadata_path = SENTINEL_DUMP_PATH.with_suffix(f"{SENTINEL_DUMP_PATH.suffix}.metadata.json")
    if not metadata_path.is_file():
        raise RuntimeError(f"expected metadata file not found: {metadata_path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    required_fields = {"sha256", "stack", "database", "file_name", "size_bytes", "created_at_utc"}
    missing_fields = sorted(required_fields.difference(metadata))
    if missing_fields:
        raise RuntimeError(f"missing metadata fields: {missing_fields}")

    if metadata["stack"] != "demo":
        raise RuntimeError(f"unexpected metadata stack: {metadata}")
    if metadata["database"] != "freight_analytics":
        raise RuntimeError(f"unexpected metadata database: {metadata}")
    if metadata["file_name"] != SENTINEL_DUMP_PATH.name:
        raise RuntimeError(f"unexpected metadata file name: {metadata}")

    return metadata_path


def cleanup_dump_files() -> None:
    metadata_path = SENTINEL_DUMP_PATH.with_suffix(f"{SENTINEL_DUMP_PATH.suffix}.metadata.json")
    if metadata_path.exists():
        metadata_path.unlink()
    if SENTINEL_DUMP_PATH.exists():
        SENTINEL_DUMP_PATH.unlink()
    if SENTINEL_DUMP_PATH.parent.exists() and not any(SENTINEL_DUMP_PATH.parent.iterdir()):
        SENTINEL_DUMP_PATH.parent.rmdir()
    backups_root = ROOT / "backups"
    if backups_root.exists() and not any(backups_root.iterdir()):
        backups_root.rmdir()


def main() -> int:
    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "demo",
            "APP_NAME": "freight_cost_risk_analytics",
            "APP_VERSION": "0.1.0",
            "API_V1_PREFIX": "/api/v1",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "freight_analytics",
            "JWT_SECRET_KEY": "demo-backup-restore-smoke-secret-with-32-plus-characters",
            "JWT_ALGORITHM": "HS256",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            "LOG_LEVEL": "INFO",
            "DEMO_PORT": DEMO_PORT,
            "COMPOSE_PROJECT_NAME": env.get("COMPOSE_PROJECT_NAME", "freight-backup-restore-smoke"),
        }
    )

    try:
        up_result = run_compose("up", "-d", env=env)
        if up_result.returncode != 0:
            sys.stderr.write(up_result.stdout)
            sys.stderr.write(up_result.stderr)
            return up_result.returncode

        wait_for_ready(f"http://127.0.0.1:{DEMO_PORT}")

        seed_sentinel_user(env)
        if sentinel_count(env) != 1:
            raise RuntimeError("failed to confirm sentinel user after seed")

        backup_result = run_python_script(
            env,
            "scripts/backup_postgres_compose.py",
            "--stack",
            "demo",
            "--output",
            str(SENTINEL_DUMP_PATH),
        )
        if backup_result.returncode != 0:
            raise RuntimeError(f"backup script failed:\n{backup_result.stdout}\n{backup_result.stderr}")

        validate_metadata_file()
        delete_sentinel_user(env)
        if sentinel_count(env) != 0:
            raise RuntimeError("failed to remove sentinel user before restore")

        restore_result = run_python_script(
            env,
            "scripts/restore_postgres_compose.py",
            "--stack",
            "demo",
            "--input",
            str(SENTINEL_DUMP_PATH),
            "--yes-i-understand-this-will-overwrite-data",
        )
        if restore_result.returncode != 0:
            raise RuntimeError(f"restore script failed:\n{restore_result.stdout}\n{restore_result.stderr}")

        if sentinel_count(env) != 1:
            raise RuntimeError("sentinel user was not restored")

        print("Backup/restore smoke test passed.")
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
        cleanup_dump_files()
        down_result = run_compose("down", "-v", env=env)
        if down_result.returncode != 0:
            sys.stderr.write(down_result.stdout)
            sys.stderr.write(down_result.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
