#!/usr/bin/env python3
"""Generate keyframe stills from a director-authored PROMPTS.md.

Reads a `PROMPTS.md` file containing one prompt block per keyframe (the
output of a director-persona keyframe pass — e.g., Hitchcock, Deakins),
calls the OpenAI Images API (gpt-image-1) for each block, and saves PNGs
into the same directory. The keyframes then feed an image-to-video pass
(Kling, Runway, etc.) downstream.

Authentication
--------------
Reads OPENAI_API_KEY from the environment. Source from canonical secrets:

    set -a && source ~/.config/dev-secrets/secrets.env && set +a
    python3 scripts/render_keyframes.py

Idempotency
-----------
Skips keyframes whose PNG already exists. --force regenerates all.
--only <name>[,<name>...] renders a single keyframe or comma-separated list.

Output size
-----------
gpt-image-1 supports 1024x1024, 1024x1536 (portrait), and 1536x1024
(landscape, ~3:2). Default 1536x1024 — the closest available to 16:9 —
trusting the downstream image-to-video stage to frame within 16:9 at
animation time. Use --size to override.

PROMPTS.md format
-----------------
Each block looks like:

    ### kf-name-slug.png
    <prompt body — markdown bold/italics tolerated>
    **Aspect ratio:** 16:9   (this line is stripped)
    **Format:** PNG          (this line is stripped)
    ---

Any kebab-case filename (with .png extension) at h3 level is recognized.
Blocks separated by `---` lines or by the next h3.

Run
---
    python3 scripts/render_keyframes.py
    python3 scripts/render_keyframes.py --only kf-opening-shot
    python3 scripts/render_keyframes.py --prompts-file path/to/PROMPTS.md
    python3 scripts/render_keyframes.py --dry-run
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_PROMPTS_FILE = "film/render/kling/keyframes/PROMPTS.md"

API_URL = "https://api.openai.com/v1/images/generations"
MODEL = "gpt-image-1"
DEFAULT_SIZE = "1536x1024"
DEFAULT_QUALITY = "high"

KEYFRAME_BLOCK_RE = re.compile(
    r"### ([a-z][a-z0-9_\-]*)\.png\s*\n(.*?)(?=^---\s*$|^### |\Z)",
    re.DOTALL | re.MULTILINE,
)


def parse_prompts(text: str) -> dict[str, str]:
    """Return {keyframe_name: prompt_text} parsed from PROMPTS.md."""
    blocks: dict[str, str] = {}
    for match in KEYFRAME_BLOCK_RE.finditer(text):
        name = match.group(1)
        body = match.group(2).strip()
        # Strip directive lines that don't belong in the image prompt.
        body = re.sub(r"\*\*Aspect ratio:\*\*.*$", "", body, flags=re.MULTILINE)
        body = re.sub(r"\*\*Format:\*\*.*$", "", body, flags=re.MULTILINE)
        body = re.sub(r"\*\*Size:\*\*.*$", "", body, flags=re.MULTILINE)
        # Drop markdown bold markers; gpt-image-1 doesn't need them.
        body = re.sub(r"\*\*([^*]+)\*\*", r"\1", body)
        blocks[name] = body.strip()
    return blocks


def call_openai(prompt: str, *, api_key: str, size: str, quality: str) -> bytes:
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": 1,
    }).encode()
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {detail}") from None
    return base64.b64decode(body["data"][0]["b64_json"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render keyframe PNGs from a director-authored PROMPTS.md.",
    )
    parser.add_argument(
        "--prompts-file",
        default=DEFAULT_PROMPTS_FILE,
        help=f"Path to PROMPTS.md (default: {DEFAULT_PROMPTS_FILE})",
    )
    parser.add_argument(
        "--out-dir",
        help="Directory to write PNGs into (default: dirname of --prompts-file)",
    )
    parser.add_argument("--only", help="Comma-separated keyframe slugs (e.g., kf-foo,kf-bar). Defaults to all blocks.")
    parser.add_argument("--force", action="store_true", help="Regenerate even if PNG exists")
    parser.add_argument("--size", default=DEFAULT_SIZE, help=f"Image size (default: {DEFAULT_SIZE})")
    parser.add_argument("--quality", default=DEFAULT_QUALITY, help=f"Image quality (default: {DEFAULT_QUALITY})")
    parser.add_argument("--dry-run", action="store_true", help="Parse prompts, skip API calls")
    args = parser.parse_args()

    prompts_path = Path(args.prompts_file).resolve()
    if not prompts_path.exists():
        print(f"error: prompts file not found at {prompts_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).resolve() if args.out_dir else prompts_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    blocks = parse_prompts(prompts_path.read_text())
    if not blocks:
        print(f"error: no keyframe blocks (### kf-name.png) found in {prompts_path}", file=sys.stderr)
        return 1

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.dry_run:
        print(
            "error: OPENAI_API_KEY not set. source ~/.config/dev-secrets/secrets.env first.",
            file=sys.stderr,
        )
        return 1

    targets = [s.strip() for s in args.only.split(",")] if args.only else sorted(blocks)

    rendered = 0
    skipped = 0
    failed = 0
    for name in targets:
        if name not in blocks:
            print(f"skip {name}: not in prompts file (have: {sorted(blocks)})")
            continue
        out_path = out_dir / f"{name}.png"
        if out_path.exists() and not args.force:
            print(f"skip {name}: {out_path.name} already exists (use --force to regenerate)")
            skipped += 1
            continue
        prompt = blocks[name]
        print(f"render {name} ({len(prompt)} chars, {args.size})")
        if args.dry_run:
            continue
        try:
            png = call_openai(prompt, api_key=api_key, size=args.size, quality=args.quality)
        except Exception as e:
            print(f"  failed: {e}", file=sys.stderr)
            failed += 1
            continue
        out_path.write_bytes(png)
        print(f"  saved {out_path} ({len(png) // 1024} KB)")
        rendered += 1

    print(f"\ndone. rendered={rendered} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
