from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class StackConfig:
    name: str
    compose_file: Path
    runtime_services: tuple[str, ...]
    postgres_user: str
    postgres_password: str
    postgres_db: str


STACKS: dict[str, StackConfig] = {
    "demo": StackConfig(
        name="demo",
        compose_file=ROOT / "docker-compose.demo.yml",
        runtime_services=("backend", "frontend"),
        postgres_user="postgres",
        postgres_password="postgres",
        postgres_db="freight_analytics",
    ),
    "production-foundation": StackConfig(
        name="production-foundation",
        compose_file=ROOT / "docker-compose.production-foundation.yml",
        runtime_services=("backend", "frontend"),
        postgres_user="postgres",
        postgres_password="replace-with-a-strong-password",
        postgres_db="freight_analytics",
    ),
}


def parse_env_file(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def build_compose_env(stack: StackConfig, env_file: Path | None) -> dict[str, str]:
    env = os.environ.copy()
    if env_file is not None:
        env.update(parse_env_file(env_file))

    env.setdefault("POSTGRES_USER", stack.postgres_user)
    env.setdefault("POSTGRES_PASSWORD", stack.postgres_password)
    env.setdefault("POSTGRES_DB", stack.postgres_db)
    return env


def resolve_stack(name: str) -> StackConfig:
    try:
        return STACKS[name]
    except KeyError as exc:
        raise ValueError(f"unsupported stack {name!r}") from exc


def compose_base_args(stack: StackConfig, env_file: Path | None) -> list[str]:
    args = ["docker", "compose"]
    if env_file is not None:
        args.extend(["--env-file", str(env_file)])
    args.extend(["-f", str(stack.compose_file)])
    return args


def run_command(
    args: list[str],
    *,
    env: dict[str, str],
    input_bytes: bytes | None = None,
    text: bool = False,
) -> subprocess.CompletedProcess[bytes] | subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        input=input_bytes,
        check=False,
        capture_output=True,
        text=text,
    )


def run_compose(
    stack: StackConfig,
    *,
    env: dict[str, str],
    env_file: Path | None,
    args: list[str],
    input_bytes: bytes | None = None,
    text: bool = False,
) -> subprocess.CompletedProcess[bytes] | subprocess.CompletedProcess[str]:
    return run_command(
        [*compose_base_args(stack, env_file), *args],
        env=env,
        input_bytes=input_bytes,
        text=text,
    )


def compose_services(stack: StackConfig, *, env: dict[str, str], env_file: Path | None) -> set[str]:
    result = run_compose(
        stack,
        env=env,
        env_file=env_file,
        args=["config", "--services"],
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"failed to inspect compose services:\n{result.stdout}\n{result.stderr}")
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def running_services(stack: StackConfig, *, env: dict[str, str], env_file: Path | None) -> set[str]:
    result = run_compose(
        stack,
        env=env,
        env_file=env_file,
        args=["ps", "--services", "--filter", "status=running"],
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"failed to inspect running services:\n{result.stdout}\n{result.stderr}")
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def utc_timestamp_for_filename() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def utc_timestamp_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def metadata_path_for_dump(dump_path: Path) -> Path:
    return dump_path.with_suffix(f"{dump_path.suffix}.metadata.json")


def write_backup_metadata(dump_path: Path, metadata: dict[str, object]) -> Path:
    metadata_path = metadata_path_for_dump(dump_path)
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    return metadata_path


def read_backup_metadata(dump_path: Path) -> dict[str, object] | None:
    metadata_path = metadata_path_for_dump(dump_path)
    if not metadata_path.is_file():
        return None
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def write_backup_failure_event(
    stack_name: str,
    database_name: str,
    step: str,
    exit_code: int,
    message: str,
) -> Path:
    alerts_dir = ROOT / "backups" / "alerts"
    alerts_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = utc_timestamp_for_filename()
    database_part = f"-{database_name}" if database_name and database_name != "unknown" else ""
    event_path = alerts_dir / f"{stack_name}{database_part}-{timestamp}-failure-event.json"
    
    payload = {
        "event": "backup_failure",
        "step": step,
        "exit_code": exit_code,
        "stack": stack_name,
        "database": database_name,
        "timestamp_utc": utc_timestamp_iso(),
        "message": message,
    }
    event_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return event_path


def validate_dump_with_pg_restore(
    stack: StackConfig,
    *,
    env: dict[str, str],
    env_file: Path | None,
    dump_bytes: bytes,
) -> None:
    result = run_compose(
        stack,
        env=env,
        env_file=env_file,
        args=[
            "exec",
            "-T",
            "postgres",
            "sh",
            "-lc",
            "tmp_dump=/tmp/backup-validation.dump; cat > \"$tmp_dump\" && pg_restore --list \"$tmp_dump\" >/dev/null && rm -f \"$tmp_dump\"",
        ],
        input_bytes=dump_bytes,
    )
    if result.returncode != 0:
        event_path = write_backup_failure_event(
            stack_name=stack.name,
            database_name=env.get("POSTGRES_DB", "unknown"),
            step="dump_integrity_validation",
            exit_code=result.returncode,
            message="The dump file was generated but failed pg_restore validation.",
        )
        error_msg = (
            "======================================================================\n"
            "[BACKUP_ERROR] Stage: dump integrity validation\n"
            f"Target Stack: {stack.name}\n"
            "======================================================================\n"
            f"STDOUT:\n{result.stdout.decode('utf-8', errors='replace')}\n"
            f"STDERR:\n{result.stderr.decode('utf-8', errors='replace')}\n"
            "======================================================================\n"
            "ACTION RECOMMENDED: The dump file was generated but failed pg_restore validation.\n"
            "It may be corrupted or incomplete. Do not rely on this dump.\n"
            f"Alert payload written to: {event_path}\n"
            "Reference: docs/backup-failure-visibility-foundation.md\n"
            "======================================================================"
        )
        raise RuntimeError(error_msg)

