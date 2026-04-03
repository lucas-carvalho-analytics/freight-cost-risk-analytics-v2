from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from postgres_compose_ops import (
    build_compose_env,
    compose_services,
    dump_sha256,
    read_backup_metadata,
    resolve_stack,
    run_compose,
    running_services,
    validate_dump_with_pg_restore,
    ROOT,
)


CONFIRM_FLAG = "--yes-i-understand-this-will-overwrite-data"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restore a PostgreSQL dump into a docker compose stack.")
    parser.add_argument(
        "--stack",
        choices=("demo", "production-foundation"),
        required=True,
        help="Target stack to restore.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Optional env file used by docker compose.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to a dump created by backup_postgres_compose.py.",
    )
    parser.add_argument(
        CONFIRM_FLAG,
        dest="confirmed",
        action="store_true",
        help="Required safety flag to confirm the restore will overwrite the target database.",
    )
    return parser.parse_args()


def run_or_raise(result: object, action: str) -> None:
    completed = result
    if completed.returncode != 0:
        raise RuntimeError(
            f"{action} failed.\nSTDOUT:\n{completed.stdout.decode('utf-8', errors='replace')}\nSTDERR:\n{completed.stderr.decode('utf-8', errors='replace')}"
        )


def main() -> int:
    args = parse_args()
    if not args.confirmed:
        raise SystemExit(f"Restore refused. Re-run with {CONFIRM_FLAG}.")

    input_path = args.input.resolve()
    if not input_path.is_file():
        raise SystemExit(f"Dump file not found: {input_path}")

    decrypted_temp_path = None
    if input_path.name.endswith(".enc"):
        if "BACKUP_ENCRYPTION_KEY" not in os.environ:
            raise SystemExit("[ERROR] Encrypted dump detected but BACKUP_ENCRYPTION_KEY is strictly missing.")
        
        print(f"\n--- Decrypting {input_path.name} ---")
        decrypted_temp_path = input_path.with_suffix("")
        try:
            subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "crypto_backup.py"),
                    "decrypt",
                    "--file",
                    str(input_path),
                ],
                check=True,
            )
            print(f"Decryption successful. Preparing memory payload...")
            input_path = decrypted_temp_path
        except subprocess.CalledProcessError:
            raise SystemExit("[ERROR] Decryption failed! Aborting restore flow.")

    stack = resolve_stack(args.stack)
    env_file = args.env_file.resolve() if args.env_file else None
    env = build_compose_env(stack, env_file)
    
    try:
        dump_bytes = input_path.read_bytes()
        metadata = read_backup_metadata(input_path)
    finally:
        if decrypted_temp_path and decrypted_temp_path.exists():
            decrypted_temp_path.unlink()
            print("Securely removed temporary decrypted disk artifact.")

    if metadata is not None:
        expected_sha = str(metadata.get("sha256", ""))
        actual_sha = dump_sha256(dump_bytes)
        if not expected_sha or expected_sha != actual_sha:
            raise SystemExit(
                f"Metadata integrity check failed for {input_path}. "
                f"expected sha256={expected_sha!r}, actual sha256={actual_sha!r}"
            )

    validate_dump_with_pg_restore(
        stack,
        env=env,
        env_file=env_file,
        dump_bytes=dump_bytes,
    )

    available_services = compose_services(stack, env=env, env_file=env_file)
    currently_running = running_services(stack, env=env, env_file=env_file)

    runtime_services = [
        service
        for service in stack.runtime_services
        if service in available_services and service in currently_running
    ]

    if runtime_services:
        stop_result = run_compose(
            stack,
            env=env,
            env_file=env_file,
            args=["stop", *runtime_services],
        )
        run_or_raise(stop_result, "Stopping runtime services")

    try:
        drop_result = run_compose(
            stack,
            env=env,
            env_file=env_file,
            args=[
                "exec",
                "-T",
                "-e",
                f"PGPASSWORD={env['POSTGRES_PASSWORD']}",
                "postgres",
                "dropdb",
                "--if-exists",
                "-U",
                env["POSTGRES_USER"],
                env["POSTGRES_DB"],
            ],
        )
        run_or_raise(drop_result, "Dropping target database")

        create_result = run_compose(
            stack,
            env=env,
            env_file=env_file,
            args=[
                "exec",
                "-T",
                "-e",
                f"PGPASSWORD={env['POSTGRES_PASSWORD']}",
                "postgres",
                "createdb",
                "-U",
                env["POSTGRES_USER"],
                env["POSTGRES_DB"],
            ],
        )
        run_or_raise(create_result, "Creating target database")

        restore_result = run_compose(
            stack,
            env=env,
            env_file=env_file,
            args=[
                "exec",
                "-T",
                "-e",
                f"PGPASSWORD={env['POSTGRES_PASSWORD']}",
                "postgres",
                "pg_restore",
                "-U",
                env["POSTGRES_USER"],
                "-d",
                env["POSTGRES_DB"],
                "--clean",
                "--if-exists",
                "--no-owner",
                "--no-privileges",
            ],
            input_bytes=dump_bytes,
        )
        run_or_raise(restore_result, "Restoring database")
    finally:
        if runtime_services:
            up_result = run_compose(
                stack,
                env=env,
                env_file=env_file,
                args=["up", "-d", *runtime_services],
            )
            run_or_raise(up_result, "Restarting runtime services")

    print(f"Restore completed from {input_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
