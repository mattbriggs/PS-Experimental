# Accessing Heretto CCMS Resources Programmatically via WebDAV

## Concept

Heretto CCMS exposes its file system through the Web Distributed Authoring and Versioning (WebDAV) protocol. While commonly associated with oXygen XML Editor, WebDAV is a standard HTTP extension that any HTTP client can use to interact with CCMS resources programmatically.

This means you can use tools like **cURL**, **Python**, **Postman**, or custom scripts to:

- List directories and resources in the CCMS
- Download DITA topics, maps, images, and other assets
- Upload new or modified files
- Delete resources
- Create directories (collections)
- Access schematron rules, taxonomies, and configuration files

### WebDAV Base URL

```
https://{organizationId}.heretto.com/webdav/
```

Where `{organizationId}` is the subdomain you use to access Heretto CCMS (e.g., `thunderbird`).

### Key Resource Paths

| Path | Contents |
|------|----------|
| `/webdav/db/organizations/{org}/` | Organization root |
| `/webdav/db/organizations/{org}/content/` | DITA content (topics, maps, images) |
| `/webdav/db/organizations/{org}/taxonomies/` | SKOS taxonomy files |
| `/webdav/db/organizations/{org}/schematron/` | Schematron validation rules |

---

## Prerequisites

### Generate an API Token

You must generate a token to authenticate WebDAV requests. This is **required** if your organization uses SSO, and **strongly recommended** in all cases.

1. Sign in to Heretto CCMS.
2. Navigate to:
   ```
   https://{organizationId}.heretto.com/tools/token-management/tokens.xql
   ```
3. Enter a meaningful **Token name** (e.g., `CI/CD Pipeline`, `Publishing Script`, `WebDAV Automation`).
4. Click **Create token**.
5. Copy the **login** and **password** (token) immediately.

> ⚠️ **Important:** Once you navigate away, you cannot retrieve the token again. Store it securely (e.g., in a secrets manager or environment variable).

### Set Up Environment Variables

For all examples below, configure these variables:

```bash
# Bash / Shell
export HERETTO_ORG="thunderbird"
export HERETTO_BASE="https://${HERETTO_ORG}.heretto.com/webdav"
export HERETTO_USER="your.email@company.com"
export HERETTO_TOKEN="your-generated-token"
```

```python
# Python
import os

HERETTO_ORG = os.environ.get("HERETTO_ORG", "thunderbird")
HERETTO_BASE = f"https://{HERETTO_ORG}.heretto.com/webdav"
HERETTO_USER = os.environ.get("HERETTO_USER")
HERETTO_TOKEN = os.environ.get("HERETTO_TOKEN")
```

---

## Task: List Resources in a Directory

Use the WebDAV `PROPFIND` method to list the contents of a directory.

### cURL

```bash
# List contents of the organization root
curl -X PROPFIND \
  -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  -H "Depth: 1" \
  -H "Content-Type: application/xml" \
  "${HERETTO_BASE}/db/organizations/${HERETTO_ORG}/"
```

The `Depth` header controls recursion:
- `Depth: 0` — Properties of the resource itself only
- `Depth: 1` — The resource and its immediate children
- `Depth: infinity` — Full recursive listing (use with caution)

### Python

```python
import requests
from xml.etree import ElementTree

def list_resources(path, depth=1):
    """List resources at a given WebDAV path."""
    url = f"{HERETTO_BASE}{path}"
    headers = {
        "Depth": str(depth),
        "Content-Type": "application/xml"
    }
    response = requests.request(
        "PROPFIND",
        url,
        auth=(HERETTO_USER, HERETTO_TOKEN),
        headers=headers
    )
    response.raise_for_status()

    # Parse the multistatus XML response
    ns = {"d": "DAV:"}
    tree = ElementTree.fromstring(response.content)
    resources = []
    for resp in tree.findall("d:response", ns):
        href = resp.find("d:href", ns).text
        is_collection = resp.find(".//d:collection", ns) is not None
        resources.append({
            "href": href,
            "type": "directory" if is_collection else "file"
        })
    return resources

# Example: List content directory
resources = list_resources(f"/db/organizations/{HERETTO_ORG}/content/")
for r in resources:
    print(f"[{r['type']}] {r['href']}")
```

---

## Task: Download a Resource

Use a standard HTTP `GET` request to download any file from the CCMS.

### cURL

