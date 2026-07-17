"""
Use case 07 — Sync a local directory to the CCMS (upload changed files).

Walks a local directory tree and uploads every file to the corresponding
remote path. Intended for CI/CD workflows such as deploying an updated
schematron rule set or a DITA-OT plugin.

This is a one-way sync (local → remote). It does NOT delete remote files
that no longer exist locally.

Run:
    python src/use_cases/07_sync_directory.py <local_dir> <url>

Example:
    python src/use_cases/07_sync_directory.py \\
        ./schematron-rules \\
        https://pstest.heretto.com/webdav/db/organizations/pstest/schematron/
"""

import argparse
import sys
sys.path.insert(0, "src")

from pathlib import Path

from heretto_webdav import HerettoWebDavClient


CONTENT_TYPES = {
    ".dita": "application/xml",
    ".ditamap": "application/xml",
    ".xml": "application/xml",
    ".sch": "application/xml",
    ".json": "application/json",
    ".css": "text/css",
    ".xsl": "application/xml",
    ".xslt": "application/xml",
}


def content_type_for(path: Path) -> str:
    return CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sync a local directory to the Heretto CCMS WebDAV interface."
    )
    parser.add_argument("local_dir", help="Local directory to sync.")
    parser.add_argument("url", help="Full WebDAV URL of the remote base directory.")
    return parser.parse_args()


def main():
    args = parse_args()
    client = HerettoWebDavClient()

    try:
        remote_base = client.path_from_url(args.url).rstrip("/")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    local_root = Path(args.local_dir)
    if not local_root.exists():
        print(f"Error: local directory not found: {local_root}", file=sys.stderr)
        sys.exit(1)

    uploaded = 0
    for filepath in sorted(local_root.rglob("*")):
        if not filepath.is_file():
            continue

        relative = filepath.relative_to(local_root)
        remote_path = f"{remote_base}/{relative}"

        print(f"  Uploading {relative} -> {remote_path}")
        client.upload(filepath, remote_path, content_type=content_type_for(filepath))
        uploaded += 1

    print(f"\nSync complete. {uploaded} file(s) uploaded.")


if __name__ == "__main__":
    main()
