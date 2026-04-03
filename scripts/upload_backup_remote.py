from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a generated SQL dump (and its metadata) to remote storage."
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Path to the local .dump file to upload.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the upload process without transmitting data.",
    )
    return parser.parse_args()


def upload_to_mock_storage(source_file: Path, destination_uri: str, dry_run: bool) -> None:
    # Simulates a remote object storage target locally using mock:// /tmp/fake_bucket
    target_dir = Path(destination_uri.replace("mock://", "").replace("file://", ""))
    
    if dry_run:
        print(f"[dry-run] Would create remote directory: {target_dir}")
        print(f"[dry-run] Would upload {source_file.name} to {target_dir}")
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / source_file.name
    shutil.copy2(source_file, target_path)
    print(f"✅ Successfully uploaded {source_file.name} to mock target: {target_dir}")


def main() -> int:
    args = parse_args()
    source_dump = args.file.resolve()

    if not source_dump.exists():
        print(f"[ERROR] Dump file does not exist: {source_dump}")
        return 1

    metadata_file = source_dump.with_suffix(f"{source_dump.suffix}.metadata.json")

    remote_dest = os.environ.get("BACKUP_REMOTE_DESTINATION")
    if not remote_dest:
        print("[WARNING] BACKUP_REMOTE_DESTINATION is strictly unset.")
        print("Skipping remote storage upload phase natively.")
        return 0

    print(f"Preparing to upload to destination: {remote_dest}")

    if remote_dest.startswith("mock://") or remote_dest.startswith("file://"):
        upload_to_mock_storage(source_dump, remote_dest, args.dry_run)
        if metadata_file.exists():
            upload_to_mock_storage(metadata_file, remote_dest, args.dry_run)
    elif remote_dest.startswith("s3://"):
        print("[ERROR] S3 uploading not fully implemented in this phase.")
        return 1
    elif remote_dest.startswith("gs://"):
        print("[ERROR] GCS uploading not fully implemented in this phase.")
        return 1
    else:
        print(f"[ERROR] Unsupported remote destination protocol: {remote_dest}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