```bash
# Download a specific DITA topic
curl -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  -o "my-topic.dita" \
  "${HERETTO_BASE}/db/organizations/${HERETTO_ORG}/content/topics/my-topic.dita"

# Download a taxonomy file
curl -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  -o "taxonomy.xml" \
  "${HERETTO_BASE}/db/organizations/${HERETTO_ORG}/taxonomies/my-taxonomy.xml"

# Download a schematron file
curl -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  -o "rules.sch" \
  "${HERETTO_BASE}/db/organizations/${HERETTO_ORG}/schematron/custom-rules.sch"
```

### Python

```python
def download_resource(path, local_filename):
    """Download a resource from WebDAV to a local file."""
    url = f"{HERETTO_BASE}{path}"
    response = requests.get(
        url,
        auth=(HERETTO_USER, HERETTO_TOKEN),
        stream=True
    )
    response.raise_for_status()

    with open(local_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"Downloaded: {local_filename} ({response.headers.get('Content-Length', 'unknown')} bytes)")

# Example: Download a DITA topic
download_resource(
    f"/db/organizations/{HERETTO_ORG}/content/topics/my-topic.dita",
    "my-topic.dita"
)
```

---

## Task: Upload a Resource

Use HTTP `PUT` to upload or overwrite a file on the CCMS.

### cURL

```bash
# Upload a schematron file
curl -X PUT \
  -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  -H "Content-Type: application/xml" \
  --data-binary @custom-rules.sch \
  "${HERETTO_BASE}/db/organizations/${HERETTO_ORG}/schematron/custom-rules.sch"

# Upload a DITA topic
curl -X PUT \
  -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  -H "Content-Type: application/xml" \
  --data-binary @my-topic.dita \
  "${HERETTO_BASE}/db/organizations/${HERETTO_ORG}/content/topics/my-topic.dita"
```

### Python

```python
def upload_resource(local_filename, remote_path, content_type="application/xml"):
    """Upload a local file to a WebDAV path."""
    url = f"{HERETTO_BASE}{remote_path}"

    with open(local_filename, "rb") as f:
        response = requests.put(
            url,
            auth=(HERETTO_USER, HERETTO_TOKEN),
            headers={"Content-Type": content_type},
            data=f
        )

    if response.status_code in (200, 201, 204):
        print(f"Uploaded: {local_filename} -> {remote_path}")
    else:
        response.raise_for_status()

# Example: Upload a schematron file
upload_resource(
    "custom-rules.sch",
    f"/db/organizations/{HERETTO_ORG}/schematron/custom-rules.sch"
)
```

---

## Task: Delete a Resource

Use HTTP `DELETE` to remove a file from the CCMS.

### cURL

```bash
curl -X DELETE \
  -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  "${HERETTO_BASE}/db/organizations/${HERETTO_ORG}/content/topics/obsolete-topic.dita"
```

### Python

```python
def delete_resource(remote_path):
    """Delete a resource at the given WebDAV path."""
    url = f"{HERETTO_BASE}{remote_path}"
    response = requests.delete(
        url,
        auth=(HERETTO_USER, HERETTO_TOKEN)
    )
    if response.status_code in (200, 204):
        print(f"Deleted: {remote_path}")
    else:
        response.raise_for_status()

# Example
delete_resource(f"/db/organizations/{HERETTO_ORG}/content/topics/obsolete-topic.dita")
```

---

## Task: Create a Directory (Collection)

Use the WebDAV `MKCOL` method to create a new directory.

### cURL

```bash
curl -X MKCOL \
  -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  "${HERETTO_BASE}/db/organizations/${HERETTO_ORG}/content/topics/new-folder/"
```

### Python

```python
def create_directory(remote_path):
    """Create a new WebDAV collection (directory)."""
    url = f"{HERETTO_BASE}{remote_path}"
    response = requests.request(
        "MKCOL",
        url,
        auth=(HERETTO_USER, HERETTO_TOKEN)
    )
    if response.status_code in (200, 201):
        print(f"Created directory: {remote_path}")
    else:
        response.raise_for_status()

# Example
create_directory(f"/db/organizations/{HERETTO_ORG}/content/topics/new-folder/")
```

---

## Use Case: CI/CD Pipeline Integration

A common use case is integrating WebDAV into a CI/CD pipeline to automate content deployment.

### Example: Upload Modified DITA-OT Package

