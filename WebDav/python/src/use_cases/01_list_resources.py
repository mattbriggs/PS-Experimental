"""
Use case 01 — List resources in a directory.

Demonstrates PROPFIND Depth: 1 against the organization content root.
Shows how to distinguish files from collections in the response.

Run:
    python src/use_cases/01_list_resources.py
"""

import sys
sys.path.insert(0, "src")

from heretto_webdav import HerettoWebDavClient


def main():
    client = HerettoWebDavClient()

    # List the organization repositories root (one level deep)
    path = client.repositories_path()
    print(f"Listing: {path}\n")

    resources = client.list_directory(path, depth=1)

    # Skip the first entry — it is the directory itself
    for resource in resources[1:]:
        marker = "[DIR] " if resource["type"] == "directory" else "[FILE]"
        print(f"  {marker} {resource['href']}")

    print(f"\n{len(resources) - 1} items found.")


if __name__ == "__main__":
    main()
