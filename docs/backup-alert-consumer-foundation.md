# Backup Alert Consumer Foundation

This document details the foundation for local alert consumption. 

## Purpose

When a backup or scheduling step fails (architected in the failure visibility foundation), a structured JSON event is deposited logically in `backups/alerts/`. The **Consumer Foundation** introduces `consume_backup_alerts.py` to read these local payload queues, print a human-readable operational summary, and mark them as `.processed` to avoid re-triggering.

## Usage

This can be run by an overarching orchestration flow (like an alert-reader cron job) or locally by an operator:

```bash
# Dry run: reads alerts without marking them as processed
python scripts/consume_backup_alerts.py --dry-run
```

```bash
# Consume and mark alerts as processed
python scripts/consume_backup_alerts.py
```

## Architectural Benefits

1. **Idempotency**: By renaming consumed files to `*.json.processed`, we ensure standard alerts aren't systematically spammed multiple times to on-call squads, keeping the noise to a minimum.
2. **Readiness for the outside world**: In the future, this exact Python consumer logic can be extended minimally to wrap HTTP requests that send Slack or Webhook API calls, using standard credentials pulled from AWS / secrets manager, bridging the gap safely.
3. **Decoupled execution**: A failing backup script shouldn't hang or crash the worker pod entirely just because a webhook integration is momentarily timing out. The event rests passively in a file wait-stage until this consumer pulls it reliably.
