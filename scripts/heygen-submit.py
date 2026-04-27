#!/usr/bin/env python3
"""Submit a HeyGen production doc to HeyGen v2 REST API.

Reads a `.heygen.md` production doc (the great-filmmakers `/filmmakers-crew --backend heygen`
output format), extracts the spoken script, resolves avatar/voice IDs from canonical
secrets, submits to HeyGen, polls for completion, and downloads the MP4.

USAGE
-----

    set -a && source ~/.config/dev-secrets/secrets.env && set +a
    python3 scripts/heygen-submit.py film/screenplay/<slug>.heygen.md [--out OUTPUT.mp4]

REQUIRED ENV
------------

    HEYGEN_API_KEY                    # HeyGen API key (sk_V2_...)
    HEYGEN_<AVATAR>_TALKING_PHOTO_ID  # e.g. HEYGEN_SETH_TALKING_PHOTO_ID
    HEYGEN_<AVATAR>_VOICE_ID          # e.g. HEYGEN_SETH_VOICE_ID

The avatar name is resolved from the production doc's `avatar_name:` frontmatter
field (uppercased, dashes → underscores). e.g. `avatar_name: Seth` resolves to
$HEYGEN_SETH_TALKING_PHOTO_ID and $HEYGEN_SETH_VOICE_ID.

If the env vars aren't set, the script falls back to using `talking_photo_id`
and `voice_id` from the production doc footer if present, then to whatever
the production doc's frontmatter contains, then errors.

NOTES
-----

- HeyGen's API tier credits are separate from web-app credits. If submission
  rejects with `MOVIO_PAYMENT_INSUFFICIENT_CREDIT`, fund the API tier at
  https://app.heygen.com/settings?nav=API.
- The HeyGen v2 API uses `talking_photo` for cloned avatars from photo+voice
  clones, and `avatar` for default-library avatars. This script defaults to
  `talking_photo` since that's the typical great-filmmakers use case.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path


def parse_doc(path):
    """Extract avatar_name, voice_id, background, and the full spoken script."""
    text = path.read_text()

    # Frontmatter (YAML between --- markers at top)
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    fm = {}
    if fm_match:
        for line in fm_match.group(1).split("\n"):
            if ":" in line and not line.strip().startswith("#"):
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()

    # Spoken script (between "## Full Spoken Script" and the next h2 or footer)
    script_start = text.find("## Full Spoken Script")
    if script_start == -1:
        raise ValueError(f"No '## Full Spoken Script' section in {path}")
    after = text[script_start:].split("\n", 2)[2]
    # Stop at the next h2 OR the word-count line OR the YAML footer fence
    stop_patterns = [r"\n## ", r"\n\*\*Word count", r"\n```yaml"]
    end = len(after)
    for pat in stop_patterns:
        m = re.search(pat, after)
        if m and m.start() < end:
            end = m.start()
    spoken = after[:end].strip()
    # Drop any "---" separators
    spoken = re.sub(r"\n---\n", "\n\n", spoken).strip()

    return fm, spoken


def resolve_ids(fm):
    """Resolve talking_photo_id and voice_id from canonical secrets, then fall back to frontmatter."""
    avatar_name = fm.get("avatar_name", "").strip()
    if not avatar_name:
        raise ValueError("avatar_name missing from frontmatter")
    env_prefix = f"HEYGEN_{avatar_name.upper().replace('-', '_')}"
    talking_photo_id = (
        os.environ.get(f"{env_prefix}_TALKING_PHOTO_ID")
        or fm.get("talking_photo_id")
        or fm.get("avatar_id")
    )
    voice_id = os.environ.get(f"{env_prefix}_VOICE_ID") or fm.get("voice_id")
    if voice_id == "TBD":
        voice_id = None
    if not talking_photo_id:
        raise ValueError(
            f"No talking_photo_id resolved. Set ${env_prefix}_TALKING_PHOTO_ID in "
            f"~/.config/dev-secrets/secrets.env or add `talking_photo_id:` to the doc."
        )
    if not voice_id:
        raise ValueError(
            f"No voice_id resolved. Set ${env_prefix}_VOICE_ID in canonical secrets "
            f"or add a real `voice_id:` to the doc (currently TBD)."
        )
    return talking_photo_id, voice_id


def submit(api_key, talking_photo_id, voice_id, spoken_text, title):
    """Submit via HeyGen Direct Video v3 API (POST /v3/videos).

    Uses the `script` field for verbatim text-to-speech — the avatar speaks
    exactly what we send, no rewriting. This is the right endpoint for
    Kaufman-tight scripts where every word is intentional.

    The /v3/video-agents endpoint is NOT used here: it always rewrites prompts
    into its own script and ignores verbatim instructions. /v3/videos is the
    documented path "for precise script control".

    `avatar_id` accepts both regular avatar IDs and talking_photo (photo-clone)
    avatar look IDs — the API treats them as a single discriminated type.
    """
    body = {
        "type": "avatar",
        "avatar_id": talking_photo_id,
        "title": title,
        "script": spoken_text,
        "voice_id": voice_id,
        "aspect_ratio": "9:16",
    }
    req = urllib.request.Request(
        "https://api.heygen.com/v3/videos",
        data=json.dumps(body).encode(),
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        result = json.loads(r.read())
    data = result.get("data") or result
    video_id = data.get("video_id") or data.get("id")
    if not video_id:
        raise RuntimeError(f"Unexpected response: {json.dumps(result)[:400]}")
    return video_id


def poll(api_key, video_id, timeout_sec=600):
    poll_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    deadline = time.time() + timeout_sec
    last_status = None
    while time.time() < deadline:
        time.sleep(15)
        req = urllib.request.Request(
            poll_url, headers={"X-Api-Key": api_key}, method="GET"
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
        except Exception as e:
            print(f"   poll error: {e}", file=sys.stderr)
            continue
        status = data.get("data", {}).get("status")
        if status != last_status:
            print(f"   status: {status}")
            last_status = status
        if status == "completed":
            return data["data"]["video_url"]
        if status == "failed":
            err = data.get("data", {}).get("error", {})
            code = err.get("code", "?")
            detail = err.get("detail", err.get("message", ""))
            if code == "MOVIO_PAYMENT_INSUFFICIENT_CREDIT":
                raise RuntimeError(
                    "HeyGen API credit insufficient. The API tier credit is separate "
                    "from web-app credits. Fund at https://app.heygen.com/settings?nav=API"
                )
            raise RuntimeError(f"HeyGen render failed: {code} — {detail}")
    raise TimeoutError(f"HeyGen poll timed out after {timeout_sec}s")


def download(url, out_path):
    with urllib.request.urlopen(url, timeout=180) as r:
        out_path.write_bytes(r.read())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("doc", help="Path to the .heygen.md production doc")
    p.add_argument("--out", help="Output MP4 path (default: same dir as doc)")
    args = p.parse_args()

    api_key = os.environ.get("HEYGEN_API_KEY")
    if not api_key:
        print(
            "ERROR: HEYGEN_API_KEY not set. Run:\n"
            "  set -a && source ~/.config/dev-secrets/secrets.env && set +a",
            file=sys.stderr,
        )
        sys.exit(2)

    doc = Path(args.doc).expanduser().resolve()
    out = Path(args.out) if args.out else doc.with_suffix(".mp4")
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"→ parsing {doc}")
    fm, spoken = parse_doc(doc)
    talking_photo_id, voice_id = resolve_ids(fm)
    title = fm.get("title", "").strip().strip('"') or doc.stem
    word_count = len(spoken.split())
    print(f"   avatar:    {fm.get('avatar_name')} ({talking_photo_id[:12]}...)")
    print(f"   voice:     {voice_id[:12]}...")
    print(f"   words:     {word_count}")
    print(f"   ~duration: {word_count / 165 * 60:.0f}s @ 165 WPM")

    print(f"\n→ submitting to HeyGen v3/videos (verbatim script)")
    try:
        video_id = submit(api_key, talking_photo_id, voice_id, spoken, title)
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        print(f"   ❌ HTTP {e.code}: {msg[:500]}", file=sys.stderr)
        sys.exit(1)
    print(f"   video_id:  {video_id}")

    print(f"\n→ polling")
    try:
        video_url = poll(api_key, video_id)
    except Exception as e:
        print(f"   ❌ {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n→ downloading to {out}")
    download(video_url, out)
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"   ✅ {out} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
