# Encrypted Restore Flow Foundation

This foundation integrates the decryption layer directly into the restore pipeline (`restore_postgres_compose.py`), removing the necessity for manual operator deciphering prior to execution.

## Architectural Behavior

When an operator initiates a restore sequentially targeting a `.dump.enc` file:

1. **Safety Intercept**: The orchestrator checks if `BACKUP_ENCRYPTION_KEY` is present. If missing, it fails fast to prevent opaque errors or corrupt payloads from entering the pipeline.
2. **On-the-fly Decryption**: The orchestrator spawns `crypto_backup.py decrypt` internally, dropping a temporary raw `.dump` file strictly on the local execution disk.
3. **Memory Loading**: Since the Postgres runtime container operates securely over `stdin` (via `pg_restore` pipelining), the orchestrator reads the temporary disk byte payload entirely into Python's fast memory path (`dump_bytes`).
4. **Secure Deletion (`Unlink`)**: Before ever executing stopping vectors or dropping the live databases for Restore initiation, a `finally` intercept securely `unlink`s the temporary decrypted disk artifact. 

## Failsafe Characteristics

Regardless of `pg_restore` crashing midway, database containers failing to restart, or the `dump_bytes` loading encountering bad formatting, the `finally` block guarantees the transient decrypted text rests on the hard disk for the absolute minimum fraction of seconds required to buffer it softly into RAM.

## Usage

```bash
# Still requires the manual target input, but the orchestrator handles the payload translation!
export BACKUP_ENCRYPTION_KEY="your-strong-secret-key-1234"
python scripts/restore_postgres_compose.py --stack demo --input backups/demo/demo-freight_analytics-2026.dump.enc --yes-i-understand-this-will-overwrite-data
```
