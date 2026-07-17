"""
Use case 02 — Download a single file from the CCMS.

Accepts the full WebDAV URL as a positional argument and saves the file
to the current working directory using the remote filename.

Run:
    python src/use_cases/02_download_resource.py <url> [-o output]

Example:
    python src/use_cases/02_download_resource.py \\
        https://pstest.heretto.com/webdav/db/organizations/pstest/taxonomies/taxonomist.xml
"""

import argparse
import sys
sys.path.insert(0, "src")

from heretto_webdav import HerettoWebDavClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download a single file from the Heretto CCMS WebDAV interface."
    )
    parser.add_argument(
        "url",
        help="Full WebDAV URL of the file to download.",
    )
    parser.add_argument(
        "-o", "--output",
        help="Local output path (default: filename from the URL).",
        default=None,
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

    local_output = args.output or remote_path.rstrip("/").split("/")[-1]

    print(f"Downloading: {remote_path}")
    dest = client.download(remote_path, local_output)
    print(f"Saved to:    {dest}")


if __name__ == "__main__":
    main()
