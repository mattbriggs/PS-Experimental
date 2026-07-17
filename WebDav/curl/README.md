# cURL — Heretto WebDAV Use Cases

Declarative shell scripts that demonstrate programmatic access to the Heretto CCMS WebDAV interface using `curl`. Each script is self-contained and maps to a single WebDAV operation.

These examples are intended for system integrators who need to understand the raw HTTP exchange before building a production integration, or for quick one-off operations against a live CCMS.

---

## Prerequisites

- `curl` (any reasonably recent version; `--write-out` and `--data-binary` have been stable for years)
- A Heretto CCMS account and API token

### Generate an API Token

1. Sign in to your Heretto CCMS instance.
2. Go to: `https://{org}.heretto.com/tools/token-management/tokens.xql`
3. Create a token with a descriptive name (e.g., `cURL-Dev`).
4. Copy the **login** and **password (token)** — they are not retrievable after you navigate away.

---

## Setup

### Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```bash
export HERETTO_ORG="your-org-subdomain"
export HERETTO_USER="your-token-login"
export HERETTO_TOKEN="your-token-password"
export HERETTO_BASE="https://${HERETTO_ORG}.heretto.com/webdav"
```

Source the file before running any example:

```bash
source .env
```

Alternatively, export the variables directly in your shell session.

---

## Scripts

```
curl/
├── .env.example
├── README.md           This file
└── examples/
    ├── 01_list_resources.sh
    ├── 02_download_resource.sh
    ├── 03_upload_resource.sh
    ├── 04_delete_resource.sh
    ├── 05_create_directory.sh
    ├── 06_export_taxonomy.sh
    └── 07_backup_deploy_schematron.sh
```

---

## Use Cases

### 01 — List Resources

Sends `PROPFIND` with `Depth: 1` against the content root. The response is WebDAV multi-status XML listing all immediate children.

```bash
bash examples/01_list_resources.sh
```

To change depth, edit the `--header "Depth: 1"` line. Use `Depth: infinity` with caution on large trees.

---

### 02 — Download a File

Sends `GET` to download a DITA topic. Update `REMOTE_FILE` in the script to a real path in your CCMS.

```bash
bash examples/02_download_resource.sh
```

Output file: `downloaded-topic.dita` in the current directory.

---

### 03 — Upload a File

Sends `PUT` to upload a local file. Creates a minimal placeholder DITA topic if the local file does not exist.

Update `LOCAL_FILE` and `REMOTE_FILE` before running.

```bash
bash examples/03_upload_resource.sh
```

---

### 04 — Delete a File

Sends `DELETE` for a single file. Prompts for confirmation before proceeding.

Update `REMOTE_FILE` to the file you intend to delete.

```bash
bash examples/04_delete_resource.sh
```

---

### 05 — Create a Directory

Sends `MKCOL` to create a new directory. The parent must already exist.

Update `NEW_DIR` before running.

```bash
bash examples/05_create_directory.sh
```

---

### 06 — Export a Taxonomy

Sends `GET` to download a SKOS taxonomy file from the `taxonomies/` collection.

Update `TAXONOMY_NAME` and `OUTPUT_FILE` before running.

```bash
bash examples/06_export_taxonomy.sh
```

---

### 07 — Backup and Deploy Schematron Rules

A two-step deployment script:
1. Downloads the current live rule file as a timestamped backup.
2. Uploads the new rule file.

Suitable for use as a CI/CD pipeline step. Update `LOCAL_FILE` and `RULE_NAME` before running.

```bash
bash examples/07_backup_deploy_schematron.sh
```

---

## WebDAV Method Quick Reference

| Method | Equivalent to | Use for |
|--------|---------------|---------|
| `PROPFIND` | `ls` / directory listing | List directories, get file metadata |
| `GET` | File download | Download any resource |
| `PUT` | File upload / overwrite | Create or replace a file |
| `DELETE` | Remove file/directory | Delete a resource (recursive on collections) |
| `MKCOL` | `mkdir` | Create a directory |
| `MOVE` | `mv` / rename | Rename or relocate a resource |
| `COPY` | `cp` | Copy a resource |

---

## Authentication

All requests use HTTP Basic authentication with your API token credentials:

```bash
--user "${HERETTO_USER}:${HERETTO_TOKEN}"
```

The `HERETTO_USER` is the login value shown when you create the token.
The `HERETTO_TOKEN` is the password value — treat it as a secret.

---

## Common Path Patterns

```
/webdav/db/organizations/{org}/              Organization root
/webdav/db/organizations/{org}/content/      DITA topics, maps, images
/webdav/db/organizations/{org}/taxonomies/   SKOS taxonomy files
/webdav/db/organizations/{org}/schematron/   Schematron rule sets
```
