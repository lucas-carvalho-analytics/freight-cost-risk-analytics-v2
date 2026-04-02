from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from postgres_compose_ops import ROOT, build_compose_env, resolve_stack, run_compose


def default_output_path(stack_name: str, database_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return ROOT / "backups" / stack_name / f"{database_name}-{timestamp}.dump"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a PostgreSQL backup from a docker compose stack.")
    parser.add_argument(
        "--stack",
        choices=("demo", "production-foundation"),
        required=True,
        help="Target stack to back up.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Optional env file used by docker compose.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional output path for the dump file. Defaults to backups/<stack>/<db>-<timestamp>.dump",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stack = resolve_stack(args.stack)
    env_file = args.env_file.resolve() if args.env_file else None
    env = build_compose_env(stack, env_file)

    output_path = (args.output.resolve() if args.output else default_output_path(stack.name, env["POSTGRES_DB"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = run_compose(
        stack,
        env=env,
        env_file=env_file,
        args=[
            "exec",
            "-T",
            "-e",
            f"PGPASSWORD={env['POSTGRES_PASSWORD']}",
            "postgres",
            "pg_dump",
            "-U",
            env["POSTGRES_USER"],
            "-d",
            env["POSTGRES_DB"],
            "-Fc",
            "--no-owner",
            "--no-privileges",
        ],
    )

    if result.returncode != 0:
        raise SystemExit(
            f"Backup failed.\nSTDOUT:\n{result.stdout.decode('utf-8', errors='replace')}\nSTDERR:\n{result.stderr.decode('utf-8', errors='replace')}"
        )

    output_path.write_bytes(result.stdout)
    print(f"Backup created at {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
