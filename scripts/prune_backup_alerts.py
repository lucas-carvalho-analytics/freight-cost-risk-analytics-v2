from __future__ import annotations

import argparse
from pathlib import Path

from postgres_compose_ops import ROOT

ALERTS_DIR = ROOT / "backups" / "alerts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prune old consumed backup alerts to prevent unbounded growth."
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=50,
        help="How many recent processed alerts to keep. Defaults to 50.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show which alerts would be pruned without actually deleting them.",
    )
    return parser.parse_args()


def processed_alerts_in(directory: Path) -> list[Path]:
    # Only target safely processed files to prevent dropping live actionable alerts
    return sorted(directory.glob("*.processed"), key=lambda path: path.name, reverse=True)


def prune_old_alerts(directory: Path, keep: int, *, dry_run: bool) -> int:
    processed_files = processed_alerts_in(directory)
    pruned_count = 0
    
    for old_file in processed_files[keep:]:
        if dry_run:
            print(f"[dry-run] would delete {old_file.name}")
        else:
            old_file.unlink(missing_ok=True)
            print(f"Deleted {old_file.name}")
        pruned_count += 1
        
    return pruned_count


def main() -> int:
    args = parse_args()
    if args.keep < 0:
        raise SystemExit("--keep must be greater than or equal to 0.")

    if not ALERTS_DIR.is_dir():
        print(f"Alerts directory not found: {ALERTS_DIR}")
        return 0

    print(f"Starting alert pruning in {ALERTS_DIR} (keep={args.keep})")
    count = prune_old_alerts(ALERTS_DIR, args.keep, dry_run=args.dry_run)
    print(f"Pruning complete. {count} old processed alert(s) wiped.")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
