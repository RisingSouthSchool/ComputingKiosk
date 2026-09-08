#!/usr/bin/env python3
"""Extract MicroStudio HTML5 exports and rebuild the hub game list."""

import hashlib
import html.parser
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import pngkit

ROOT = Path(__file__).resolve().parent
ZIPS_DIR = ROOT / "zips"
GAMES_DIR = ROOT / "games"
GAMES_JSON = ROOT / "games.json"
DEFAULT_ICONS_DIR = ROOT / "default_icons"

ICON_SIZE = 192
GENERATED_ICON = "generated_icon.png"
PLACEHOLDER_ICON = "placeholder_icon.png"

# MicroStudio ships this gamepad artwork with every new project, at every size.
# Students who never draw their own icon export these bytes unchanged, so we
# match on content rather than filename: a genuinely plain custom icon is still
# a custom icon. Extra defaults can be dropped into default_icons/ at any time.
STOCK_DEFAULT_ICON_HASHES = (
    "933f1885a30cd07b5537b2be1c35cf2e1be7f4163fbad177d88f339e4280a617",  # icon16
    "47fc6926867731592dc0c354b42595e4e5e8c3341d82d222f3be14ace18e9fd3",  # icon32
    "63407c8c678c14fd35db8196802806f2e4ba3181100ce0578cba1562c6fa16a4",  # icon64
    "7f20fa97bec25b9bb1efdd93c798c5941e569fe5ab0f9a8e62296a0270cfa06a",  # icon180
    "2a540baeea6d7214e2459ea346c4ccb9acaec7afec482b0a46f73c9771a1ce00",  # icon192
    "ab9b4ee094d6df8c74589c0625fabde959a9d99b04cac0480467591a9fcd6ba0",  # icon512
    "f4d3efb2d3664347ab757f130dc2e3c4230324ea9d00b81e552f7aff5686c863",  # icon1024
    "18d18f6e7b48aae6b87a752ccb030b11447705dda603c0006d4c028e8ec0424e",  # sprites/icon
)

# Filename hints, most telling first. A sprite called "player" is a far better
# tile than whatever happens to be the biggest file in the folder.
NAME_HINTS = ("player", "hero", "title", "icon", "main", "character")

# Scenery and UI chrome. Still usable, but only once nothing better is left:
# a tiling grass texture makes a dull, unreadable icon.
SCENERY_HINTS = (
    "background", "bg", "floor", "wall", "tile", "grass", "sand",
    "water", "sky", "ground", "btn", "button",
)

# MicroStudio's own generated icon set, which is derived from sprites/icon.png
# and so never tells us anything new.
EXPORT_ICON_NAMES = {f"icon{size}.png" for size in (16, 32, 64, 180, 192, 512, 1024)}

# Fields scan_and_build.py owns. Anything else in games.json was put there by
# hand (blurb, featured, student, ...) and is carried across untouched.
MANAGED_FIELDS = {"slug", "title", "hasIcon", "iconSource", "iconFile"}


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


def default_icon_hashes():
    """Known-default icon hashes: the built-in list plus any local additions."""
    hashes = set(STOCK_DEFAULT_ICON_HASHES)
    if DEFAULT_ICONS_DIR.is_dir():
        for path in sorted(DEFAULT_ICONS_DIR.iterdir()):
            if path.is_file() and not path.name.startswith("."):
                hashes.add(pngkit.file_hash(path))
    return hashes


def candidate_sprites(game_dir, defaults):
    """Rank the game's own images by how well each would work as a tile icon.

    Returns (candidates, unreadable) where candidates are (rank, -pixels, name,
    path, width, height) tuples, best first.
    """
    candidates = []
    unreadable = []
    for path in sorted(game_dir.rglob("*")):
        if not path.is_file():
            continue
        name = path.name.lower()
        if name in (GENERATED_ICON, PLACEHOLDER_ICON):
            continue  # never feed our own output back in
        if path.parent == game_dir and name in EXPORT_ICON_NAMES:
            continue  # derived from sprites/icon.png, tells us nothing new
        data = path.read_bytes()
        kind = pngkit.sniff(data)
        if kind is None:
            continue  # not an image at all
        if kind != "png":
            unreadable.append((path.relative_to(game_dir).as_posix(), kind))
            continue
        if hashlib.sha256(data).hexdigest() in defaults:
            continue  # this is the stock icon wearing a different filename
        try:
            width, height = pngkit.read_header(data)
        except pngkit.UnsupportedImage:
            unreadable.append((path.relative_to(game_dir).as_posix(), "damaged"))
            continue
        if width < 8 or height < 8:
            continue  # too small to survive being blown up to 192px
        stem = path.stem.lower()
        rank = len(NAME_HINTS) + 1
        for index, hint in enumerate(NAME_HINTS):
            if hint in stem:
                rank = index
                break
        if rank > len(NAME_HINTS) and any(hint in stem for hint in SCENERY_HINTS):
            rank += 1  # scenery and buttons sink below ordinary sprites
        candidates.append((rank, -(width * height), path.name, path, width, height))
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    return candidates, unreadable


def build_generated_icon(game_dir, defaults):
    """Render an icon from the game's best sprite. Returns (filename, reason)."""
    candidates, unreadable = candidate_sprites(game_dir, defaults)
    for rank, negative_pixels, _, path, width, height in candidates:
        try:
            source_width, source_height, pixels = pngkit.decode(path.read_bytes())
        except (pngkit.UnsupportedImage, OSError):
            unreadable.append((path.relative_to(game_dir).as_posix(), "damaged"))
            continue
        background = pngkit.dominant_background(pixels, source_width, source_height)
        square = pngkit.fit_square(pixels, source_width, source_height, ICON_SIZE, background)
        (game_dir / GENERATED_ICON).write_bytes(pngkit.encode(ICON_SIZE, ICON_SIZE, square))
        if rank < len(NAME_HINTS):
            reason = f"filename matches \"{NAME_HINTS[rank]}\""
        else:
            reason = f"largest usable image ({width}x{height} = {-negative_pixels:,}px)"
        return path.relative_to(game_dir).as_posix(), reason, unreadable
    return None, None, unreadable


