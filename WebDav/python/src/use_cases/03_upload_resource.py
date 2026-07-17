"""
Use case 03 — Upload a file to the CCMS.

Demonstrates PUT to write a local file to a remote WebDAV path.
If the file already exists it will be overwritten.
If the parent directory does not exist the server returns 409 — use
use case 05 to create the parent directory first.

Run:
    python src/use_cases/03_upload_resource.py <local_file> <url>

Example:
    python src/use_cases/03_upload_resource.py \\
        my-topic.dita \\
        https://pstest.heretto.com/webdav/db/organizations/pstest/repositories/my-topic.dita
"""

import argparse
import sys
sys.path.insert(0, "src")

from pathlib import Path

from heretto_webdav import HerettoWebDavClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Upload a local file to the Heretto CCMS WebDAV interface."
    )
    parser.add_argument("local_file", help="Path to the local file to upload.")
    parser.add_argument("url", help="Full WebDAV URL of the destination.")
    parser.add_argument(
        "--content-type",
        default="application/xml",
        help="MIME type to send with the upload (default: application/xml).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    client = HerettoWebDavClient()

    local = Path(args.local_file)
    if not local.exists():
        print(f"Error: local file not found: {local}", file=sys.stderr)
        sys.exit(1)

    try:
        remote_path = client.path_from_url(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Uploading {local} -> {remote_path}")
    client.upload(local, remote_path, content_type=args.content_type)
    print("Upload complete.")


if __name__ == "__main__":
    main()
