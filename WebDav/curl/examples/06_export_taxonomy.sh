#!/usr/bin/env bash
# Use case 06 — Export a SKOS taxonomy from the CCMS
#
# Downloads a named taxonomy file from the taxonomies collection.
# Useful for exporting taxonomy data for version control, external
# processing, or migration preparation.
#
# Update TAXONOMY_NAME and OUTPUT_FILE before running.
#
# Prerequisites: source ../.env (or export variables manually)

set -euo pipefail

: "${HERETTO_ORG:?Set HERETTO_ORG}"
: "${HERETTO_USER:?Set HERETTO_USER}"
: "${HERETTO_TOKEN:?Set HERETTO_TOKEN}"

BASE="https://${HERETTO_ORG}.heretto.com/webdav"

TAXONOMY_NAME="product-taxonomy.xml"
OUTPUT_FILE="exported-taxonomy.xml"

REMOTE_PATH="/db/organizations/${HERETTO_ORG}/taxonomies/${TAXONOMY_NAME}"

echo "Exporting: ${BASE}${REMOTE_PATH}"
echo "Saving to: ${OUTPUT_FILE}"
echo "---"

curl --silent \
  --user "${HERETTO_USER}:${HERETTO_TOKEN}" \
  --output "${OUTPUT_FILE}" \
  --write-out "HTTP %{http_code} — %{size_download} bytes\n" \
  "${BASE}${REMOTE_PATH}"
