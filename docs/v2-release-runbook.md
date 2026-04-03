# Freight Cost Risk Analytics V2 - Final Release Runbook

This document specifies the frozen operational baseline for V2, certifying production readiness for a single organizational domain.

## Verified Baselines
### Application
- **Backend**: Pydantic/FastAPI endpoints properly validating and authenticating traffic. Test coverage passes cleanly in CI.
- **Frontend**: Vue/Vite or React MVP statically compiling cleanly into `dist` and served via NGINX with strict CSRF/CORS configurations.
- **Compose Stacks**: Both `demo` and `production-foundation` Compose graphs validate without syntax decay, mapping networks and volumes securely. 
- **Role Base**: KPI routes logically protected by hardcoded credential requirements embedded in `.env`/auth middleware.

## Backup & Disaster Recovery Architecture
The `V2` architecture includes a robust, resilient system designed to protect state without polluting local host drives or exposing plaintext:

1. **Scheduling**: A crontab hook calls `scripts/run_scheduled_backup.py --stack [NAME]` periodically.
2. **Generation**: `pg_dump` creates a localized SQL dump stream, verified natively against `pg_restore`.
3. **Cryption**: The engine instantly encrypts the payload (`crypto_backup.py`) via AES-256-CBC relying on `BACKUP_ENCRYPTION_KEY`. The original plaintext is aggressively wiped (`unlink`) from local drives upon successful cipher injection.
4. **Transport**: The `upload_backup_remote.py` module discovers the `.enc` artifact and its JSON sister metadata file, shifting both payloads entirely out of host storage utilizing external Cloud protocols.
5. **Observability**: If the container execution fails to reach valid dumping state, an isolated alert JSON is dropped out-of-band in `backups/alerts/`. 
6. **Notification**: The queue consumer `consume_backup_alerts.py` fires an HTTP POST notification towards `BACKUP_ALERT_WEBHOOK_URL` natively. Old alerts are auto-pruned to preserve host inodes.
7. **Restoration**: To revive an encrypted dump, the operator sequentially runs `restore_postgres_compose.py` passing `--input foo.dump.enc`. The internal machinery temporarily decrypts strictly to Memory buffer bytes, `unlinks` the temp disk text immediately, and restores directly against the runtime PostgreSQL socket.

## Operational Constraints (For V3 Expansion)
Do not treat this baseline as a zero-trust multi-cloud distributed system yet. We intentionally constrained the following:

- **Key Management**: We rely on static `os.environ` keys rather than dynamic KMS/Vault integrations. Loss of the key = permanent loss of the backups.
- **Restore Source**: The automation expects the encrypted dump locally available; `curl` or automated `s3://` fetches ahead of restore have not been coded yet.
- **Event Mesh**: Webhooks are straightforward HTTP POSTs, not dead-letter-queued Kafka streams.

We certify that this codebase is operationally mature to operate an MVP Data application within an internal/closed cluster environment.
