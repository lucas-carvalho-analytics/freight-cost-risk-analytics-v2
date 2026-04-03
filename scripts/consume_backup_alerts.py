from __future__ import annotations

import argparse
import json
import os
import urllib.request
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

    report = (
        "========================================\n"
        f"ALERT: {event} | Stack: {stack} | DB: {db}\n"
        f"Step: {step}\n"
        f"Time: {timestamp}\n"
        f"Message:\n{message}\n"
        "========================================\n"
    )
    print(report)

    webhook_url = os.environ.get("BACKUP_ALERT_WEBHOOK_URL")
    if webhook_url:
        payload_bytes = json.dumps({"text": f"```\n{report.strip()}\n```"}).encode("utf-8")
        if not dry_run:
            req = urllib.request.Request(
                webhook_url,
                data=payload_bytes,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req) as response:
                    print(f"Webhook sent successfully. Status: {response.status}")
            except Exception as exc:
                print(f"[ERROR] Failed to send alert webhook: {exc}")
                print(f"Retaining {path.name} for future retry.")
                return
        else:
            print(f"[dry-run] Would send alert webhook to {webhook_url}")

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
