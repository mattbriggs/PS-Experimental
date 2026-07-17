#!/usr/bin/env bash
# Use case 03 — Upload a file to the CCMS
#
# Uses HTTP PUT to write a local file to a remote WebDAV path.
# If the file already exists it will be overwritten.
# If the parent directory does not exist the server returns 409.
# Run 05_create_directory.sh first if the parent is missing.
#
# Update LOCAL_FILE and REMOTE_FILE before running.
#
# Prerequisites: source ../.env (or export variables manually)

set -euo pipefail

: "${HERETTO_ORG:?Set HERETTO_ORG}"
: "${HERETTO_USER:?Set HERETTO_USER}"
: "${HERETTO_TOKEN:?Set HERETTO_TOKEN}"

BASE="https://${HERETTO_ORG}.heretto.com/webdav"

LOCAL_FILE="sample-topic.dita"
REMOTE_FILE="/db/organizations/${HERETTO_ORG}/content/topics/sample-topic.dita"

# Create a minimal placeholder topic if the local file does not exist.
if [[ ! -f "${LOCAL_FILE}" ]]; then
  cat > "${LOCAL_FILE}" <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE topic PUBLIC "-//OASIS//DTD DITA Topic//EN" "topic.dtd">
<topic id="sample">
  <title>Sample Topic</title>
  <body><p>Placeholder created by use case 03.</p></body>
</topic>
XML
  echo "Created placeholder: ${LOCAL_FILE}"
fi

echo "Uploading: ${LOCAL_FILE} -> ${BASE}${REMOTE_FILE}"
echo "---"

curl --silent \
  --request PUT \
  --user "${HERETTO_USER}:${HERETTO_TOKEN}" \
  --header "Content-Type: application/xml" \
  --data-binary "@${LOCAL_FILE}" \
  --write-out "HTTP %{http_code}\n" \
  "${BASE}${REMOTE_FILE}"
