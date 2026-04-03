# Backup Encrypted Flow Foundation

This stage integrates the previously isolated local encryption utility directly into the core backup generation pipeline. 

## Architectural Behavior

When `backup_postgres_compose.py` succeeds in creating a validated `pg_dump`:

1. **Encryption Phase (Optional)**: If `BACKUP_ENCRYPTION_KEY` is present in the environment block, the root script triggers `crypto_backup.py` internally to yield a `.dump.enc` symmetric artifact.
2. **Post-Encryption Wipe**: If the `.enc` generation outputs successfully without crashes, the original local `.dump` (raw SQL) is immediately and permanently `unlink`ed from the file system. Thus, operators do not need to worry about plain-text backups residing on the disk asynchronously.
3. **Remote Upload Transfer (Optional)**: If `BACKUP_REMOTE_DESTINATION` is also provided in the environment string, the upload system transparently detects the payload modification. It seamlessly passes the newly generated `.dump.enc` to the remote path along with its sister metadata record.

## Error Handling

If encryption encounters a fatal failure midway, the system aggressively aborts the downstream execution of the remote upload phase but leaves the core raw dump safely on disk as a fallback measure. The terminal fails explicitly, dropping the execution context immediately.

## Restore Strategy

The operator's `restore_postgres_compose.py` does logically intercept encrypted files yet natively. For now, an operator retrieving a `.enc` file (remotely or locally) must manually run `crypto_backup.py decrypt --file path_to.enc` before feeding it back into the local dump restore mechanisms.
