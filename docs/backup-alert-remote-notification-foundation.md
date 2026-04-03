# Backup Alert Remote Notification Foundation

This document explains the foundation for sending generated backup failure logic to remote endpoints (e.g., Webhooks for Slack, Microsoft Teams, or custom observability platforms).

## Architecture

We avoid heavy third-party messaging libraries dependencies (like `slack-sdk` or `requests`) by utilizing pure Python's `urllib`. The alert processor natively integrates with local JSON payloads and dispatches them via standard HTTP POST if configured. 

If the webhook transmission fails (network error, timeout, non-2xx status), the script aborts processing for that specific alert. This intentionally prevents the system from renaming the file to `.processed`, allowing the cron to try sending the alert again in the next cycle automatically (Robust Retries by design).

## Usage

Set the `BACKUP_ALERT_WEBHOOK_URL` environment variable before running the consumer. The webhook expects to receive a standard application/json POST body with a `text` field containing the raw markdown layout of the alert.

```bash
# Dry run: previews the HTTP payload and destination without sending it
BACKUP_ALERT_WEBHOOK_URL="https://hooks.slack.com/services/T00/B00/XXX" \
python scripts/consume_backup_alerts.py --dry-run
```

```bash
# Production trigger (usually placed inside a cron job wrapper)
export BACKUP_ALERT_WEBHOOK_URL="https://example.com/webhook/alerts"
python scripts/consume_backup_alerts.py
```

## Security Limits

- Webhook endpoint is fully decoupled from the business back-end.
- Raw payload sizes are very small.
- Only metadata is sent (no database rows/keys/dumps), ensuring GDPR compliance during troubleshooting.
- No continuous daemon polling; script processes existing queue synchronously and exits cleanly.
