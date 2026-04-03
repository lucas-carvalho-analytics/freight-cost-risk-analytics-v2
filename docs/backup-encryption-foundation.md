# Backup Encryption Foundation

This document details the foundation for local encryption of backup data. Encrypting locally ensures that if backups are exposed either by remote storage misconfiguration (like an open S3 bucket) or a compromised worker cache, the dumps and secrets inside them remain unreadable.

## Architecture

We use OpenSSL (`AES-256-CBC` with `PBKDF2` key derivation) via standard native hooks instead of managing complex Python third-party encryption libraries (`cryptography`). This guarantees strict compatibility with basic sysadmin toolchains while maximizing pipeline execution speed and dependency simplicity. 

The encryption module `crypto_backup.py` demands an explicit symmetric key supplied by the environment.

## Safety Constraints

1. **Strictly Aborts if Key is Missing**: The script will not silently skip encryption if `BACKUP_ENCRYPTION_KEY` is not set; it throws an error.
2. **Partial Artifact Pruning**: If decryption or encryption crashes midway (e.g. wrong key, interruption), the partial corrupted output file is automatically deleted to prevent deceptive files.
3. **Loss of Key = Data Loss**: Because this is strong symmetric encryption, losing the `BACKUP_ENCRYPTION_KEY` makes recovering the dumps impossible.

## Usage

### Encrypt a Dump

```bash
export BACKUP_ENCRYPTION_KEY="your-very-strong-secret-key-1234"
python scripts/crypto_backup.py encrypt --file backups/demo/demo-freight_analytics-2026.dump

# Produces: backups/demo/demo-freight_analytics-2026.dump.enc
```

### Decrypt a Dump

```bash
export BACKUP_ENCRYPTION_KEY="your-very-strong-secret-key-1234"
python scripts/crypto_backup.py decrypt --file backups/demo/demo-freight_analytics-2026.dump.enc

# Produces: backups/demo/demo-freight_analytics-2026.dump
```
