from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
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

