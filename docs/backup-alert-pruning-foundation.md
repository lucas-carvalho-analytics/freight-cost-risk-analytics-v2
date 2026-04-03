# Backup Alert Pruning Foundation

This document defines the foundation for local retention and pruning of operational backup alerts.

## Purpose

To prevent unbounded disk growth within the `backups/alerts/` directory, old events that have already been consumed and tracked must eventually be deleted. The **Alert Pruning Foundation** incorporates `prune_backup_alerts.py` to scrub aging payload caches deterministically.

## Safety Constraints (Rules of Engagement)

1. **Active Files are Immune**: The script *strictly* targets files ending in `.processed`. It will never delete a fresh `*-event.json` that has not yet been processed by the consumer logic.
2. **Quantity-based Retention**: It relies on file counting (`--keep`) sorted dynamically by timestamp rather than complex date-math. It guarantees you will always have the N most recent processed alerts historically available for manual audit.

## Usage

You can invoke this logic manually or hook it neatly into your cron schedules just after running the standard consumer script.

```bash
# Dry run: previews which processed logs would be expunged, protecting the newest 10
python scripts/prune_backup_alerts.py --keep 10 --dry-run
```

```bash
# Delete all consumed logs except for the last 50
python scripts/prune_backup_alerts.py --keep 50
```

## Architectural Benefits

1. **Storage Predictability**: Bounds the max inode depth of the alerts queue, keeping the directory perfectly healthy indefinitely.
2. **Easy Audit Trace**: Operators retain a limited historic log of what previously failed simply by visually inspecting the `backups/alerts/` directory. By keeping the last 50 events, troubleshooting recurring failures gets easier.
