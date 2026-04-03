# Backup Failure Visibility Foundation

This document outlines the standard operational procedure and troubleshooting guidelines when a backup fails in this repository.

## Operational Context

The backup scripts (`backup_postgres_compose.py` and `run_scheduled_backup.py`) have been improved to emit structured error blocks that provide crucial troubleshooting information directly in standard output/error paths.

When a scheduled or manual backup fails, look for the following blocks in your CI/CD logs, cron logs, or terminal output:

- `[BACKUP_ERROR]`: Identifies exactly which stage of the backup failed (`pg_dump execution` vs `dump integrity validation`).
- `[SCHEDULED_BACKUP_ERROR]`: Identifies failures wrapper-level constraints (like disk space issues before executing the backup).

### Context Included in Errors
- **Target Stack & Database**: Clearly calls out which compose stack has failed.
- **Stage**: Shows whether `pg_dump` itself failed or the validation step (`pg_restore --list`) failed.
- **STDOUT / STDERR**: The raw output exactly as returned by Docker/Postgres processes.

## Common Failure Modes & Recommended Actions

### 1. `pg_dump execution` Failures
**Symptom**: The script fails with `[BACKUP_ERROR] Stage: pg_dump execution`.
**Likely Causes**:
- The Postgres container may be stopped, restarting, or unhealthy.
- Wrong credentials or no network connectivity to the docker daemon.
- Disk space exhausted in the host preventing Docker exec.
**Action**:
- Run `docker compose ps` to inspect running services.
- Check service logs: `docker compose logs postgres`.

### 2. `dump integrity validation` Failures
**Symptom**: The script fails with `[BACKUP_ERROR] Stage: dump integrity validation`.
**Likely Causes**:
- File was written partially (perhaps out of space locally).
- Corrupted Postgres catalog causing partial dump success but validation failure.
**Action**:
- Manually inspect the dump size in the `backups/<stack>` directory.
- Attempt to read the dump using `pg_restore --list <dump_file>`.

### 3. `Scheduled Backup Command` Failures
**Symptom**: The script fails with `[SCHEDULED_BACKUP_ERROR]`.
**Likely Causes**:
- An error in `run_scheduled_backup.py` trying to invoke the python interpreter or sub-scripts.
- Permissions error on the host filesystem when attempting to write backups or metadata.
**Action**:
- Verify the output directory permissions.
- Validate python environment variables and subprocess paths in `run_scheduled_backup.py`.

## Next Steps Evolution
In future features, this structured stdout output format will make it easy to scrape for `[BACKUP_ERROR]` lines using standard observability tools or simple Slack webhook wrappers, laying the foundation for remote alerting.
