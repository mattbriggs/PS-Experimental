#!/usr/bin/env bash
# Use case 04 — Delete a file from the CCMS
#
# Uses HTTP DELETE to permanently remove a resource.
#
# WARNING: DELETE on a collection (directory) removes all contents
# recursively without confirmation. This script targets a single file.
#
# Update REMOTE_FILE to the real path you intend to delete.
# The script prompts for confirmation before proceeding.
#
# Prerequisites: source ../.env (or export variables manually)

set -euo pipefail

: "${HERETTO_ORG:?Set HERETTO_ORG}"
: "${HERETTO_USER:?Set HERETTO_USER}"
: "${HERETTO_TOKEN:?Set HERETTO_TOKEN}"

BASE="https://${HERETTO_ORG}.heretto.com/webdav"

# Update this path to the file you intend to delete.
REMOTE_FILE="/db/organizations/${HERETTO_ORG}/content/topics/obsolete-topic.dita"

echo "Target: ${BASE}${REMOTE_FILE}"
read -r -p "Delete this file? [y/N] " CONFIRM

if [[ "${CONFIRM}" != "y" && "${CONFIRM}" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

echo "---"

curl --silent \
  --request DELETE \
  --user "${HERETTO_USER}:${HERETTO_TOKEN}" \
  --write-out "HTTP %{http_code}\n" \
  "${BASE}${REMOTE_FILE}"
