#!/usr/bin/env python3
"""Presenty CLI — create, fetch, and update Presenty presentations.

Self-contained: Python 3 standard library only. Talks directly to the
Presenty Supabase backend (anonymous writes are allowed by design).

Usage:
  # Create a new presentation from a markdown file. Prints edit/view URLs.
  python3 presenty.py create --name "My Presentation" --file slides.md

  # Fetch the markdown of an existing presentation (by URL or id).
  python3 presenty.py get --url "https://www.presenty.dev/published/edit/912988/my-presentation"
  python3 presenty.py get --id 912988 --out existing.md

  # Update an existing presentation's markdown (preserves theme & settings).
  python3 presenty.py update --id 912988 --file slides.md
  python3 presenty.py update --url "<presenty url>" --file slides.md --name "New Name"

Options:
  --theme      Reveal.js theme for create (default: Black). One of:
               Black, White, League, Beige, Moon, Solarized, Night, Serif, Simple, Sky, Blood
  --animation  Slide transition for create (default: Slide). e.g. Slide, Zoom, Fade, Concave, Convex, None
"""

import argparse
import json
import random
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = "https://blhyjvsuxivofwbhzhjs.supabase.co"
# Public anonymous key — the same key shipped in the Presenty web app bundle.
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJsaHlqdnN1eGl2b2Z3Ymh6aGpzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI4Njg4NDUsImV4cCI6MjA5ODQ0NDg0NX0."
    "t0fPTVIJfwE2fiu30nn6NRef6C55N8hcOi4449m0J1M"
)
REST = f"{SUPABASE_URL}/rest/v1/markdown"
SITE = "https://www.presenty.dev"

DEFAULT_EDITOR = {
    "showPen": True,
    "showSlides": True,
    "toggleViewer": False,
    "showAutoSlide": False,
    "themeSelected": "Black",
    "showDrawingArea": True,
    "animationSelected": "Slide",
    "mermaidStyleSelected": "",
    "showAutoDelayInMS": 2000,
    "drawPerStep": False,
}


def request(method, url, body=None):
    headers = {
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else []
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"ERROR: {method} {url} -> HTTP {e.code}\n{detail}")
    except urllib.error.URLError as e:
        raise SystemExit(f"ERROR: network problem reaching Presenty backend: {e.reason}")


def slugify(name):
    return re.sub(r"\s+", "-", name.strip()).lower()


def parse_id(args):
    if getattr(args, "id", None):
        return int(args.id)
    if getattr(args, "url", None):
        m = re.search(r"/published/(?:edit|view)/(\d+)", args.url)
        if m:
            return int(m.group(1))
        raise SystemExit(
            "ERROR: could not find a presentation id in that URL. "
            "Expected a URL like https://www.presenty.dev/published/edit/912988/my-presentation"
        )
    raise SystemExit("ERROR: pass --id or --url to identify the presentation")


def fetch_row(pid):
    rows = request("GET", f"{REST}?id=eq.{pid}&select=*")
    if not rows:
        raise SystemExit(f"ERROR: no presentation found with id {pid}")
    return rows[0]


def print_urls(pid, url_name):
    print(f"id: {pid}")
    print(f"edit_url: {SITE}/published/edit/{pid}/{url_name}")
    print(f"view_url: {SITE}/published/view/{pid}/{url_name}")


def cmd_create(args):
    content = open(args.file, encoding="utf-8").read()
    editor = dict(DEFAULT_EDITOR)
    editor["content"] = content
    if args.theme:
        editor["themeSelected"] = args.theme
    if args.animation:
        editor["animationSelected"] = args.animation
    url_name = slugify(args.name)
    now = datetime.now(timezone.utc).isoformat()

    last_error = None
    for _ in range(5):  # retry on the rare random-id collision
        pid = random.randint(100000, 999999)
        body = {
            "id": pid,
            "name": args.name,
            "url_name": url_name,
            "allow_edit": True,
            "editor": editor,
            "modified": now,
        }
        try:
            rows = request("POST", REST, body)
        except SystemExit as e:
            if "duplicate key" in str(e) or "23505" in str(e):
                last_error = e
                continue
            raise
        row = rows[0] if rows else body
        print("CREATED")
        print_urls(row["id"], row.get("url_name") or url_name)
        return
    raise SystemExit(f"ERROR: could not find a free id after retries: {last_error}")


def cmd_get(args):
    row = fetch_row(parse_id(args))
    content = (row.get("editor") or {}).get("content", "")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"name: {row.get('name')}")
        print(f"saved markdown to: {args.out}")
        print_urls(row["id"], row.get("url_name") or "presentation")
    else:
        print(content)


def cmd_update(args):
    pid = parse_id(args)
    row = fetch_row(pid)
    editor = row.get("editor") or dict(DEFAULT_EDITOR)
    editor["content"] = open(args.file, encoding="utf-8").read()
    if args.theme:
        editor["themeSelected"] = args.theme
    if args.animation:
        editor["animationSelected"] = args.animation
    patch = {"editor": editor, "modified": datetime.now(timezone.utc).isoformat()}
    if args.name:
        patch["name"] = args.name
        patch["url_name"] = slugify(args.name)
    rows = request("PATCH", f"{REST}?id=eq.{pid}", patch)
    row = rows[0] if rows else {**row, **patch}
    print("UPDATED")
    print_urls(pid, row.get("url_name") or "presentation")


def main():
    p = argparse.ArgumentParser(description="Presenty presentation CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="create a new presentation")
    c.add_argument("--name", required=True, help="presentation display name")
    c.add_argument("--file", required=True, help="markdown file with slide content")
    c.add_argument("--theme", help="theme, e.g. Black, White, League, Moon")
    c.add_argument("--animation", help="transition, e.g. Slide, Zoom, Fade")
    c.set_defaults(fn=cmd_create)

    g = sub.add_parser("get", help="fetch markdown of an existing presentation")
    g.add_argument("--id", help="presentation id")
    g.add_argument("--url", help="presenty.dev published URL")
    g.add_argument("--out", help="write markdown to this file instead of stdout")
    g.set_defaults(fn=cmd_get)

    u = sub.add_parser("update", help="update an existing presentation")
    u.add_argument("--id", help="presentation id")
    u.add_argument("--url", help="presenty.dev published URL")
    u.add_argument("--file", required=True, help="markdown file with the new content")
    u.add_argument("--name", help="optionally rename the presentation")
    u.add_argument("--theme", help="optionally change theme")
    u.add_argument("--animation", help="optionally change transition")
    u.set_defaults(fn=cmd_update)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
