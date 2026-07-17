#!/usr/bin/env bash
# Use case 07 — Backup and deploy a schematron rule set
#
# Demonstrates a safe deployment pattern for schematron rule files:
#   1. Download the current live file as a timestamped backup.
#   2. Upload the new version.
#
# This script is suitable for use in a CI/CD pipeline step.
# The LOCAL_FILE variable points to the file produced by your build.
#
# Update LOCAL_FILE and RULE_NAME before running.
#
# Prerequisites: source ../.env (or export variables manually)

set -euo pipefail

: "${HERETTO_ORG:?Set HERETTO_ORG}"
: "${HERETTO_USER:?Set HERETTO_USER}"
: "${HERETTO_TOKEN:?Set HERETTO_TOKEN}"

BASE="https://${HERETTO_ORG}.heretto.com/webdav"

RULE_NAME="custom-rules.sch"
LOCAL_FILE="./${RULE_NAME}"
SCHEMATRON_DIR="/db/organizations/${HERETTO_ORG}/schematron"
REMOTE_FILE="${SCHEMATRON_DIR}/${RULE_NAME}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}_${RULE_NAME}"

# --- Step 1: Download current version as backup ---

echo "Step 1: Backing up current rule set to ${BACKUP_FILE}"

HTTP_STATUS=$(
  curl --silent \
    --user "${HERETTO_USER}:${HERETTO_TOKEN}" \
    --output "${BACKUP_FILE}" \
    --write-out "%{http_code}" \
    "${BASE}${REMOTE_FILE}"
)

if [[ "${HTTP_STATUS}" == "200" ]]; then
  echo "  Backup saved: ${BACKUP_FILE}"
elif [[ "${HTTP_STATUS}" == "404" ]]; then
  echo "  No existing file found — skipping backup (first deploy)."
  rm -f "${BACKUP_FILE}"
else
  echo "  Backup failed with HTTP ${HTTP_STATUS}. Aborting."
  exit 1
fi

# --- Step 2: Create a placeholder if local file is missing ---

if [[ ! -f "${LOCAL_FILE}" ]]; then
  cat > "${LOCAL_FILE}" <<'XML'
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
  <title>Custom Rules — placeholder created by use case 07</title>
</schema>
XML
  echo "  Created placeholder: ${LOCAL_FILE}"
fi

# --- Step 3: Upload the new version ---

echo "Step 2: Deploying ${LOCAL_FILE} -> ${BASE}${REMOTE_FILE}"

HTTP_STATUS=$(
  curl --silent \
    --request PUT \
    --user "${HERETTO_USER}:${HERETTO_TOKEN}" \
    --header "Content-Type: application/xml" \
    --data-binary "@${LOCAL_FILE}" \
    --write-out "%{http_code}" \
    "${BASE}${REMOTE_FILE}"
)

if [[ "${HTTP_STATUS}" =~ ^(200|201|204)$ ]]; then
  echo "  Deploy complete (HTTP ${HTTP_STATUS})."
else
  echo "  Deploy failed with HTTP ${HTTP_STATUS}."
  exit 1
fi
