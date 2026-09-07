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

## Keep these files intact

Do not rename or edit files inside a game's exported folder. Do not hand-edit
`games.json`; it is rebuilt automatically every time the launcher runs. You
can delete a game's folder from `games/` and its entry will disappear from the
next generated list, but remove the original zip from `zips/` too if you do
not want it extracted again.