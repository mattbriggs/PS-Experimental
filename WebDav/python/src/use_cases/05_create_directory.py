"""
Use case 05 — Create a new directory (collection) in the CCMS.

Demonstrates MKCOL to create a directory at a given path.
The parent directory must already exist — WebDAV does not create
intermediate directories automatically.

Run:
    python src/use_cases/05_create_directory.py <url>

Example:
    python src/use_cases/05_create_directory.py \\
        https://pstest.heretto.com/webdav/db/organizations/pstest/repositories/new-section/
"""

import argparse
import sys
sys.path.insert(0, "src")

from heretto_webdav import HerettoWebDavClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a directory in the Heretto CCMS WebDAV interface."
    )
    parser.add_argument("url", help="Full WebDAV URL of the directory to create.")
    return parser.parse_args()


def main():
    args = parse_args()
    client = HerettoWebDavClient()

    try:
        remote_path = client.path_from_url(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Creating directory: {remote_path}")
    client.create_directory(remote_path)
    print("Directory created.")


if __name__ == "__main__":
    main()
