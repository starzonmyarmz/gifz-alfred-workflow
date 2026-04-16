# CLAUDE.md

Project guide for Claude Code.

## What this is

Alfred workflow that searches a personal gif collection hosted at `https://gifz.netlify.app/`. Implementation is a single Python 3 file, `gifz.py`, using only the standard library. No `npm install`, no `pip install`.

## Entry point

Alfred invokes `/usr/bin/python3 gifz.py "$1"` (configured in `info.plist`, script filter node, `<key>script</key>`). `$1` is the user's query string.

## Output contract

Stdout must be valid Alfred Script Filter JSON:

```json
{"items": [{"title": "...", "arg": "..."}]}
```

Never print anything else to stdout. Send logs/diagnostics to stderr.

## Data source

`https://gifz.netlify.app/gifs.json` — array of objects shaped `{"keywords": str, "url": str}`. `url` is relative; prepend `https://gifz.netlify.app/` for the final `arg`.

## Cache

Disk cache at `$alfred_workflow_cache/gifs.json` (Alfred sets this env var; falls back to `tempfile.gettempdir()`). TTL 1 hour. On fetch failure with a stale cache present, serve stale. On fetch failure with no cache, emit a single error item (`valid: false`) so the user sees the problem.

## Rebuilding `Gifz.alfredworkflow`

The `.alfredworkflow` file is a zip of `info.plist`, `icon.png`, `gifz.py`:

```
cd /Users/marino/Code/gifz-alfred-workflow
rm -f Gifz.alfredworkflow
zip Gifz.alfredworkflow info.plist icon.png gifz.py
```

Keep the existing bundle id (`com.starzonmyarmz.gif.alfredworkflow`) so Alfred upgrades in place.

## Testing

```
python3 gifz.py anchorman   # expect items array
python3 gifz.py ""          # expect {"items": []}
```

## Don'ts

Do not reintroduce Node, npm, `alfy`, or any runtime dependency. The point of this codebase is zero install step.
