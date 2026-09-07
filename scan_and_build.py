#!/usr/bin/env python3
"""Extract MicroStudio HTML5 exports and rebuild the hub game list."""

import html.parser
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZIPS_DIR = ROOT / "zips"
GAMES_DIR = ROOT / "games"
GAMES_JSON = ROOT / "games.json"


class TitleParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data)


def slug_for(zip_path):
    slug = zip_path.stem.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9_-]+", "-", slug)
    return re.sub(r"-+", "-", slug).strip("-") or "game"


def safe_extract(zip_path, destination):
    root = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if target != root and root not in target.parents:
                raise ValueError("archive contains an unsafe path")
        archive.extractall(destination)


def find_index(extracted):
    candidates = [path for path in extracted.rglob("index.html") if path.is_file()]
    candidates.sort(key=lambda path: (len(path.relative_to(extracted).parts), str(path)))
    return candidates[0] if candidates else None


def copy_normalized(source, target):
    target.mkdir(parents=True, exist_ok=True)
    for item in source.iterdir():
        destination = target / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)


def validate_game(game_dir):
    if not (game_dir / "index.html").is_file():
        return "no index.html found after extraction"
    if not any(game_dir.rglob("*.js")):
        return "no .js engine file found after extraction"
    return None


def title_from_index(index_path, fallback):
    parser = TitleParser()
    parser.feed(index_path.read_text(encoding="utf-8", errors="replace"))
    title = " ".join("".join(parser.parts).split())
    return title or fallback


def process_zip(zip_path):
    slug = slug_for(zip_path)
    game_dir = GAMES_DIR / slug
    if game_dir.is_dir() and validate_game(game_dir) is None:
        return False, None

    with tempfile.TemporaryDirectory(prefix="game-extract-") as temp_name:
        extracted = Path(temp_name)
        try:
            safe_extract(zip_path, extracted)
        except (OSError, zipfile.BadZipFile, ValueError) as error:
            return False, f"could not extract archive ({error})"

        index_path = find_index(extracted)
        if index_path is None:
            return False, "no index.html found after extraction"

        staging = Path(tempfile.mkdtemp(prefix="game-normalized-", dir=GAMES_DIR))
        try:
            copy_normalized(index_path.parent, staging)
            error = validate_game(staging)
            if error:
                return False, error
            if game_dir.exists():
                shutil.rmtree(game_dir)
            staging.rename(game_dir)
            staging = None
        finally:
            if staging is not None and staging.exists():
                shutil.rmtree(staging)
    return True, None


def rebuild_games_json():
    games = []
    for game_dir in sorted((path for path in GAMES_DIR.iterdir() if path.is_dir()), key=lambda p: p.name):
        if validate_game(game_dir) is not None:
            continue
        games.append({
            "slug": game_dir.name,
            "title": title_from_index(game_dir / "index.html", game_dir.name.replace("-", " ").title()),
            "hasIcon": (game_dir / "icon192.png").is_file(),
        })
    GAMES_JSON.write_text(json.dumps(games, indent=2) + "\n", encoding="utf-8")
    return games


def main():
    ZIPS_DIR.mkdir(exist_ok=True)
    GAMES_DIR.mkdir(exist_ok=True)
    added = []
    skipped = 0
    for zip_path in sorted(ZIPS_DIR.glob("*.zip"), key=lambda p: p.name.lower()):
        was_added, error = process_zip(zip_path)
        if error:
            skipped += 1
            print(f"Skipped {zip_path.name}: {error}")
        elif was_added:
            added.append(zip_path)

    games = rebuild_games_json()
    for zip_path in added:
        title = title_from_index(GAMES_DIR / slug_for(zip_path) / "index.html", slug_for(zip_path))
        print(f"Added: {title}.")
    print(f"Summary: Added {len(added)}. Skipped: {skipped}. Total working games: {len(games)}.")


if __name__ == "__main__":
    main()