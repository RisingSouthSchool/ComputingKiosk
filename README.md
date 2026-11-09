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

## Add a Python console project

1. Put the student's `.zip` submission in `py_zips/`.
2. Double-click `start.command`.

This needs the `websockets` package. A copy is bundled in `vendor/py/`, so there
is nothing to install; if a newer one is installed for your Python it is used
instead.

`python_scan.py` extracts each new submission into `python_projects/<slug>/`,
preserving its internal folder structure exactly as zipped (a `Game/` or
`imposter/` subfolder with supporting files stays put). It finds the entry
point to run using this priority order:

1. A file literally named `main.py`, anywhere in the zip.
2. If none, a file whose name matches the zip's own name.
3. If none, and there is exactly one `.py` file anywhere in the zip, that one.
4. Otherwise the submission is skipped, and the scanner prints which `.py`
   files it found and why it would not guess. Re-export the project so one of
   the above rules applies unambiguously, or rename a file to `main.py`.

Results go in `pythonProjects.json`: `slug`, `title` (derived from the zip's
name), `entryFile`, and two fields you fill in by hand and that survive
re-scans — `student` and `blurb` (shown on the project's pre-launch screen).

On the hub, a Python project opens as a real, live terminal session (using a
pty on the server, streamed to the browser over WebSocket) rather than a
static page, so `input()`, `curses`, and other interactive terminal programs
work as they would running locally. Every session is force-closed after 10
minutes, and any way the program can end -- finishing normally, crashing,
being killed by the timeout, or losing the connection -- always returns to
the Python projects list automatically.

## Add a Year 11 database project

Database projects (Python + SQLite) live in `db_projects/`, one folder per
project, and appear under the **Y11 Databases** tile on the landing screen.

1. Make a folder, e.g. `db_projects/my-project/`, with the program, its `.db`
   file and any `.sql` files. Use a neutral folder name; do not put student
   names in file names, code or the database itself.
2. Add an entry to `databaseProjects.json`: `slug` (the folder name), `title`,
   `entryFile` (the `.py` to run, relative to the folder), `blurb`, and leave
   `student` empty.
3. Make the scripts executable (`chmod +x db_projects/my-project/*.py`) and
   commit.

They run in the same live terminal as the Python projects, but on a temporary
copy of the folder that is deleted afterwards, so changes made while using a
program never alter the stored `.db` file. Projects that import `cs50` need
that package installed for the kiosk's Python (`pip3 install cs50`).

## Add a web app

Single-page web apps (the Year 10 "AI created, human designed" project) live in
`webapps/`, one folder per app:

1. Make a folder, e.g. `webapps/my-app/`, and put the app's HTML file in it
   named `index.html` (plus any images or scripts it needs).
2. Double-click `start.command`.

`webapp_scan.py` builds `webapps.json` and draws a placeholder icon for any app
without a custom `icon192.png`. Hand-edit `title`, `student`, `blurb` and
`featured` in `webapps.json`; they survive re-scans. New apps start with
`featured: true`; set it to `false` to keep one out of the featured list.

Web apps open in the same player as games, and are set up to run offline:

- Libraries, icons and fonts (Three.js, Chart.js, fengari, Font Awesome, the
  Google fonts) are saved in `vendor/web/`, and each Tailwind app has its own
  compiled `tailwind.css` next to its `index.html`.
- Photos on the internet (recipe photos, Minecraft avatars) are downloaded by
  `cache_remote_images.py`, which `start.command` runs each launch. Run
  `start.command` once while the kiosk is online and they are saved to each
  app's `images/` folder for good. Until then, an app shows a plain grey tile
  with the first letter instead of a broken image.
- A new app copied from an AI tool will usually still point at CDNs. Its
  scripts, styles and fonts need swapping for the local files in `vendor/web/`
  (and Tailwind compiling to a `tailwind.css`) before it works offline.

## Start automatically at login

To start the hub and open Chrome in kiosk mode whenever the user logs in, run
`setup_autostart.command` once from inside the **Student Station** account.
Do not run it from the admin account: the registration belongs to the account
that runs the setup script. It installs a per-user macOS LaunchAgent and is
safe to run again; it replaces the existing registration instead of creating a
duplicate.

To turn this off while debugging or reset it, run `remove_autostart.command`
from the same Student Station account. This unloads and deletes the LaunchAgent.

## Updating from GitHub

The landing screen shows the version (commit count, short hash and date) in the
bottom-right corner next to a **Check for updates** button. The button pulls the
latest `main` from GitHub, rebuilds the game, project and web app lists, and
reloads the page (restarting the server first if its code changed). With no
internet it says so instead of failing silently. The page also reloads itself
when the served version changes, for example after the background auto-sync
(`setup_autosync.command`) has pulled an update. Votes (`votes.json`) are always
kept. The button needs the hub folder to be a git clone.

## Idle behaviour and the usage log

- **No input on a menu for 20 seconds** (`IDLE_MS`): the showcase fades in.
- **No input in a game, web app or Python/database program for 2 minutes**
  (`PLAY_IDLE_MS`): it is closed, the hub returns to the home screen and the
  showcase fades in over it. A video that is playing counts as input. The hub
  listens for keys, mouse, touch and wheel inside the game frame (games are
  served from the same origin) and for gamepad input.
- Either way the showcase always sits on the home screen, and touching the
  screen starts a fresh visit for the next person.

Every time something is open the hub logs a session to `usage.db` (SQLite, in
the hub folder, git-ignored so it stays on the kiosk and survives updates):
`started`, `last_seen` (a heartbeat every 30 s), `ended`, `kind` (`game`,
`webapp`, `python`, `db` or `video`), `slug`, a random per-visit `visitor` id
and the end `reason` (`back`, `idle`, `exit`, `crash`, `timeout`, `paused`,
`ended`, `unload`). It records what was used and for how long, never who. Query
it with `sqlite3 usage.db`, for example:

```
select kind, slug, count(*) from sessions where ended - started >= 30 group by 1, 2 order by 3 desc;
```

## Likes and spam limits

Games and web apps both have a 👍 button (keyboard `V`, gamepad Y). The kiosk is
shared, so there are no accounts; instead:

- A person can like each game or web app **once per visit**. A new visit starts
  whenever the hub has been idle long enough to drop into attract mode.
- The server also refuses a second like for the same item within
  `VOTE_COOLDOWN_SECONDS` (10), and more than `VOTE_GLOBAL_LIMIT` (20) likes in
  `VOTE_GLOBAL_WINDOW_SECONDS` (60) across everything. These are constants at
  the top of `server.py`; they reset when the server restarts.
- Only games and web apps that actually exist can be liked, so junk keys can't
  get into `votes.json`. Web app likes are stored as `webapp:<slug>`.

## Year and type tags

Two more hand-edited fields in `games.json` (kept across re-scans) drive the
filter chips at the top of the Games view and the label on each tile:

- `"year"` — e.g. `9` or `10`, shown as "Year 9".
- `"type"` — e.g. `"MicroStudio"` or `"Vibe coded"`.

Games without them still appear under "All". To add a non-MicroStudio game
(for example a vibe-coded single-file HTML game), put its folder in
`games/<slug>/` with an `index.html` (an inline `<script>` is enough), make it
work offline using the files in `vendor/web/` (for example
`../../vendor/web/three.min.js`), then set its `year` and `type`.

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

The featured list is every game and web app marked `featured: true`. The
banner on the landing screen shows one of them at random and swaps to a
different one every 5 minutes (it never repeats the same one back to back).

After 20 seconds with nobody touching the hub, it fades into attract mode and
cycles through the featured list, six seconds each, showing the icon, title,
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