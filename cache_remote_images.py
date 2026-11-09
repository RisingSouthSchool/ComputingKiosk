#!/usr/bin/env python3
"""Download the remote photos the web apps use so they work with no internet.

Looks through webapps/<slug>/index.html for remote image URLs (in src="...",
image: "..." and url(...)), saves each one to webapps/<slug>/images/, and
rewrites the HTML to point at the local copy. Anything that turns out not to be
an image is left alone. Safe to run every launch: with nothing left to cache it
does nothing, and with no internet it gives up quickly and leaves the apps alone
(they show a plain placeholder tile instead of a broken image).
"""

import hashlib
import html
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEBAPPS_DIR = ROOT / "webapps"

TIMEOUT_SECONDS = 8
MAX_BYTES = 8 * 1024 * 1024
USER_AGENT = "Mozilla/5.0 (ComputingKiosk image cache)"
EXTENSIONS = {
    "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
    "image/gif": ".gif", "image/svg+xml": ".svg", "image/avif": ".avif",
}


class Offline(Exception):
    """The network is unreachable; stop trying."""


# A remote URL used the way an image is: src="...", image: "..." or url(...).
URL_PATTERN = re.compile(r"""(?:\bsrc\s*=\s*|\bimage\s*:\s*|url\()\s*["']?(https?://[^"'\s)<>\\]+)""")


def find_urls(text):
    return sorted(set(URL_PATTERN.findall(text)))


def fetch(url):
    request = urllib.request.Request(html.unescape(url), headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            content_type = response.headers.get_content_type()
            data = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as error:
        raise ValueError(f"HTTP {error.code}") from error
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise Offline(str(getattr(error, "reason", error))) from error
    if len(data) > MAX_BYTES:
        raise ValueError("file is too large")
    return data, content_type


def local_name(url, content_type):
    extension = EXTENSIONS.get(content_type)
    if extension is None:
        raise ValueError(f"not an image ({content_type})")
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12] + extension


def cache_app(app_dir, fetcher=fetch):
    """Cache one app's remote images. Returns (saved, failed) counts."""
    index_path = app_dir / "index.html"
    text = index_path.read_text(encoding="utf-8")
    urls = find_urls(text)
    if not urls:
        return 0, 0

    images_dir = app_dir / "images"
    replacements = {}
    failed = 0
    for url in urls:
        try:
            data, content_type = fetcher(url)
            name = local_name(url, content_type)
        except Offline:
            raise
        except ValueError as error:
            failed += 1
            print(f"  {app_dir.name}: could not cache {url[:70]} ({error})")
            continue
        images_dir.mkdir(exist_ok=True)
        (images_dir / name).write_bytes(data)
        replacements[url] = f"images/{name}"

    # Longest first so a URL that is a prefix of another is never half-replaced.
    for url in sorted(replacements, key=len, reverse=True):
        text = text.replace(url, replacements[url])
    if replacements:
        index_path.write_text(text, encoding="utf-8")
    return len(replacements), failed


def main():
    if not WEBAPPS_DIR.is_dir():
        return
    pending = [d for d in sorted(WEBAPPS_DIR.iterdir())
               if (d / "index.html").is_file()
               and find_urls((d / "index.html").read_text(encoding="utf-8"))]
    if not pending:
        print("All web app images are already saved locally.")
        return

    saved = failed = 0
    for app_dir in pending:
        try:
            app_saved, app_failed = cache_app(app_dir)
        except Offline as error:
            print(f"No internet ({error}), so web app photos were not downloaded. "
                  "Run start.command once while online and they will be saved for good.")
            break
        saved += app_saved
        failed += app_failed
        print(f"  {app_dir.name}: saved {app_saved} image(s).")
    if saved or failed:
        print(f"Summary: saved {saved}, could not save {failed}.")


if __name__ == "__main__":
    main()
