"""
Use case 04 — Delete a file from the CCMS.

Demonstrates DELETE against a specific resource path.

WARNING: This permanently removes the file from the CCMS. Do not point
this at a directory — DELETE on a collection removes all contents
recursively without confirmation.

Run:
    python src/use_cases/04_delete_resource.py <url> [--yes]

Example:
    python src/use_cases/04_delete_resource.py \\
        https://pstest.heretto.com/webdav/db/organizations/pstest/repositories/obsolete-topic.dita
"""

import argparse
import sys
sys.path.insert(0, "src")

from heretto_webdav import HerettoWebDavClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Delete a file from the Heretto CCMS WebDAV interface."
    )
    parser.add_argument("url", help="Full WebDAV URL of the file to delete.")
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip the confirmation prompt.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    client = HerettoWebDavClient()

    try:
        remote_path = client.path_from_url(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.yes:
        confirm = input(f"Delete {remote_path}? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    client.delete(remote_path)
    print(f"Deleted: {remote_path}")


if __name__ == "__main__":
    main()