def build_placeholder_icon(game_dir, slug, title):
    """Deterministic coloured disc with the game's initials, from the slug."""
    seed = int(hashlib.sha256(slug.encode("utf-8")).hexdigest()[:8], 16)
    # Spread hues around the wheel but keep them dark enough for white text.
    hue = seed % 360
    background = _hue_to_rgb(hue, 0.55, 0.30)
    foreground = (245, 247, 250)
    words = [word for word in re.split(r"[^A-Za-z0-9]+", title or slug) if word]
    initials = "".join(word[0] for word in words[:2]) or (title or slug or "?")[:2]
    pixels = pngkit.placeholder(ICON_SIZE, initials, background, foreground)
    (game_dir / PLACEHOLDER_ICON).write_bytes(pngkit.encode(ICON_SIZE, ICON_SIZE, pixels))
    return initials.upper()[:2]


def _hue_to_rgb(hue, saturation, lightness):
    chroma = (1 - abs(2 * lightness - 1)) * saturation
    secondary = chroma * (1 - abs((hue / 60) % 2 - 1))
    match = lightness - chroma / 2
    table = [(chroma, secondary, 0), (secondary, chroma, 0), (0, chroma, secondary),
             (0, secondary, chroma), (secondary, 0, chroma), (chroma, 0, secondary)]
    red, green, blue = table[int(hue // 60) % 6]
    return tuple(round((channel + match) * 255) for channel in (red, green, blue))


def resolve_icon(game_dir, slug, title, defaults, notes, force=False):
    """Decide which file the hub should show for this game.

    custom      -> the student drew their own icon192.png
    generated   -> icon is MicroStudio's default (or absent); use a real sprite
    placeholder -> nothing usable in the export at all
    """
    icon = game_dir / "icon192.png"
    generated = game_dir / GENERATED_ICON
    placeholder = game_dir / PLACEHOLDER_ICON

    if icon.is_file() and pngkit.file_hash(icon) not in defaults:
        for stale in (generated, placeholder):
            stale.unlink(missing_ok=True)
        return "custom", "icon192.png"

    why = "default MicroStudio icon" if icon.is_file() else "no icon192.png"

    # Rendering is slow in pure Python, so reuse an earlier result. Re-extracting
    # a zip wipes the game folder, which clears these automatically.
    if not force:
        if generated.is_file():
            placeholder.unlink(missing_ok=True)
            return "generated", GENERATED_ICON
        if placeholder.is_file():
            return "placeholder", PLACEHOLDER_ICON

    chosen, reason, unreadable = build_generated_icon(game_dir, defaults)
    for name, kind in unreadable:
        notes.append(f"  {slug}: skipped {name} ({kind}, not a readable PNG)")
    if chosen:
        placeholder.unlink(missing_ok=True)
        notes.append(f"  {slug}: {why}; generated icon from {chosen} ({reason})")
        return "generated", GENERATED_ICON

    generated.unlink(missing_ok=True)
    initials = build_placeholder_icon(game_dir, slug, title)
    notes.append(f"  {slug}: {why} and no usable sprites; drew \"{initials}\" placeholder")
    return "placeholder", PLACEHOLDER_ICON


def load_manual_fields():
    """Read hand-edited fields out of the existing games.json, keyed by slug."""
    if not GAMES_JSON.is_file():
        return {}
    try:
        existing = json.loads(GAMES_JSON.read_text(encoding="utf-8"))
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


def rebuild_games_json(force_icons=False):
    defaults = default_icon_hashes()
    manual = load_manual_fields()
    notes = []
    games = []
    for game_dir in sorted((path for path in GAMES_DIR.iterdir() if path.is_dir()), key=lambda p: p.name):
        if validate_game(game_dir) is not None:
            continue
        slug = game_dir.name
        title = title_from_index(game_dir / "index.html", slug.replace("-", " ").title())
        icon_source, icon_file = resolve_icon(game_dir, slug, title, defaults, notes, force_icons)
        entry = {
            "slug": slug,
            "title": title,
            "hasIcon": (game_dir / "icon192.png").is_file(),
            "iconSource": icon_source,
            "iconFile": icon_file,
        }
        # Hand-edited fields survive re-scans; new games start with empty ones.
        carried = manual.get(slug, {})
        entry["blurb"] = carried.pop("blurb", "")
        entry["featured"] = carried.pop("featured", False)
        entry.update(carried)
        games.append(entry)
    GAMES_JSON.write_text(json.dumps(games, indent=2) + "\n", encoding="utf-8")
    return games, notes


def main():
    force_icons = "--force-icons" in sys.argv[1:]
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

    games, notes = rebuild_games_json(force_icons)
    for zip_path in added:
        title = title_from_index(GAMES_DIR / slug_for(zip_path) / "index.html", slug_for(zip_path))
        print(f"Added: {title}.")
    if notes:
        print("Icons:")
        for note in notes:
            print(note)
    counts = {}
    for game in games:
        counts[game["iconSource"]] = counts.get(game["iconSource"], 0) + 1
    breakdown = ", ".join(f"{count} {name}" for name, count in sorted(counts.items()))
    print(f"Summary: Added {len(added)}. Skipped: {skipped}. Total working games: {len(games)}.")
    print(f"Icon sources: {breakdown or 'none'}.")


if __name__ == "__main__":
    main()