from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt backup dumps securely."
    )
    parser.add_argument(
        "action",
        choices=["encrypt", "decrypt"],
        help="Action to perform on the target file.",
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Path to the file to encrypt or decrypt.",
    )
    return parser.parse_args()


def run_openssl(action: str, input_path: Path, output_path: Path, key: str) -> None:
    # AES-256-CBC with PBKDF2 key derivation ensures strong modern symmetric protection natively
    cmd = [
        "openssl", "enc", "-aes-256-cbc", "-pbkdf2"
    ]
    if action == "decrypt":
        cmd.append("-d")
    
    cmd.extend([
        "-in", str(input_path),
        "-out", str(output_path),
        "-pass", f"pass:{key}"
    ])

    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] OpenSSL failed with exit code {e.returncode}")
        print(f"Details: {e.stderr.strip()}")
        if output_path.exists():
            output_path.unlink() # Cleanup partial/failed output
        raise SystemExit(1)


def main() -> int:
    args = parse_args()
    source_file = args.file.resolve()

    if not source_file.exists():
        print(f"[ERROR] Target file does not exist: {source_file}")
        return 1

    encryption_key = os.environ.get("BACKUP_ENCRYPTION_KEY")
    if not encryption_key:
        print("[ERROR] BACKUP_ENCRYPTION_KEY environment variable is severely missing.")
        print("Aborting to prevent unencrypted operations or silent failures.")
        return 1

    if args.action == "encrypt":
        target_file = source_file.with_suffix(f"{source_file.suffix}.enc")
        print(f"Encrypting {source_file.name}...")
        run_openssl("encrypt", source_file, target_file, encryption_key)
        print(f"✅ Created encrypted artifact: {target_file.name}")
    else:
        # Decrypt flow
        if not source_file.name.endswith(".enc"):
            print(f"[WARNING] File {source_file.name} does not appear to end in .enc")
            
        target_file = source_file.with_suffix("") # Strip .enc
        # If it was just .enc without other suffix, we fallback cleanly
        if target_file == source_file: 
            target_file = source_file.with_name(f"{source_file.name}.decrypted")
            
        print(f"Decrypting {source_file.name}...")
        run_openssl("decrypt", source_file, target_file, encryption_key)
        print(f"✅ Successfully decrypted to: {target_file.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
