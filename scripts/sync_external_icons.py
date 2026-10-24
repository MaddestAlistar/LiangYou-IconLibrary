#!/usr/bin/env python3
"""Nightly incremental import of NEW external icon feed entries into the full subscription.

First successful run records a baseline and deliberately does not bulk-import old icons.
Only later feed additions are imported. Original subscription is never modified.
"""
import json
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "LiangYou-Emby-Icons.json"
STATE = ROOT / "data" / "external-icon-sync-state.json"
SOURCES = {
    "lige47": "https://raw.githubusercontent.com/lige47/lige_icon/main/lige-emby-icon.json",
    "sooyaaabo": "https://raw.githubusercontent.com/sooyaaabo/IconLibrary/main/Emby-Icon.json",
}

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "LiangYou-IconLibrary-nightly-sync", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            raise ValueError("Source unavailable: " + url)
        return json.load(response)

def valid_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        return False
    u = urlsplit(value)
    return u.scheme == "https" and bool(u.hostname) and u.hostname not in ("localhost", "127.0.0.1")

def name_base(name):
    return re.sub(r"\\s+0*[0-9]+$", "", str(name).strip())

def main():
    feeds = {}
    for key, url in SOURCES.items():
        obj = fetch(url)
        icons = obj.get("icons")
        if not isinstance(icons, list) or not icons:
            raise ValueError("Invalid or empty source: " + key)
        feeds[key] = icons
    catalog = json.loads(TARGET.read_text(encoding="utf-8"))
    if not isinstance(catalog.get("icons"), list) or len(catalog["icons"]) < 5:
        raise ValueError("Unexpected official catalog; refusing to overwrite")
    if STATE.exists():
        state = json.loads(STATE.read_text(encoding="utf-8"))
        if set(state.get("seen", {})) != set(SOURCES):
            raise ValueError("Source baseline keys changed; review state manually")
    else:
        state = {"schema": 1, "seen": {key: [] for key in SOURCES}, "initialized": False}
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    existing_urls = {str(x.get("url", "")).strip() for x in catalog["icons"]}
    existing_names = {str(x.get("name", "")).strip().casefold() for x in catalog["icons"]}
    seen = {key: set(state["seen"][key]) for key in SOURCES}
    initialized = bool(state.get("initialized", False))
    added = 0
    for key, icons in feeds.items():
        current = set()
        for item in icons:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url", "")).strip()
            name = str(item.get("name", "")).strip()
            if not valid_url(url) or not name or len(name) > 110:
                continue
            current.add(url)
            if not initialized or url in seen[key] or url in existing_urls:
                continue
            # GIF must be searchable using 动态; preserve other source labels.
            if urlsplit(url).path.lower().endswith(".gif") and "动态" not in name:
                name += " 动态"
            label = name
            if label.casefold() in existing_names:
                base = name_base(name)
                n = 2
                while (base + " " + f"{n:02d}").casefold() in existing_names:
                    n += 1
                label = base + " " + f"{n:02d}"
            catalog["icons"].append({"name": label, "url": url})
            existing_names.add(label.casefold())
            existing_urls.add(url)
            added += 1
        if len(current) < 1:
            raise ValueError("No valid icon URLs for " + key)
        # Remember all valid URLs, including ones already present in the catalog.
        seen[key].update(current)
    state["seen"] = {key: sorted(values) for key, values in seen.items()}
    state["initialized"] = True
    state["checkedAt"] = now
    state["lastAdded"] = added
    state["sources"] = SOURCES
    if added:
        pinned = catalog["icons"][:5]
        rest = catalog["icons"][5:]
        rest.sort(key=lambda x: (bool(re.match(r"^[0-9]", str(x.get("name", "")))), str(x.get("name", "")).casefold()))
        catalog["icons"] = pinned + rest
        catalog["description"] = re.sub(r"更新时间：\\d{4}-\\d{2}-\\d{2}", "更新时间：" + now, str(catalog.get("description", "")))
        TARGET.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"External icon sync {now}: baseline={not initialized}, added={added}, total={len(catalog['icons'])}")

if __name__ == "__main__":
    main()
