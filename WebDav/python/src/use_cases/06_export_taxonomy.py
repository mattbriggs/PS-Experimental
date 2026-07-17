"""
Use case 06 — Export a SKOS taxonomy from the CCMS.

Downloads a named taxonomy file from the taxonomies collection and saves
it locally. Useful for exporting taxonomy data for external processing,
version control, or migration.

Run:
    python src/use_cases/06_export_taxonomy.py <taxonomy_name> [-o output]

Example:
    python src/use_cases/06_export_taxonomy.py taxonomist.xml
    python src/use_cases/06_export_taxonomy.py product-taxonomy.xml -o my-taxonomy.xml
"""

import argparse
import sys
sys.path.insert(0, "src")

from heretto_webdav import HerettoWebDavClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export a SKOS taxonomy file from the Heretto CCMS."
    )
    parser.add_argument(
        "taxonomy_name",
        help="Filename of the taxonomy in the taxonomies collection (e.g. taxonomist.xml).",
    )
    parser.add_argument(
        "-o", "--output",
        help="Local output path (default: same as taxonomy_name).",
        default=None,
    )
    return parser.parse_args()


def main():
    args = parse_args()
    client = HerettoWebDavClient()

    remote = client.taxonomy_path(args.taxonomy_name)
    local_output = args.output or args.taxonomy_name

    print(f"Exporting taxonomy: {remote}")
    dest = client.download(remote, local_output)
    print(f"Saved to: {dest}")


if __name__ == "__main__":
    main()
