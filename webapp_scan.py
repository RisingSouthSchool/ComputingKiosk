#!/usr/bin/env python3
"""Rebuild webapps.json from the single-page web apps in webapps/.

Each app lives in webapps/<slug>/index.html (plus any files it needs). To add
one, make a new folder there and drop the app's index.html in it. New apps are
featured by default; set "featured" to false in webapps.json to opt one out.
"""

import json
import re
import sys
from pathlib import Path

import scan_and_build

ROOT = Path(__file__).resolve().parent
WEBAPPS_DIR = ROOT / "webapps"
WEBAPPS_JSON = ROOT / "webapps.json"

# Fields this script owns on every run. Anything else (title, student, blurb,
# featured, ...) was put there by hand or on first scan and is carried across.
MANAGED_FIELDS = {"slug", "hasIcon", "iconSource", "iconFile"}


def derive_title(index_path, fallback):
    """Page <title>, trimmed to the part before a ' | ' tagline."""
    title = scan_and_build.title_from_index(index_path, fallback)
    return re.split(r"\s+\|\s+", title)[0].strip() or fallback


def load_existing():
    if not WEBAPPS_JSON.is_file():
        return {}
    try:
        existing = json.loads(WEBAPPS_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(existing, list):
        return {}
    return {entry["slug"]: entry for entry in existing
            if isinstance(entry, dict) and isinstance(entry.get("slug"), str)}


def main():
    force_icons = "--force-icons" in sys.argv[1:]
    WEBAPPS_DIR.mkdir(exist_ok=True)
    existing = load_existing()
    defaults = scan_and_build.default_icon_hashes()
    notes = []
    apps = []
    new_slugs = []
    for app_dir in sorted((p for p in WEBAPPS_DIR.iterdir() if p.is_dir()), key=lambda p: p.name):
        index_path = app_dir / "index.html"
        if not index_path.is_file():
            print(f"Skipped {app_dir.name}: no index.html")
            continue
        slug = app_dir.name
        carried = {k: v for k, v in existing.get(slug, {}).items() if k not in MANAGED_FIELDS}
        is_new = slug not in existing
        if is_new:
            new_slugs.append(slug)

        title = carried.pop("title", None) or derive_title(index_path, slug.replace("-", " ").title())
        # Apostrophes would split "What's" into "What" + "s" for the initials.
        icon_title = title.replace("'", "").replace("’", "")
        icon_source, icon_file = scan_and_build.resolve_icon(
            app_dir, slug, icon_title, defaults, notes, force_icons)

        entry = {
            "slug": slug,
            "title": title,
            "hasIcon": (app_dir / "icon192.png").is_file(),
            "iconSource": icon_source,
            "iconFile": icon_file,
        }
        entry["blurb"] = carried.pop("blurb", "")
        entry["featured"] = carried.pop("featured", True)
        entry.update(carried)
        apps.append(entry)

    WEBAPPS_JSON.write_text(json.dumps(apps, indent=2) + "\n", encoding="utf-8")
    for slug in new_slugs:
        print(f"Added web app: {slug}.")
    for note in notes:
        print(note)
    print(f"Summary: Added {len(new_slugs)}. Total web apps: {len(apps)}.")


if __name__ == "__main__":
    main()
