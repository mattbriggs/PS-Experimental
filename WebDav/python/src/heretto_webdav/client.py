"""
Thin wrapper around the Heretto CCMS WebDAV interface.

All methods raise requests.HTTPError on non-2xx responses.
Auth is HTTP Basic: username = token login, password = token value.
"""

import os
from pathlib import Path
from xml.etree import ElementTree

import requests
from dotenv import load_dotenv

load_dotenv()


class HerettoWebDavClient:
    def __init__(
        self,
        org: str | None = None,
        user: str | None = None,
        token: str | None = None,
    ):
        self.org = org or os.environ["HERETTO_ORG"]
        self.user = user or os.environ["HERETTO_USER"]
        self.token = token or os.environ["HERETTO_TOKEN"]
        self.base_url = f"https://{self.org}.heretto.com/webdav"
        self._auth = (self.user, self.token)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _org_path(self, relative: str) -> str:
        """Resolve a path relative to the organization root."""
        return f"/db/organizations/{self.org}/{relative.lstrip('/')}"

    # -------------------------------------------------------------------------
    # Directory operations
    # -------------------------------------------------------------------------

    def list_directory(self, path: str, depth: int = 1) -> list[dict]:
        """
        Return the immediate children of a WebDAV collection.

        depth=0  — properties of the resource itself only
        depth=1  — resource and its immediate children (default)
        """
        url = self._url(path)
        headers = {"Depth": str(depth), "Content-Type": "application/xml"}
        response = requests.request("PROPFIND", url, auth=self._auth, headers=headers)
        response.raise_for_status()

        ns = {"d": "DAV:"}
        tree = ElementTree.fromstring(response.content)
        resources = []
        for resp in tree.findall("d:response", ns):
            href = resp.find("d:href", ns).text
            is_collection = resp.find(".//d:collection", ns) is not None
            resources.append(
                {
                    "href": href,
                    "type": "directory" if is_collection else "file",
                }
            )
        return resources

    def create_directory(self, path: str) -> None:
        """Create a WebDAV collection (directory)."""
        response = requests.request("MKCOL", self._url(path), auth=self._auth)
        if response.status_code not in (200, 201):
            response.raise_for_status()

    # -------------------------------------------------------------------------
    # File operations
    # -------------------------------------------------------------------------

    def download(self, remote_path: str, local_path: str | Path) -> Path:
        """Download a remote file to a local path. Returns the local path."""
        response = requests.get(self._url(remote_path), auth=self._auth, stream=True)
        response.raise_for_status()
        dest = Path(local_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest

    def upload(
        self,
        local_path: str | Path,
        remote_path: str,
        content_type: str = "application/xml",
    ) -> None:
        """Upload a local file to a remote WebDAV path."""
        with open(local_path, "rb") as f:
            response = requests.put(
                self._url(remote_path),
                auth=self._auth,
                headers={"Content-Type": content_type},
                data=f,
            )
        if response.status_code not in (200, 201, 204):
            response.raise_for_status()

    def delete(self, remote_path: str) -> None:
        """Delete a file or directory at the given WebDAV path."""
        response = requests.delete(self._url(remote_path), auth=self._auth)
        if response.status_code not in (200, 204):
            response.raise_for_status()

    # -------------------------------------------------------------------------
    # Convenience path builders
    # -------------------------------------------------------------------------

    def content_path(self, relative: str) -> str:
        return self._org_path(f"content/{relative.lstrip('/')}")

    def repositories_path(self, relative: str = "") -> str:
        return self._org_path(f"repositories/{relative.lstrip('/')}")

    def path_from_url(self, url: str) -> str:
        """Strip the base URL prefix from a full WebDAV URL, returning the path."""
        if not url.startswith(self.base_url):
            raise ValueError(f"URL must start with {self.base_url}")
        return url[len(self.base_url):]

    def taxonomy_path(self, name: str) -> str:
        return self._org_path(f"taxonomies/{name}")

    def schematron_path(self, name: str) -> str:
        return self._org_path(f"schematron/{name}")
