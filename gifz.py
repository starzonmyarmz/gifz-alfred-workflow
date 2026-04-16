#!/usr/bin/env python3
import json
import os
import sys
import tempfile
import time
import urllib.request

BASE_URL = "https://gifz.netlify.app/"
DATA_URL = BASE_URL + "gifs.json"
CACHE_TTL = 3600
CACHE_FILE = "gifs.json"
FETCH_TIMEOUT = 5


def cache_path():
    root = os.environ.get("alfred_workflow_cache") or tempfile.gettempdir()
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, CACHE_FILE)


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


def fetch():
    req = urllib.request.Request(DATA_URL, headers={"User-Agent": "gifz-alfred"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
        return json.load(resp)


def get_data():
    path = cache_path()
    cached, mtime = load_cache(path)
    if cached is not None and time.time() - mtime < CACHE_TTL:
        return cached, None
    try:
        data = fetch()
        save_cache(path, data)
        return data, None
    except Exception as err:
        if cached is not None:
            return cached, None
        return None, err


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

    items = [
        {"title": item["keywords"], "arg": BASE_URL + item["url"]}
        for item in data
        if query in item["keywords"].lower()
    ]
    json.dump({"items": items}, sys.stdout)


if __name__ == "__main__":
    main()
