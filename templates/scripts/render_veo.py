#!/usr/bin/env python3
"""Veo 3 render script — submit shots from a .veo3.md production doc.

Parses a `<slug>.veo3.md` production doc, extracts per-shot prompts and
durations, and submits each shot to the Gemini Veo API. Mirrors the
interface of `scripts/render_kling.py` so the two renderers can be
operated identically.

Authentication
--------------
Reads GEMINI_API_KEY (or GOOGLE_API_KEY) from the environment. Source
from canonical secrets:

    set -a && source ~/.config/dev-secrets/secrets.env && set +a
    python3 scripts/render_veo.py film/screenplay/<slug>.veo3.md

Idempotency
-----------
State is persisted at `film/render/veo/_render_state.json`.
Reruns skip already-rendered shots. Failed shots can be retried by
deleting their entry from the state file or by passing `--only <id>`.

API constraints (Veo 3.0 Fast on Gemini API mldev tier)
-------------------------------------------------------
- Durations quantized to {4, 6, 8}. Shots specifying 5/7/10/12 are
  rounded down to the nearest legal value at parse time.
- aspectRatio: "16:9".
- Do NOT pass personGeneration on tier 1 (it is rejected).
- Do NOT pass referenceImages to veo-3.0-fast (it is rejected).
- Pacing: 60 seconds between submissions to stay under per-minute quota.
- Cost: $0.10/sec at 720p.

Production doc format
---------------------
The script expects:

    ## Style anchor
    ```
    <style anchor block — prepended to every shot prompt>
    ```

    ### Shot A1 — 6 seconds
    **Prompt:**
    ```
    [STYLE ANCHOR — applied automatically]

    <shot-specific prompt>
    ```
    **Negations:** no text overlays, no rapid cuts.

    ### Shot A2 — 8 seconds
    ...

The `[STYLE ANCHOR ...]` placeholder line is stripped; the actual style
anchor block is prepended to every shot prompt.

Run
---
    python3 scripts/render_veo.py film/screenplay/<slug>.veo3.md
    python3 scripts/render_veo.py film/screenplay/<slug>.veo3.md --only A1,A2
    python3 scripts/render_veo.py film/screenplay/<slug>.veo3.md --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_BASE = os.environ.get("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta")
DEFAULT_MODEL = "veo-3.0-fast-generate-001"
DEFAULT_PACING_SECONDS = 60
POLL_INTERVAL_SECONDS = 15
MAX_POLL_ATTEMPTS = 80                # 80 * 15s = 20 min total wait per shot
LEGAL_DURATIONS = (4, 6, 8)

# Browser User-Agent for download requests. Some CDNs (notably Leonardo's)
# return 403 to default Python urllib User-Agents; using a browser UA
# preventatively avoids the same trap on any future CDN. Set on every
# download request, even where the API doesn't require it.
DOWNLOAD_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Genres for which Veo is likely to refuse body/death/violence-adjacent prompts.
# Used by the --check-content-policy pre-flight scanner. Read from
# .great-authors/project.md's `## Genre` section.
CONTENT_POLICY_GENRES = ("mystery", "crime", "thriller", "noir", "horror", "war")

# Keywords that frequently trigger Veo's content-policy refusal in crime fiction.
# The scanner does substring (case-insensitive) matching on the shot prompt.
# Not exhaustive — Veo's actual policy is opaque. Used as a heuristic to surface
# RISK before submission, not to guarantee acceptance/refusal.
CONTENT_POLICY_KEYWORDS = (
    # Bodies and death
    "body", "corpse", "dead", "death", "murder", "killed", "kill", "killer",
    "victim", "wound", "blood", "bleeding", "bullet", "stabbed",
    # Violence and weapons
    "weapon", "gun", "knife", "rifle", "pistol", "violent", "violence",
    "attack", "assault", "strangled", "choking",
    # Body parts in distress register
    "throat", "chest wound", "head wound",
)


def read_project_genre(project_root: Path) -> str | None:
    """Return the genre field from .great-authors/project.md, lowercased."""
    bible_path = project_root / ".great-authors" / "project.md"
    if not bible_path.exists():
        return None
    text = bible_path.read_text()
    # Look for `## Genre` heading followed by the next non-empty line.
    match = re.search(r"^##\s+Genre\s*\n+([^\n#]+)", text, re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip().lower()


def check_content_policy(
    shots: list[dict[str, Any]], project_root: Path,
) -> list[dict[str, Any]]:
    """Pre-flight scanner — return list of shots flagged as refusal-prone.

    Reads project genre from .great-authors/project.md. If genre is in
    CONTENT_POLICY_GENRES, scans each shot prompt for keywords in
    CONTENT_POLICY_KEYWORDS. Returns one entry per shot with at least one
    matched keyword.

    Heuristic — Veo's content policy is opaque and changes. The scanner
    surfaces risk before submission so the user doesn't burn quota on
    prompts that will refuse mid-pipeline.
    """
    genre = read_project_genre(project_root)
    if not genre:
        print("⚠️  No project genre found at .great-authors/project.md — skipping content-policy scan.")
        return []
    if not any(g in genre for g in CONTENT_POLICY_GENRES):
        print(f"   project genre is '{genre}' — content-policy scan not applicable.")
        return []

    print(f"   project genre is '{genre}' — scanning shots for refusal-prone prompts.")
    flagged: list[dict[str, Any]] = []
    for shot in shots:
        prompt_lower = shot["prompt"].lower()
        matched = [kw for kw in CONTENT_POLICY_KEYWORDS if kw in prompt_lower]
        if matched:
            flagged.append({
                "id": shot["id"],
                "matched_keywords": matched,
                "prompt_preview": shot["prompt"][:150],
            })
    return flagged


def get_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.stderr.write(
            "ERROR: GEMINI_API_KEY (or GOOGLE_API_KEY) must be set in env.\n"
            "Source ~/.config/dev-secrets/secrets.env first.\n"
        )
        sys.exit(2)
    return key


# -----------------------------------------------------------------------------
# Doc parsing
# -----------------------------------------------------------------------------

STYLE_ANCHOR_RE = re.compile(
    r"^## Style anchor.*?\n```\s*\n(.*?)\n```",
    re.DOTALL | re.MULTILINE,
)
SHOT_HEADING_RE = re.compile(
    r"^### Shot ([A-Za-z0-9]+) — (\d+)\s*seconds.*$",
    re.MULTILINE,
)
PROMPT_BLOCK_RE = re.compile(r"\*\*Prompt:\*\*\s*\n```\s*\n(.*?)\n```", re.DOTALL)
NEGATIONS_RE = re.compile(r"\*\*Negations:\*\*\s*(.*?)(?:\n\n|\Z)", re.DOTALL)
ANCHOR_PLACEHOLDER_RE = re.compile(r"\[STYLE ANCHOR[^\]]*\]\s*", re.IGNORECASE)


def quantize_duration(seconds: int) -> int:
    """Round down to nearest legal Veo duration in {4, 6, 8}."""
    if seconds >= 8:
        return 8
    if seconds >= 6:
        return 6
    return 4


def parse_doc(text: str) -> tuple[str, list[dict[str, Any]]]:
    """Return (style_anchor, shots[]) parsed from veo3.md text."""
    anchor_match = STYLE_ANCHOR_RE.search(text)
    if not anchor_match:
        raise ValueError("Could not find ## Style anchor block in veo3 doc")
    style_anchor = anchor_match.group(1).strip()

    shots: list[dict[str, Any]] = []
    headings = list(SHOT_HEADING_RE.finditer(text))
    for i, m in enumerate(headings):
        shot_id = m.group(1)
        declared_duration = int(m.group(2))
        block_start = m.end()
        block_end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[block_start:block_end]

        prompt_match = PROMPT_BLOCK_RE.search(block)
        if not prompt_match:
            raise ValueError(f"Shot {shot_id}: no Prompt code block found")
        raw_prompt = prompt_match.group(1).strip()
        prompt = ANCHOR_PLACEHOLDER_RE.sub("", raw_prompt).strip()
        if not raw_prompt.startswith(style_anchor):
            prompt = f"{style_anchor}\n\n{prompt}"

        neg_match = NEGATIONS_RE.search(block)
        if neg_match:
            negations = neg_match.group(1).strip().rstrip(".")
            prompt = f"{prompt}\n\nAvoid: {negations}."

        shots.append({
            "id": shot_id,
            "duration": quantize_duration(declared_duration),
            "declared_duration": declared_duration,
            "prompt": prompt,
        })
    return style_anchor, shots


# -----------------------------------------------------------------------------
# Gemini Veo API client (urllib, no extra deps)
# -----------------------------------------------------------------------------

def _post(url: str, *, body: dict[str, Any], api_key: str, timeout: int = 60) -> dict[str, Any]:
    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} on POST {url}: {detail}") from None


def _get(url: str, *, api_key: str, timeout: int = 60) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={"x-goog-api-key": api_key},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} on GET {url}: {detail}") from None


def submit_shot(api_key: str, *, prompt: str, duration: int, model: str = DEFAULT_MODEL) -> str:
    """Submit a Veo generation request. Return the operation name."""
    url = f"{API_BASE}/models/{model}:predictLongRunning"
    body = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": "16:9",
            "durationSeconds": duration,
            "sampleCount": 1,
        },
    }
    resp = _post(url, body=body, api_key=api_key, timeout=120)
    op_name = resp.get("name")
    if not op_name:
        raise RuntimeError(f"No operation name in response: {resp}")
    return op_name


def poll_operation(api_key: str, op_name: str) -> dict[str, Any]:
    """Poll an LRO until done; return the final operation dict."""
    url = f"{API_BASE}/{op_name}"
    for _ in range(MAX_POLL_ATTEMPTS):
        time.sleep(POLL_INTERVAL_SECONDS)
        op = _get(url, api_key=api_key, timeout=30)
        if op.get("done"):
            if "error" in op:
                err = op["error"]
                raise RuntimeError(f"Operation failed: code={err.get('code')} msg={err.get('message')}")
            return op
    raise TimeoutError(
        f"Operation {op_name} did not complete within "
        f"{MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS}s"
    )


def extract_video_uri(op: dict[str, Any]) -> str:
    """Pull the generated-video URI out of a completed operation."""
    response = op.get("response", {})
    samples = (
        response.get("generateVideoResponse", {}).get("generatedSamples")
        or response.get("predictResponse", {}).get("generatedSamples")
        or response.get("generatedSamples")
        or []
    )
    if samples:
        video = samples[0].get("video") or {}
        uri = video.get("uri") or video.get("videoUri")
        if uri:
            return uri
    raise RuntimeError(f"No video URI in operation response: {op}")


def download_video(uri: str, out_path: Path, *, api_key: str) -> None:
    sep = "&" if "?" in uri else "?"
    url = f"{uri}{sep}key={urllib.parse.quote(api_key)}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": DOWNLOAD_USER_AGENT})
    with urllib.request.urlopen(req, timeout=300) as resp, out_path.open("wb") as f:
        while True:
            chunk = resp.read(64 * 1024)
            if not chunk:
                break
            f.write(chunk)


# -----------------------------------------------------------------------------
# State
# -----------------------------------------------------------------------------

def load_state(state_path: Path) -> dict[str, Any]:
    if state_path.exists():
        try:
            return json.loads(state_path.read_text())
        except json.JSONDecodeError:
            sys.stderr.write(f"WARN: state file at {state_path} is corrupt; starting fresh\n")
    return {}


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_suffix(state_path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.replace(state_path)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def render_shot(
    api_key: str, *,
    shot: dict[str, Any],
    out_dir: Path,
    project_root: Path,
) -> dict[str, Any]:
    shot_id = shot["id"]
    duration = shot["duration"]
    print(f"[{shot_id}] submitting ({duration}s, {len(shot['prompt'])} chars)")
    op_name = submit_shot(api_key, prompt=shot["prompt"], duration=duration)
    print(f"[{shot_id}] operation={op_name}")
    op = poll_operation(api_key, op_name)
    uri = extract_video_uri(op)
    out_path = out_dir / f"{shot_id}.mp4"
    download_video(uri, out_path, api_key=api_key)
    # When --out-dir points outside the project, relative_to() raises;
    # fall back to the absolute path so we don't crash post-download.
    try:
        display_path = out_path.relative_to(project_root)
    except ValueError:
        display_path = out_path
    print(f"[{shot_id}] saved {display_path}")
    return {
        "status": "complete",
        "operation": op_name,
        "duration": duration,
        "rendered_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "output": str(display_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Veo shots from a .veo3.md production doc.")
    parser.add_argument("doc", help="Path to .veo3.md")
    parser.add_argument("--pace", type=int, default=DEFAULT_PACING_SECONDS,
                        help="Seconds between submissions (default 60)")
    parser.add_argument("--only", help="Comma-separated shot IDs (default: all pending)")
    parser.add_argument("--out-dir",
                        help="Output directory for rendered MP4s (default: <project>/film/render/veo/)")
    parser.add_argument("--state-file",
                        help="Render-state JSON path (default: <out-dir>/_render_state.json)")
    parser.add_argument("--dry-run", action="store_true", help="Parse doc, do not call API")
    parser.add_argument(
        "--check-content-policy",
        choices=["off", "warn", "strict"],
        default="warn",
        help=(
            "Pre-flight content-policy scan (default: warn). "
            "off = no scan. "
            "warn = scan, list flagged shots, prompt user to continue. "
            "strict = scan, abort if any shot is flagged."
        ),
    )
    args = parser.parse_args()

    doc_path = Path(args.doc).resolve()
    if not doc_path.exists():
        sys.stderr.write(f"ERROR: doc not found: {doc_path}\n")
        return 1

    project_root = doc_path.parents[2]
    out_dir = Path(args.out_dir).resolve() if args.out_dir else (project_root / "film" / "render" / "veo")
    state_path = (
        Path(args.state_file).resolve() if args.state_file
        else (out_dir / "_render_state.json")
    )

    text = doc_path.read_text()
    style_anchor, shots = parse_doc(text)
    print(f"Project root: {project_root}")
    print(f"Output dir:   {out_dir}")
    print(f"Style anchor: {len(style_anchor)} chars")
    print(f"Shots parsed: {len(shots)}")
    if not shots:
        sys.stderr.write(
            f"ERROR: no shots parsed from {doc_path}. Expected '### Shot <ID> — <N> seconds' "
            f"headings (note: em dash —, not hyphen -). Check the production doc format.\n"
        )
        return 1
    for s in shots:
        flag = "" if s["duration"] == s["declared_duration"] else f" (was {s['declared_duration']}s)"
        print(f"  {s['id']:4}  {s['duration']}s{flag}  prompt={len(s['prompt'])} chars")

    if args.dry_run:
        return 0

    # Pre-flight content-policy scan (item #9 from trilogy improvements).
    if args.check_content_policy != "off":
        print()
        print("→ content-policy pre-flight scan")
        flagged = check_content_policy(shots, project_root)
        if flagged:
            print(f"   ⚠️  {len(flagged)} shot(s) contain refusal-prone keywords:")
            for f in flagged:
                kws = ", ".join(f["matched_keywords"])
                print(f"     [{f['id']}] keywords: {kws}")
                print(f"           preview: {f['prompt_preview']}...")
            print()
            print(
                "   Veo refuses many body/violence-adjacent prompts in crime fiction.\n"
                "   Recommendations:\n"
                "   - Sanitize the prompts (drop the keyword; describe consequence rather than action)\n"
                "   - Use Kling for these shots (kling-side scripts are more permissive on stylized content)\n"
                "   - Run this script with --check-content-policy=off to bypass this check entirely"
            )
            if args.check_content_policy == "strict":
                sys.stderr.write("\nERROR: --check-content-policy=strict — aborting before submission.\n")
                return 3
            try:
                response = input("   Continue with submission anyway? [y/N]: ").strip().lower()
            except EOFError:
                response = ""
            if response not in ("y", "yes"):
                print("   Aborted.")
                return 0

    api_key = get_api_key()
    state = load_state(state_path)
    only = set(args.only.split(",")) if args.only else None

    submitted_count = 0
    for shot in shots:
        if only and shot["id"] not in only:
            continue
        if state.get(shot["id"], {}).get("status") == "complete":
            print(f"[{shot['id']}] already complete — skipping")
            continue
        if submitted_count > 0:
            time.sleep(args.pace)
        try:
            shot_state = render_shot(
                api_key, shot=shot, out_dir=out_dir, project_root=project_root,
            )
            state[shot["id"]] = shot_state
            save_state(state_path, state)
            if shot_state.get("status") == "complete":
                submitted_count += 1
        except Exception as e:
            sys.stderr.write(f"[{shot['id']}] ERROR: {e}\n")
            state[shot["id"]] = {
                "status": "error",
                "error": str(e),
                "at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
            save_state(state_path, state)

    print()
    print("Render pass complete.")
    print(f"State: {state_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
