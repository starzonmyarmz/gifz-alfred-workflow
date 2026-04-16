#!/usr/bin/env python3
import json
import os
import sys
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "https://gifz.netlify.app/"
DATA_URL = BASE_URL + "gifs.json"
CACHE_TTL = 3600
CACHE_FILE = "gifs.json"
THUMB_DIR = "thumbs"
FETCH_TIMEOUT = 5
THUMB_TIMEOUT = 5
THUMB_WORKERS = 8


def cache_root():
    root = os.environ.get("alfred_workflow_cache") or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    return root


def cache_path():
    return os.path.join(cache_root(), CACHE_FILE)


def thumb_dir():
    path = os.path.join(cache_root(), THUMB_DIR)
    os.makedirs(path, exist_ok=True)
    return path


def load_cache(path):
    try:
        with open(path, "rb") as f:
            return json.load(f), os.path.getmtime(path)
    except (OSError, ValueError):
        return None, 0


def save_cache(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except OSError:
        pass


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gifz-alfred"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
        return json.load(resp)


def get_data():
    path = cache_path()
    cached, mtime = load_cache(path)
    if cached is not None and time.time() - mtime < CACHE_TTL:
        return cached, None
    try:
        data = fetch_json(DATA_URL)
        save_cache(path, data)
        return data, None
    except Exception as err:
        if cached is not None:
            return cached, None
        return None, err


def ensure_thumb(thumb_rel):
    local = os.path.join(thumb_dir(), os.path.basename(thumb_rel))
    if os.path.exists(local) and os.path.getsize(local) > 0:
        return local
    try:
        req = urllib.request.Request(BASE_URL + thumb_rel, headers={"User-Agent": "gifz-alfred"})
        with urllib.request.urlopen(req, timeout=THUMB_TIMEOUT) as resp:
            tmp = local + ".part"
            with open(tmp, "wb") as f:
                f.write(resp.read())
            os.replace(tmp, local)
        return local
    except Exception:
        return None


def prefetch_thumbs(thumb_rels):
    with ThreadPoolExecutor(max_workers=THUMB_WORKERS) as pool:
        pool.map(ensure_thumb, thumb_rels)


def main():
    query = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""
    data, err = get_data()

    if err is not None:
        json.dump({"items": [{
            "title": "Failed to load gifs",
            "subtitle": str(err),
            "valid": False,
        }]}, sys.stdout)
        return

    if not query:
        json.dump({"items": []}, sys.stdout)
        return

    matches = [item for item in data if query in item["keywords"].lower()]

    thumb_rels = [m["thumb"] for m in matches if m.get("thumb")]
    if thumb_rels:
        prefetch_thumbs(thumb_rels)

    items = []
    for m in matches:
        entry = {"title": m["keywords"], "arg": BASE_URL + m["url"]}
        thumb_rel = m.get("thumb")
        if thumb_rel:
            local = os.path.join(thumb_dir(), os.path.basename(thumb_rel))
            if os.path.exists(local) and os.path.getsize(local) > 0:
                entry["icon"] = {"path": local}
        items.append(entry)

    json.dump({"items": items}, sys.stdout)


if __name__ == "__main__":
    main()
