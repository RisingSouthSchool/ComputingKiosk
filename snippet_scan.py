#!/usr/bin/env python3
"""Build snippets.json: short pieces of student code and SQL for standby mode.

Sources:
  - python_projects/**/*.py and db_projects/**/*.py: whole functions, trimmed
    to a screen-sized length (code snippets).
  - db_projects/**/*.sql and the .db files themselves: CREATE TABLE statements
    (schemas), plus SELECT queries found in the .sql and .py files (sql snippets).

INSERT statements are never used: they hold the sample data. Anything that
looks like an email address, a hard-coded password or a long number is
skipped, as are files named in SKIP_FILES.

Hand-edited fields survive re-scans, like the other manifests: set
"hidden": true on a snippet to keep it out of standby mode, or edit "title"
and "note". Everything else is rebuilt on every run.
"""

import ast
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "snippets.json"
PY_MANIFEST = ROOT / "pythonProjects.json"
DB_MANIFEST = ROOT / "databaseProjects.json"
PYTHON_DIR = ROOT / "python_projects"
DB_DIR = ROOT / "db_projects"

MIN_LINES = 5
MAX_LINES = 16
MAX_WIDTH = 78
MAX_PER_PROJECT = 6          # keeps one big project (poker) from filling the screen time
SKIP_FILES = {"main-mrsouthwood.py", "test.py"}   # teacher copies and scratch files
MANAGED = {"id", "kind", "project", "year", "file", "text"}

SENSITIVE = re.compile(
    r"[\w.+-]+@[\w-]+\.?[\w.]*"                       # email-ish
    r"|(?i:password|passkey)\s*=\s*['\"]"             # hard-coded password
    r"|\b\d{9,}\b",                                    # long numbers (phones, ids)
)


def load_titles(path):
    try:
        return {item["slug"]: item.get("title") or item["slug"] for item in json.loads(path.read_text(encoding="utf-8"))}
    except (OSError, ValueError, KeyError):
        return {}


