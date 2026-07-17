#!/usr/bin/env bash
# Use case 01 — List resources in a directory
#
# Uses WebDAV PROPFIND with Depth: 1 to list the immediate children of the
# organization content root. The response is raw WebDAV multistatus XML.
#
# Depth values:
#   0          Properties of the resource itself only
#   1          Resource and its immediate children (default here)
#   infinity   Full recursive listing — use with caution on large trees
#
# Prerequisites: source ../.env (or export variables manually)

set -euo pipefail

: "${HERETTO_ORG:?Set HERETTO_ORG}"
: "${HERETTO_USER:?Set HERETTO_USER}"
: "${HERETTO_TOKEN:?Set HERETTO_TOKEN}"

BASE="https://${HERETTO_ORG}.heretto.com/webdav"
CONTENT_PATH="/db/organizations/${HERETTO_ORG}/content/"

echo "Listing: ${BASE}${CONTENT_PATH}"
echo "---"

curl --silent \
  --request PROPFIND \
  --user "${HERETTO_USER}:${HERETTO_TOKEN}" \
  --header "Depth: 1" \
  --header "Content-Type: application/xml" \
  "${BASE}${CONTENT_PATH}"
