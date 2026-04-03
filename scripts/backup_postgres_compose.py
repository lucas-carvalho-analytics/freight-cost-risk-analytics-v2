from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from postgres_compose_ops import (
    ROOT,
    build_compose_env,
    dump_sha256,
    resolve_stack,
    run_compose,
    utc_timestamp_for_filename,
    utc_timestamp_iso,
    validate_dump_with_pg_restore,
    write_backup_failure_event,
    write_backup_metadata,
)


def default_output_path(stack_name: str, database_name: str) -> Path:
    timestamp = utc_timestamp_for_filename()
    return ROOT / "backups" / stack_name / f"{stack_name}-{database_name}-{timestamp}.dump"


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
        event_path = write_backup_failure_event(
            stack_name=stack.name,
            database_name=env["POSTGRES_DB"],
            step="pg_dump_execution",
            exit_code=result.returncode,
            message=result.stderr.decode("utf-8", errors="replace").strip() or "pg_dump failed to execute.",
        )
        error_msg = (
            "======================================================================\n"
            "[BACKUP_ERROR] Stage: pg_dump execution\n"
            f"Target Stack: {stack.name} | Database: {env['POSTGRES_DB']}\n"
            "======================================================================\n"
            f"STDOUT:\n{result.stdout.decode('utf-8', errors='replace')}\n"
            f"STDERR:\n{result.stderr.decode('utf-8', errors='replace')}\n"
            "======================================================================\n"
            "ACTION RECOMMENDED: Check if database container is running and accepting connections.\n"
            f"Alert payload written to: {event_path}\n"
            "Reference: docs/backup-failure-visibility-foundation.md\n"
            "======================================================================"
        )
        raise SystemExit(error_msg)

    dump_bytes = result.stdout
    validate_dump_with_pg_restore(
        stack,
        env=env,
        env_file=env_file,
        dump_bytes=dump_bytes,
    )

    output_path.write_bytes(dump_bytes)
    sha256 = dump_sha256(dump_bytes)
    metadata_path = write_backup_metadata(
        output_path,
        {
            "backup_version": 1,
            "stack": stack.name,
            "database": env["POSTGRES_DB"],
            "postgres_user": env["POSTGRES_USER"],
            "created_at_utc": utc_timestamp_iso(),
            "dump_format": "pg_dump_custom",
            "sha256": sha256,
            "size_bytes": len(dump_bytes),
            "file_name": output_path.name,
        },
    )
    print(f"Backup created at {output_path}")
    print(f"Backup metadata created at {metadata_path}")
    print(f"Backup sha256: {sha256}")

    if "BACKUP_ENCRYPTION_KEY" in os.environ:
        print("\n--- Encrypting Backup ---")
        try:
            subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "crypto_backup.py"),
                    "encrypt",
                    "--file",
                    str(output_path),
                ],
                check=True,
            )
            encrypted_path = output_path.with_suffix(f"{output_path.suffix}.enc")
            print(f"Encrypted artifact generated successfully: {encrypted_path.name}")
            
            output_path.unlink(missing_ok=True)
            print(f"Raw dump removed securely: {output_path.name}")
            
            output_path = encrypted_path
        except subprocess.CalledProcessError:
            print("[ERROR] Core Encryption Flow Failed! Aborting.")
            raise SystemExit(1)

    if os.environ.get("BACKUP_REMOTE_DESTINATION"):
        print("\n--- Uploading Backup ---")
        try:
            subprocess.run(
                [
                    "python3",
                    str(ROOT / "scripts" / "upload_backup_remote.py"),
                    "--file",
                    str(output_path),
                ],
                check=True,
            )
        except subprocess.CalledProcessError:
            print("[ERROR] Remote Upload Flow Failed! Aborting.")
            raise SystemExit(1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