def clean(text):
    """Tabs to spaces, strip trailing space and shared indentation."""
    lines = [line.rstrip().expandtabs(4) for line in text.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    indent = min((len(line) - len(line.lstrip()) for line in lines if line.strip()), default=0)
    return "\n".join(line[indent:] for line in lines)


def acceptable(text):
    lines = text.splitlines()
    if not (MIN_LINES <= len(lines) <= MAX_LINES):
        return False
    if max(len(line) for line in lines) > MAX_WIDTH:
        return False
    if SENSITIVE.search(text):
        return False
    # Mostly blank or mostly comments is not interesting to look at.
    real = [line for line in lines if line.strip() and not line.strip().startswith(("#", "--"))]
    return len(real) >= MIN_LINES - 1


def python_functions(path):
    """Yield (name, text) for each top-level or class-level function worth showing."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
        return
    lines = source.splitlines()
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        end = getattr(node, "end_lineno", None)
        if not end:
            continue
        text = clean("\n".join(lines[node.lineno - 1:end]))
        if acceptable(text):
            yield node.name, text


def sql_statements(text):
    """Split SQL text into statements, keeping them as written."""
    for statement in re.split(r";\s*(?:\n|$)", text):
        statement = clean(statement)
        if statement:
            yield statement + ";"


def sql_from_python(path):
    """SELECT queries inside string literals of a .py file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
        return
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.match(r"\s*SELECT\b", node.value, re.I):
            text = clean(node.value)
            yield text if text.rstrip().endswith(";") else text + ";"


def sql_snippets(project_dir):
    """Yield (file, kind_label, text) of CREATE TABLE and SELECT statements."""
    seen = set()

    def offer(file, text):
        key = re.sub(r"\s+", " ", text.lower())
        if key in seen or not re.match(r"\s*(CREATE TABLE|SELECT)\b", text, re.I) or not acceptable(text):
            return None
        seen.add(key)
        return (file, text)

    for path in sorted(project_dir.rglob("*.sql")):
        for statement in sql_statements(path.read_text(encoding="utf-8", errors="ignore")):
            statement = re.sub(r"^(?:\s*--[^\n]*\n)+", "", statement)   # leading comment lines
            found = offer(path.name, statement)
            if found:
                yield found
    for path in sorted(project_dir.rglob("*.py")):
        if path.name.lower() in SKIP_FILES:
            continue
        for query in sql_from_python(path):
            found = offer(path.name, query)
            if found:
                yield found
    # Schemas straight from the databases (they match what the program really uses).
    for path in sorted(project_dir.rglob("*.db")):
        try:
            with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as database:
                rows = database.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND sql IS NOT NULL AND name NOT LIKE 'sqlite_%'").fetchall()
        except sqlite3.Error:
            continue
        for (sql,) in rows:
            found = offer(path.name, clean(sql) + ";")
            if found:
                yield found


def snippet_id(project, kind, text):
    return f"{project}:{kind}:" + hashlib.sha1(re.sub(r"\s+", " ", text).encode()).hexdigest()[:8]


def main():
    previous = {}
    if OUTPUT.exists():
        try:
            previous = {item["id"]: item for item in json.loads(OUTPUT.read_text(encoding="utf-8"))}
        except (ValueError, KeyError):
            print("Existing snippets.json is unreadable; rebuilding without hand edits.", file=sys.stderr)

    py_titles = load_titles(PY_MANIFEST)
    db_titles = load_titles(DB_MANIFEST)
    snippets = []

    def add(project, title, year, kind, file, text, label=None):
        sid = snippet_id(project, kind, text)
        entry = {"id": sid, "kind": kind, "project": title, "year": year, "file": file, "text": text}
        if label:
            entry["label"] = label
        # carry over hand-edited fields (hidden, note, a retitled project, ...)
        for key, value in previous.get(sid, {}).items():
            if key not in MANAGED and key != "label":
                entry[key] = value
        if "title" in previous.get(sid, {}):
            entry["project"] = previous[sid]["title"]
        snippets.append(entry)

    # Student Python, from both the Year 11 Python and database projects.
    for base, titles, year in ((PYTHON_DIR, py_titles, 11), (DB_DIR, db_titles, 11)):
        if not base.is_dir():
            continue
        for project in sorted(p for p in base.iterdir() if p.is_dir()):
            title = titles.get(project.name, project.name.replace("-", " ").title())
            found = []
            for path in sorted(project.rglob("*.py")):
                if path.name.lower() in SKIP_FILES or "__pycache__" in path.parts:
                    continue
                for name, text in python_functions(path):
                    found.append((path.name, text))
            # spread the picks across the files rather than taking the first N
            step = max(1, len(found) // MAX_PER_PROJECT)
            for file, text in found[::step][:MAX_PER_PROJECT]:
                add(project.name, title, year, "code", file, text)

    # SQL, from the database projects only.
    if DB_DIR.is_dir():
        for project in sorted(p for p in DB_DIR.iterdir() if p.is_dir()):
            title = db_titles.get(project.name, project.name.replace("-", " ").title())
            found = list(sql_snippets(project))
            queries = [item for item in found if item[1].upper().startswith("SELECT")]
            schemas = [item for item in found if item[1].upper().startswith("CREATE")]
            picks = queries[:MAX_PER_PROJECT - 2] + schemas[:2]
            for file, text in picks:
                add(project.name, title, 11, "sql", file, text, "Schema" if text.upper().startswith("CREATE") else "Query")

    snippets.sort(key=lambda item: (item["kind"], item["project"], item["id"]))
    OUTPUT.write_text(json.dumps(snippets, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {kind: sum(1 for item in snippets if item["kind"] == kind) for kind in ("code", "sql")}
    hidden = sum(1 for item in snippets if item.get("hidden"))
    print(f"snippets.json: {counts['code']} code, {counts['sql']} SQL ({hidden} hidden)")


if __name__ == "__main__":
    main()
