from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from postgres_compose_ops import (
    ROOT,
    build_compose_env,
    resolve_stack,
    utc_timestamp_for_filename,
    write_backup_failure_event,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a recurring PostgreSQL backup using the existing compose backup workflow."
    )
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
        "--output-dir",
        type=Path,
        help="Optional output directory. Defaults to backups/<stack>/",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=7,
        help="How many recent backups to keep in the target directory. Defaults to 7.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the backup command and pruning plan without changing files.",
    )
    return parser.parse_args()


def backup_files_in(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.dump"), key=lambda path: path.name, reverse=True)


def metadata_path_for(dump_path: Path) -> Path:
    return dump_path.with_suffix(f"{dump_path.suffix}.metadata.json")


def prune_old_backups(directory: Path, keep: int, *, dry_run: bool) -> None:
    dumps = backup_files_in(directory)
    for old_dump in dumps[keep:]:
        metadata_path = metadata_path_for(old_dump)
        if dry_run:
            print(f"[dry-run] would remove {old_dump}")
            if metadata_path.exists():
                print(f"[dry-run] would remove {metadata_path}")
            continue

        old_dump.unlink(missing_ok=True)
        if metadata_path.exists():
            metadata_path.unlink()


def run_backup(
    stack: str,
    *,
    env_file: Path | None,
    output_path: Path,
    dry_run: bool,
) -> None:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "backup_postgres_compose.py"),
        "--stack",
        stack,
        "--output",
        str(output_path),
    ]
    if env_file is not None:
        command.extend(["--env-file", str(env_file)])

    if dry_run:
        print("[dry-run] backup command:")
        print(" ".join(command))
        return

    result = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        event_path = write_backup_failure_event(
            stack_name=stack,
            database_name="unknown",
            step="scheduled_backup_execution",
            exit_code=result.returncode,
            message="The underlying backup command failed. Check script output.",
        )
        error_msg = (
            "======================================================================\n"
            "[SCHEDULED_BACKUP_ERROR] The underlying backup command failed\n"
            f"Target Stack: {stack} | Output Dir: {output_path.parent}\n"
            "======================================================================\n"
            f"Command Executed: {' '.join(command)}\n"
            "======================================================================\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            "======================================================================\n"
            "ACTION RECOMMENDED: Check the underlying backup script output above.\n"
            "Ensure enough disk space and that the stack is running.\n"
            f"Alert payload written to: {event_path}\n"
            "Reference: docs/backup-failure-visibility-foundation.md\n"
            "======================================================================"
        )
        raise SystemExit(error_msg)

    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)


def main() -> int:
    args = parse_args()
    if args.keep < 1:
        raise SystemExit("--keep must be greater than or equal to 1.")

    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (ROOT / "backups" / args.stack).resolve()
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    env_file = args.env_file.resolve() if args.env_file else None
    stack_config = resolve_stack(args.stack)
    env = build_compose_env(stack_config, env_file)
    output_path = output_dir / (
        f"{args.stack}-{env['POSTGRES_DB']}-{utc_timestamp_for_filename()}.dump"
    )

    run_backup(
        args.stack,
        env_file=env_file,
        output_path=output_path,
        dry_run=args.dry_run,
    )
    prune_old_backups(output_dir, args.keep, dry_run=args.dry_run)
    print(f"Retention complete for {output_dir} (keep={args.keep})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
