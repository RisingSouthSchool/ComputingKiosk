# Classroom Game Hub

This is a small offline game launcher for MicroStudio HTML5 exports. It needs
only Python 3, which is already included with macOS.

## Add a game

1. Put the game's `.zip` export in `zips/`.
2. Double-click `start.command`.

The scanner extracts each new game, finds its `index.html` even when the zip
has an extra enclosing folder, and builds `games.json` automatically. A local
web server opens the hub in the default browser. Leave the terminal window
open while the hub is being used.

## Start automatically at login

To start the hub and open Chrome in kiosk mode whenever the user logs in, run
`setup_autostart.command` once from inside the **Student Station** account.
Do not run it from the admin account: the registration belongs to the account
that runs the setup script. It installs a per-user macOS LaunchAgent and is
safe to run again; it replaces the existing registration instead of creating a
duplicate.

To turn this off while debugging or reset it, run `remove_autostart.command`
from the same Student Station account. This unloads and deletes the LaunchAgent.

## Skipped games

The scanner prints a `Skipped ...` warning when an archive cannot be used. The
usual reason is that the zip is not a proper MicroStudio HTML5 export. A
working export must contain an `index.html` file and at least one JavaScript
engine file. Re-export the game from MicroStudio and replace the zip in
`zips/`, then run `start.command` again.

## Game icons

Every export ships an `icon192.png`, but MicroStudio fills it with a stock
gamepad picture until a student draws their own. The scanner compares each
file against the known stock artwork by checksum, so a genuinely plain
hand-drawn icon still counts as custom. Each game ends up as one of:

- `"iconSource": "custom"` — the student drew it. `icon192.png` is used as-is.
- `"iconSource": "generated"` — the icon was stock or missing, so the scanner
  picked a real sprite from the game (preferring names like `player`, `hero`,
  `title`, `main`, otherwise the largest image) and wrote a square 192px
  `generated_icon.png` beside it.
- `"iconSource": "placeholder"` — the export had no usable artwork at all, so
  the scanner drew `placeholder_icon.png`: the game's initials on a colour
  derived from its slug, so it looks the same after every re-scan.

The scanner only ever adds these two new files; it never edits anything that
came out of the zip. It prints which sprite it chose and why. Re-runs reuse the
existing image — pass `--force-icons` to redraw them all:

```
python3 scan_and_build.py --force-icons
```

Sprites that are not readable PNGs are reported and skipped. Students often
save a JPEG or WebP from the web and rename it `.png`; those cannot be used as
icons, though the games still run fine.

If MicroStudio ever changes its stock icon, drop a copy of the new default
into a `default_icons/` folder in this directory. Every file in there is
treated as a default, alongside the ones already built in.

## Featured games and blurbs

Two fields in `games.json` are yours to fill in by hand, and the scanner
preserves them across re-scans:

- `"blurb"` — one sentence about the project or the brief.
- `"featured"` — set to `true` to include the game in the idle showcase.

A `"student"` field is optional; if present it is shown too. New games start
with an empty blurb and `featured: false`.

After 20 seconds with nobody touching the hub, it fades into attract mode and
cycles through the featured games, six seconds each, showing the icon, title,
student and blurb. If nothing is marked featured yet it cycles through every
game instead, so the screen is never blank. Any mouse movement, click, key or
controller input returns to the tile grid immediately. Attract mode never
appears while a game is actually being played.

## Keep these files intact

Do not rename or edit files inside a game's exported folder. Apart from
`blurb`, `featured` and `student`, leave `games.json` alone: every other field
is rebuilt automatically each time the launcher runs. You can delete a game's
folder from `games/` and its entry will disappear from the next generated
list, but remove the original zip from `zips/` too if you do not want it
extracted again.