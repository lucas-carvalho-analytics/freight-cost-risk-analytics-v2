from __future__ import annotations

import argparse
import json
from pathlib import Path

from postgres_compose_ops import ROOT

ALERTS_DIR = ROOT / "backups" / "alerts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consume and display backup failure alerts locally."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Process and display alerts without marking them as consumed.",
    )
    return parser.parse_args()


def process_alert(path: Path, dry_run: bool) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"[ERROR] Found invalid JSON in alert file: {path}")
        return

    event = data.get("event", "UNKNOWN")
    step = data.get("step", "UNKNOWN")
    stack = data.get("stack", "UNKNOWN")
    db = data.get("database", "UNKNOWN")
    timestamp = data.get("timestamp_utc", "UNKNOWN")
    message = data.get("message", "No message provided")

    print("========================================")
    print(f"ALERT: {event} | Stack: {stack} | DB: {db}")
    print(f"Step: {step}")
    print(f"Time: {timestamp}")
    print(f"Message:\n{message}")
    print("========================================\n")

    if not dry_run:
        target_path = path.with_suffix(f"{path.suffix}.processed")
        path.rename(target_path)
        print(f"Marked as processed: {target_path.name}\n")
    else:
        print(f"[dry-run] Would mark {path.name} as processed.\n")


def main() -> int:
    args = parse_args()
    if not ALERTS_DIR.is_dir():
        print(f"Alerts directory not found: {ALERTS_DIR}")
        return 0

    alert_files = sorted(ALERTS_DIR.glob("*-event.json"))
    if not alert_files:
        print("No active alerts to consume.")
        return 0

    print(f"Found {len(alert_files)} active alert(s).\n")
    for alert_file in alert_files:
        process_alert(alert_file, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
