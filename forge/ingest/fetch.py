"""Download a source once and keep the original in sources/raw/."""

import ssl
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import certifi

from .common import IngestError

USER_AGENT = "re-course-ingest/0.1 (course generator; fetches only pages its author lists)"
TIMEOUT = 60
CONTENT_TYPES = {"text/html": "html", "application/xhtml+xml": "html",
                 "application/pdf": "pdf", "text/markdown": "markdown", "text/plain": "text"}
EXTENSIONS = {".html": "html", ".htm": "html", ".pdf": "pdf", ".md": "markdown",
              ".markdown": "markdown", ".txt": "text"}
SAVED_AS = {"html": ".html", "pdf": ".pdf", "markdown": ".md", "text": ".txt"}


def fetch(url, raw_dir, source_id, refresh=False):
    """Return (path of the saved original, kind). Uses the saved copy unless
    `refresh` is set."""
    saved = sorted(raw_dir.glob(f"{source_id}.*"))
    if saved and not refresh:
        return saved[0], EXTENSIONS[saved[0].suffix]

    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context(cafile=certifi.where())
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
            data = response.read()
            content_type = response.headers.get_content_type()
    except (urllib.error.URLError, TimeoutError) as error:
        raise IngestError(f"could not download {url}: {error}") from None
    kind = CONTENT_TYPES.get(content_type) or EXTENSIONS.get(Path(urlparse(url).path).suffix.lower())
    if kind is None:
        raise IngestError(f"{url}: unsupported content type {content_type}")

    raw_dir.mkdir(parents=True, exist_ok=True)
    for old in saved:
        old.unlink()
    path = raw_dir / f"{source_id}{SAVED_AS[kind]}"
    path.write_bytes(data)
    return path, kind
