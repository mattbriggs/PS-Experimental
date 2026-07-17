#!/usr/bin/env bash
# Use case 02 — Download a single file from the CCMS
#
# Uses a standard HTTP GET to retrieve a DITA topic.
# Update REMOTE_FILE to a real path in your organization.
#
# The file is saved to the current directory with the same basename.
#
# Prerequisites: source ../.env (or export variables manually)

set -euo pipefail

: "${HERETTO_ORG:?Set HERETTO_ORG}"
: "${HERETTO_USER:?Set HERETTO_USER}"
: "${HERETTO_TOKEN:?Set HERETTO_TOKEN}"

BASE="https://${HERETTO_ORG}.heretto.com/webdav"

# Update this path to a real file in your CCMS.
REMOTE_FILE="/db/organizations/${HERETTO_ORG}/content/topics/sample-topic.dita"
LOCAL_FILE="downloaded-topic.dita"

echo "Downloading: ${BASE}${REMOTE_FILE}"
echo "Saving to:   ${LOCAL_FILE}"
echo "---"

curl --silent \
  --user "${HERETTO_USER}:${HERETTO_TOKEN}" \
  --output "${LOCAL_FILE}" \
  --write-out "HTTP %{http_code} — %{size_download} bytes\n" \
  "${BASE}${REMOTE_FILE}"