```python
import glob

def sync_directory(local_dir, remote_base_path):
    """Upload all files from a local directory to WebDAV."""
    for filepath in glob.glob(f"{local_dir}/**/*", recursive=True):
        if os.path.isfile(filepath):
            relative = os.path.relpath(filepath, local_dir)
            remote_path = f"{remote_base_path}/{relative}"

            # Determine content type
            if filepath.endswith((".dita", ".ditamap", ".xml", ".sch")):
                content_type = "application/xml"
            elif filepath.endswith(".json"):
                content_type = "application/json"
            else:
                content_type = "application/octet-stream"

            upload_resource(filepath, remote_path, content_type)

# Sync a local DITA-OT plugin to the CCMS
sync_directory(
    "./my-dita-ot-plugin",
    f"/db/organizations/{HERETTO_ORG}/dita-ot-plugins/my-plugin"
)
```

### Example: Backup Schematron Rules Before Updating

```bash
#!/bin/bash
# backup-and-update-schematron.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCHEMATRON_PATH="/db/organizations/${HERETTO_ORG}/schematron"

# Download current version as backup
curl -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  -o "backup_${TIMESTAMP}_rules.sch" \
  "${HERETTO_BASE}${SCHEMATRON_PATH}/custom-rules.sch"

# Upload new version
curl -X PUT \
  -u "${HERETTO_USER}:${HERETTO_TOKEN}" \
  -H "Content-Type: application/xml" \
  --data-binary @custom-rules.sch \
  "${HERETTO_BASE}${SCHEMATRON_PATH}/custom-rules.sch"

echo "Backup saved as backup_${TIMESTAMP}_rules.sch"
echo "New schematron deployed."
```

---

## Use Case: Export Taxonomy Programmatically

```python
def export_taxonomy(taxonomy_name, output_file):
    """Download a SKOS taxonomy file from Heretto."""
    path = f"/db/organizations/{HERETTO_ORG}/taxonomies/{taxonomy_name}.xml"
    download_resource(path, output_file)

# Export the full taxonomy as SKOS XML
export_taxonomy("product-taxonomy", "product-taxonomy-export.xml")
```

---

## Token Management

### Invalidate a Token

When a token is no longer needed (e.g., a script is retired or credentials are rotated):

1. Navigate to:
   ```
   https://{organizationId}.heretto.com/tools/token-management/tokens.xql
   ```
2. Click **Invalidate** next to the token.

All requests using that token will immediately fail.

### Best Practices

| Practice | Rationale |
|----------|-----------|
| One token per application/script | Revoke individually without breaking other integrations |
| Store tokens in environment variables or secrets managers | Never hardcode in source |
| Rotate tokens periodically | Limit exposure window |
| Name tokens descriptively | `CI/CD Pipeline`, `Schematron Sync`, `Taxonomy Export` |

---

## Security Considerations

> ⚠️ **Important:** WebDAV provides access to the entire CCMS file system, not just content files. Exercise caution:

- **Scope your scripts** to only the paths they need
- **Never traverse** directories outside your intended scope
- **Avoid recursive deletes** without explicit safeguards
- **Log all operations** for audit purposes
- **Use read-only tokens** where possible (if supported by your environment)

---

## Troubleshooting

| Symptom | Cause | Resolution |
|---------|-------|------------|
| `401 Unauthorized` | Invalid or expired token | Regenerate token at `/tools/token-management/tokens.xql` |
| `403 Forbidden` | Insufficient permissions | Verify your CCMS role has access to the target path |
| `404 Not Found` | Incorrect path or resource doesn't exist | Verify path with a `PROPFIND` on the parent directory |
| `405 Method Not Allowed` | WebDAV not enabled for environment | Contact Heretto support to verify WebDAV is active |
| `409 Conflict` (on PUT) | Parent directory doesn't exist | Create parent with `MKCOL` first |

---

## Reference

- **Token Management:** `https://{org}.heretto.com/tools/token-management/tokens.xql`
- **WebDAV Base URL:** `https://{org}.heretto.com/webdav/`
- **WebDAV Protocol Spec:** [RFC 4918](https://www.rfc-editor.org/rfc/rfc4918)
- **Python WebDAV Library (alternative):** [webdavclient3](https://pypi.org/project/webdavclient3/) — provides higher-level abstractions if preferred over raw `requests`

---

## Sources

- [Connect Heretto CCMS and Oxygen through WebDAV](https://help.heretto.com/user-guide/integrate/oxygen-integration) — Original documentation (token generation, WebDAV URL structure)
- [WebDAV Deprecation Discussion](https://jorsek.atlassian.net/wiki/spaces/PM/pages/1538097171/WebDAV+Deprecation) — Internal notes on access scope and security concerns
