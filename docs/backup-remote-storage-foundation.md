# Backup Remote Storage Foundation

This document defines the foundational abstraction for shipping local PostgreSQL dumps securely to off-site Object Storage (like AWS S3, GCS, Azure Blob, etc).

## Architecture

The script `upload_backup_remote.py` acts as a generic transport adapter. It decouples the core `pg_dump` operation from the heavy lifting of cloud provider SDKs.

Currently, it leverages an environmental toggle mapping `BACKUP_REMOTE_DESTINATION` to a protocol handler. By injecting a URI string, you instruct the pipeline where to send exactly two files per session:
1. `stack-database-TIMESTAMP.dump`
2. `stack-database-TIMESTAMP.dump.metadata.json`

## Supported Protocols

For this foundation phase, the abstraction introduces a validatable Mock protocol. Cloud protocols generate NotImplemented safety catches pending explicit AWS/GCP library inclusions in later stages.

- `mock://` or `file://`: Emulates network upload by writing the output into a segregated folder (e.g., `mock:///tmp/remote_storage_simulation`).
- `s3://` (Upcoming)
- `gs://` (Upcoming)

## Usage

You can trigger a remote upload manually following a dump generation:

```bash
# Validating an upload block against a mock/staging bucket
export BACKUP_REMOTE_DESTINATION="mock:///tmp/my-fake-s3-bucket"
python scripts/upload_backup_remote.py --file backups/demo/demo-freight_analytics-YOUR_TIMESTAMP.dump
```

When left empty, the pipeline respects the default constraint:
```bash
# Safely skips if you are developing locally with no bucket configured
BACKUP_REMOTE_DESTINATION="" python scripts/upload_backup_remote.py ...
# output: Skipping remote storage upload phase natively.
```
