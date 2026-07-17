#!/usr/bin/env bash
# Use case 05 — Create a new directory (collection) in the CCMS
#
# Uses the WebDAV MKCOL method to create a directory.
# The parent directory must already exist.
#
# Update NEW_DIR before running.
#
# Prerequisites: source ../.env (or export variables manually)

set -euo pipefail

: "${HERETTO_ORG:?Set HERETTO_ORG}"
: "${HERETTO_USER:?Set HERETTO_USER}"
: "${HERETTO_TOKEN:?Set HERETTO_TOKEN}"

BASE="https://${HERETTO_ORG}.heretto.com/webdav"

NEW_DIR="/db/organizations/${HERETTO_ORG}/content/topics/new-section/"

echo "Creating directory: ${BASE}${NEW_DIR}"
echo "---"

curl --silent \
  --request MKCOL \
  --user "${HERETTO_USER}:${HERETTO_TOKEN}" \
  --write-out "HTTP %{http_code}\n" \
  "${BASE}${NEW_DIR}"
