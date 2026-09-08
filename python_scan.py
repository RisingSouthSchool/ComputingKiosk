#!/usr/bin/env python3
"""Extract Year 11 Python console submissions and rebuild the Python-projects list."""

import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZIPS_DIR = ROOT / "py_zips"
PROJECTS_DIR = ROOT / "python_projects"
MANIFEST_JSON = ROOT / "pythonProjects.json"

# Fields python_scan.py owns. Anything else in pythonProjects.json was put
# there by hand (student, ...) and is carried across untouched.
MANAGED_FIELDS = {"slug", "title", "entryFile"}


def slug_for(zip_path):
    slug = zip_path.stem.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9_-]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-") or "project"


def safe_extract(zip_path, destination):
    root = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if target != root and root not in target.parents:
                raise ValueError("archive contains an unsafe path")
        archive.extractall(destination)


def _shallowest(paths):
    """Pick the path with the fewest path segments, then shortest name, for
    determinism when more than one file matches a priority rule."""
    return sorted(paths, key=lambda path: (len(path.parts), str(path)))[0]


def find_entry_point(extracted, zip_stem):
    """Return (entry_path, warning). entry_path is None when the submission
    should be skipped; warning explains why in that case."""
    all_py = [path for path in extracted.rglob("*.py") if path.is_file()]
    if not all_py:
        return None, "no .py files found in the archive"

    named_main = [path for path in all_py if path.name.lower() == "main.py"]
    if named_main:
        return _shallowest(named_main), None

    zip_name_slug = re.sub(r"[^a-z0-9]+", "", zip_stem.lower())
    name_matches = [
        path for path in all_py
        if re.sub(r"[^a-z0-9]+", "", path.stem.lower()) == zip_name_slug
    ]
    if name_matches:
        return _shallowest(name_matches), None

    if len(all_py) == 1:
        return all_py[0], None

    names = ", ".join(sorted(path.relative_to(extracted).as_posix() for path in all_py))
    warning = (
        f"multiple .py files ({names}) and none is named main.py or matches "
        f"the zip name \"{zip_stem}\" -- skipping rather than guessing"
    )
    return None, warning


def title_from_slug(slug):
    return " ".join(word.capitalize() for word in slug.replace("_", "-").split("-"))


def process_zip(zip_path, notes):
    slug = slug_for(zip_path)
    project_dir = PROJECTS_DIR / slug
    if project_dir.is_dir() and (project_dir / ".entry").is_file():
        return False, None

    with tempfile.TemporaryDirectory(prefix="pyproj-extract-") as temp_name:
        extracted = Path(temp_name)
        try:
            safe_extract(zip_path, extracted)
        except (OSError, zipfile.BadZipFile, ValueError) as error:
            return False, f"could not extract archive ({error})"

        entry_path, warning = find_entry_point(extracted, zip_path.stem)
        if entry_path is None:
            notes.append(f"  {zip_path.name}: {warning}")
            return False, warning

        staging = Path(tempfile.mkdtemp(prefix="pyproj-normalized-", dir=PROJECTS_DIR))
        try:
            for item in extracted.iterdir():
                destination = staging / item.name
                if item.is_dir():
                    shutil.copytree(item, destination, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, destination)
            relative_entry = entry_path.relative_to(extracted).as_posix()
            (staging / ".entry").write_text(relative_entry, encoding="utf-8")
            if project_dir.exists():
                shutil.rmtree(project_dir)
            staging.rename(project_dir)
            staging = None
        finally:
            if staging is not None and staging.exists():
                shutil.rmtree(staging)
    return True, None


def load_manual_fields():
    """Read hand-edited fields out of the existing manifest, keyed by slug."""
    if not MANIFEST_JSON.is_file():
        return {}
    try:
        existing = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(existing, list):
        return {}
    manual = {}
    for entry in existing:
        if isinstance(entry, dict) and isinstance(entry.get("slug"), str):
            manual[entry["slug"]] = {
                key: value for key, value in entry.items() if key not in MANAGED_FIELDS
            }
    return manual


def rebuild_manifest():
    manual = load_manual_fields()
    projects = []
    for project_dir in sorted((path for path in PROJECTS_DIR.iterdir() if path.is_dir()), key=lambda p: p.name):
        entry_marker = project_dir / ".entry"
        if not entry_marker.is_file():
            continue
        entry_file = entry_marker.read_text(encoding="utf-8").strip()
        if not entry_file or not (project_dir / entry_file).is_file():
            continue
        slug = project_dir.name
        entry = {
            "slug": slug,
            "title": title_from_slug(slug),
            "entryFile": entry_file,
        }
        carried = manual.get(slug, {})
        entry["student"] = carried.pop("student", "")
        entry["blurb"] = carried.pop("blurb", "")
        entry.update(carried)
        projects.append(entry)
    MANIFEST_JSON.write_text(json.dumps(projects, indent=2) + "\n", encoding="utf-8")
    return projects


def main():
    ZIPS_DIR.mkdir(exist_ok=True)
    PROJECTS_DIR.mkdir(exist_ok=True)
    added = []
    skipped = 0
    notes = []
    for zip_path in sorted(ZIPS_DIR.glob("*.zip"), key=lambda p: p.name.lower()):
        was_added, error = process_zip(zip_path, notes)
        if error:
            skipped += 1
            print(f"Skipped {zip_path.name}: {error}")
        elif was_added:
            added.append(zip_path)

    projects = rebuild_manifest()
    for zip_path in added:
        slug = slug_for(zip_path)
        entry_file = (PROJECTS_DIR / slug / ".entry").read_text(encoding="utf-8").strip()
        print(f"Added: {title_from_slug(slug)} (entry point: {entry_file}).")
    print(f"Summary: Added {len(added)}. Skipped: {skipped}. Total working projects: {len(projects)}.")


if __name__ == "__main__":
    main()
