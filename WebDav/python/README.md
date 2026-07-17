# Python — Heretto WebDAV Use Cases

Standalone Python scripts that demonstrate programmatic access to the Heretto CCMS WebDAV interface. Each script is a self-contained, runnable example for a specific operation.

These examples are intended for system integrators who need to understand how the WebDAV interface behaves from application code before building a production integration.

---

## Prerequisites

- Python 3.10 or later
- A Heretto CCMS account and API token

### Generate an API Token

1. Sign in to your Heretto CCMS instance.
2. Go to: `https://{org}.heretto.com/tools/token-management/tokens.xql`
3. Create a token with a descriptive name (e.g., `WebDAV-Dev`).
4. Copy the **login** and **password (token)** — they are not retrievable after you navigate away.

---

## Setup

### 1. Create and activate a virtual environment

```bash
cd python/
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or install the package in editable mode (includes dev tools):

```bash
pip install -e ".[dev]"
```

### 3. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```bash
HERETTO_ORG=your-org-subdomain
HERETTO_USER=your-token-login
HERETTO_TOKEN=your-token-password
```

The scripts load this file automatically via `python-dotenv`. You can also export the variables in your shell instead.

---

## Project Structure

```
python/
├── .env.example
├── pyproject.toml
├── requirements.txt
└── src/
    ├── heretto_webdav/
    │   ├── __init__.py
    │   └── client.py          Reusable WebDAV client class
    └── use_cases/
        ├── 01_list_resources.py
        ├── 02_download_resource.py
        ├── 03_upload_resource.py
        ├── 04_delete_resource.py
        ├── 05_create_directory.py
        ├── 06_export_taxonomy.py
        └── 07_sync_directory.py
```

---

## Use Cases

Run each script from the `python/` directory with the virtual environment active.

### 01 — List Resources

Lists the immediate children of the content root using `PROPFIND`.

```bash
python src/use_cases/01_list_resources.py
```

Output shows each item labeled `[DIR]` or `[FILE]` with its full WebDAV path.

---

### 02 — Download a File

Downloads a single file using `GET`. Pass the full WebDAV URL as a positional argument. The file is saved using the remote filename by default; use `-o` to override.

```bash
python src/use_cases/02_download_resource.py <url> [-o output]
```

```bash
python src/use_cases/02_download_resource.py \
    https://pstest.heretto.com/webdav/db/organizations/pstest/taxonomies/taxonomist.xml

python src/use_cases/02_download_resource.py \
    https://pstest.heretto.com/webdav/db/organizations/pstest/taxonomies/taxonomist.xml \
    -o my-taxonomy.xml
```

---

### 03 — Upload a File

Uploads a local file using `PUT`. If the destination already exists it will be overwritten. If the parent directory does not exist the server returns 409 — use use case 05 to create it first.

```bash
python src/use_cases/03_upload_resource.py <local_file> <url>
```

```bash
python src/use_cases/03_upload_resource.py \
    my-topic.dita \
    https://pstest.heretto.com/webdav/db/organizations/pstest/repositories/my-topic.dita
```

Pass `--content-type` to override the default `application/xml`.

---

### 04 — Delete a File

Deletes a single file using `DELETE`. Prompts for confirmation before proceeding. Pass `-y` to skip the prompt (useful in scripts).

```bash
python src/use_cases/04_delete_resource.py <url> [-y]
```

```bash
python src/use_cases/04_delete_resource.py \
    https://pstest.heretto.com/webdav/db/organizations/pstest/repositories/obsolete-topic.dita
```

---

### 05 — Create a Directory

Creates a new directory using `MKCOL`. The parent must already exist — WebDAV does not create intermediate directories automatically.

```bash
python src/use_cases/05_create_directory.py <url>
```

```bash
python src/use_cases/05_create_directory.py \
    https://pstest.heretto.com/webdav/db/organizations/pstest/repositories/new-section/
```

---

### 06 — Export a Taxonomy

Downloads a named SKOS taxonomy file from the `taxonomies/` collection. The file is saved using the taxonomy name by default; use `-o` to override.

```bash
python src/use_cases/06_export_taxonomy.py <taxonomy_name> [-o output]
```

```bash
python src/use_cases/06_export_taxonomy.py taxonomist.xml
python src/use_cases/06_export_taxonomy.py product-taxonomy.xml -o my-taxonomy.xml
```

---

### 07 — Sync a Local Directory

Uploads all files from a local directory to a remote WebDAV path. One-way sync (local → remote) — does not delete remote files that no longer exist locally. Intended for CI/CD pipelines such as deploying an updated schematron rule set.

```bash
python src/use_cases/07_sync_directory.py <local_dir> <url>
```

```bash
python src/use_cases/07_sync_directory.py \
    ./schematron-rules \
    https://pstest.heretto.com/webdav/db/organizations/pstest/schematron/
```

---

## Client Module

The `heretto_webdav.client.HerettoWebDavClient` class provides the core operations. Import it directly to build your own scripts:

```python
from heretto_webdav import HerettoWebDavClient

client = HerettoWebDavClient()  # reads HERETTO_ORG / USER / TOKEN from env

# List a directory
resources = client.list_directory(client.content_path("topics/"), depth=1)

# Download a file
client.download(client.taxonomy_path("product-taxonomy.xml"), "local-copy.xml")

# Upload a file
client.upload("new-rules.sch", client.schematron_path("new-rules.sch"))

# Delete a file
client.delete(client.content_path("topics/obsolete.dita"))
```

All methods raise `requests.HTTPError` on non-2xx responses so errors surface immediately.

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP client for all WebDAV operations |
| `python-dotenv` | Load credentials from `.env` file |
