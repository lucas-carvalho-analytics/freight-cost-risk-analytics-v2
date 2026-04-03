# Backup Failure Alerting Foundation

This document details the foundation for operational signaling of backup failures. 
The goal of this phase is to emit a standardized failure event payload locally whenever a backup operation drops or gets corrupted, so that future integrations (like Cron, an external monitoring agent, or a simple Slack Python webhook script) can consume these signals without having to parse complex `stderr` logic.

## The Alert Payload
When a backup script fails, it automatically deposits a JSON file within `backups/alerts/`.
Example path: `backups/alerts/demo-freight_analytics-20260403T142010Z-failure-event.json`

The payload schema is highly structured:
```json
{
  "event": "backup_failure",
  "step": "pg_dump_execution",
  "exit_code": 1,
  "stack": "demo",
  "database": "freight_analytics",
  "timestamp_utc": "2026-04-03T14:20:10.123456+00:00",
  "message": "service \"postgres\" is not running"
}
```

### Supported Steps
The `step` field will typically be one of the following:
- `pg_dump_execution`: Failed to execute the `pg_dump` binary within the container (e.g. database not running, wrong credentials).
- `dump_integrity_validation`: Dump generated successfully, but corrupted and failed to pass `pg_restore --list`.
- `scheduled_backup_execution`: An overarching failure at the scheduler level (e.g. wrapper script crashed, missing dependencies, permissions denied).

## Operational Consumption

For now, this event file exists simply as a sidecar record of the error.
In future phases, you can wire alert notifications quickly by:
1. Having an observability agent (e.g., FluentBit, Datadog Agent) watch the `backups/alerts/*.json` path.
2. Building a small `notify_slack.py` script that receives these JSON payloads and fires an alert webhook directly.

By standardizing the payload here, the `freight-cost-risk-analytics-v2` project ensures that adding alerting is just a matter of reading a JSON object instead of building regex-based error log parsers.
