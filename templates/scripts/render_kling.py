#!/usr/bin/env python3
"""Kling render script — submit shots from a production doc to the Kling API.

Reads structured shot definitions from a JSON sidecar
(`<docpath>.kling.shots.json`) and submits each shot to the Kling AI API.

Authentication
--------------
Reads KLING_ACCESS_KEY and KLING_SECRET_KEY from the environment.
Never persist these to disk. Never log them. The script will refuse to run
without both set.

    set -a && source ~/.config/dev-secrets/secrets.env && set +a
    python3 scripts/render_kling.py film/screenplay/<slug>.kling.md

Idempotency
-----------
State is persisted at `film/render/kling/_render_state.json`.
Reruns skip already-rendered shots. Failed shots can be retried by
deleting their entry from the state file or by passing `--only <id>`.

Pacing & rate limits
--------------------
Default 30 seconds between submissions to stay under per-minute quota.
Exponential backoff on HTTP 429, starting at 60s, capped at 600s.

Chain conditioning (image-to-image-to-video)
--------------------------------------------
For shots with `chain_from: <prev_shot_id>`, the script extracts the
final frame of the previous shot's MP4 (via ffmpeg) and uses that frame
as the input image — instead of a pre-generated keyframe. This is how a
held descent across multiple shots renders as one continuous take.

Shot sidecar JSON shape
-----------------------
    {
      "model_default": "kling-v2-master",
      "aspect_ratio": "16:9",
      "shots": [
        {
          "id": "A1",
          "duration": 5,
          "prompt": "...",
          "keyframe": "kf-opening-shot.png"   // optional, for image-to-video
        },
        {
          "id": "A2",
          "duration": 5,
          "prompt": "...",
          "chain_from": "A1"                   // optional, chains from prior MP4
        }
      ]
    }

API spec disclaimer
-------------------
The Kling API endpoint paths, model names, and field names below reflect
the spec at the time of authoring. Verify against current Kling docs
before relying on this script in production. Likely areas of drift:
  - Endpoint base URL (api.klingai.com vs regional variants)
  - Model name strings (kling-v2-master vs kling-2.0-master)
  - Field naming in responses (data.task_id vs task_id)

Dependencies
------------
    pip install requests
    # ffmpeg must be on PATH (brew install ffmpeg / apt-get install ffmpeg)
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


KLING_API_BASE = os.environ.get("KLING_API_BASE", "https://api.klingai.com")

DEFAULT_PACING_SECONDS = 30
POLL_INTERVAL_SECONDS = 15
MAX_POLL_ATTEMPTS = 80                # 80 * 15s = 20 min total wait per shot
INITIAL_BACKOFF_SECONDS = 60
MAX_BACKOFF_SECONDS = 600
MAX_RETRIES = 4
JWT_TTL_SECONDS = 1800                # 30 min

# Browser User-Agent for download requests. Some CDNs (notably Leonardo's)
# return 403 to default Python User-Agents; using a browser UA preventatively
# avoids the same trap on Kling's CDN if it changes.
DOWNLOAD_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


# -----------------------------------------------------------------------------
# JWT signing (HS256), stdlib-only — no PyJWT dependency
# -----------------------------------------------------------------------------

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def make_jwt(access_key: str, secret_key: str) -> str:
    """Mint a Kling JWT. Header HS256. Payload iss/exp/nbf."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "iss": access_key,
        "exp": now + JWT_TTL_SECONDS,
        "nbf": now - 5,
    }
    h = _b64url(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{h}.{p}".encode()
    sig = hmac.new(secret_key.encode(), signing_input, hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url(sig)}"


def auth_headers(access: str, secret: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {make_jwt(access, secret)}",
        "Content-Type": "application/json",
    }


# -----------------------------------------------------------------------------
# Credentials and pre-flight
# -----------------------------------------------------------------------------

def get_credentials() -> tuple[str, str]:
    access = os.environ.get("KLING_ACCESS_KEY")
    secret = os.environ.get("KLING_SECRET_KEY")
    if not access or not secret:
        sys.stderr.write(
            "ERROR: KLING_ACCESS_KEY and KLING_SECRET_KEY must be set in env.\n"
            "Source ~/.config/dev-secrets/secrets.env first; do not paste keys on the CLI.\n"
        )
        sys.exit(2)
    return access, secret


def check_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        sys.stderr.write(
            "ERROR: ffmpeg not found on PATH. Required for chain-conditioning frame extraction.\n"
            "Install: brew install ffmpeg  (macOS)  or  apt-get install ffmpeg  (Debian/Ubuntu)\n"
        )
        sys.exit(2)


# -----------------------------------------------------------------------------
# Image helpers
# -----------------------------------------------------------------------------

def encode_image_b64(path: Path) -> str:
    with path.open("rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def extract_last_frame(mp4_path: Path, out_path: Path) -> None:
    """Extract the final frame of an MP4 as a PNG."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-sseof", "-0.1",
        "-i", str(mp4_path),
        "-vframes", "1",
        "-q:v", "2",
        str(out_path),
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed extracting last frame from {mp4_path}: "
            f"{result.stderr.decode('utf-8', errors='replace')}"
        )


# -----------------------------------------------------------------------------
# Kling API client
# -----------------------------------------------------------------------------

def _extract_task_id(response_json: dict[str, Any]) -> str:
    data = response_json.get("data") or response_json
    task_id = data.get("task_id") if isinstance(data, dict) else None
    if not task_id:
        raise RuntimeError(f"No task_id in response: {response_json}")
    return task_id


def submit_image_to_video(
    access: str, secret: str, *,
    image_b64: str, prompt: str, duration: int,
    model: str, aspect_ratio: str,
) -> str:
    url = f"{KLING_API_BASE}/v1/videos/image2video"
    body = {
        "model_name": model,
        "image": image_b64,
        "prompt": prompt,
        "duration": str(duration),
        "aspect_ratio": aspect_ratio,
        "cfg_scale": 0.5,
    }
    r = requests.post(url, headers=auth_headers(access, secret), json=body, timeout=60)
    r.raise_for_status()
    return _extract_task_id(r.json())


def submit_text_to_video(
    access: str, secret: str, *,
    prompt: str, duration: int,
    model: str, aspect_ratio: str,
) -> str:
    url = f"{KLING_API_BASE}/v1/videos/text2video"
    body = {
        "model_name": model,
        "prompt": prompt,
        "duration": str(duration),
        "aspect_ratio": aspect_ratio,
        "cfg_scale": 0.5,
    }
    r = requests.post(url, headers=auth_headers(access, secret), json=body, timeout=60)
    r.raise_for_status()
    return _extract_task_id(r.json())


def poll_task(access: str, secret: str, task_id: str, mode: str) -> str:
    """Poll the task until it completes; return the video URL."""
    endpoint = "image2video" if mode == "image" else "text2video"
    url = f"{KLING_API_BASE}/v1/videos/{endpoint}/{task_id}"

    for _ in range(MAX_POLL_ATTEMPTS):
        time.sleep(POLL_INTERVAL_SECONDS)
        r = requests.get(url, headers=auth_headers(access, secret), timeout=30)
        r.raise_for_status()
        body = r.json()
        task = body.get("data") if isinstance(body.get("data"), dict) else body
        status = task.get("task_status")

        if status == "succeed":
            videos = (task.get("task_result") or {}).get("videos") or []
            if not videos or "url" not in videos[0]:
                raise RuntimeError(f"Task succeeded but no video URL: {body}")
            return videos[0]["url"]
        if status == "failed":
            reason = task.get("task_status_msg") or "unknown"
            raise RuntimeError(f"Task failed: {reason}")
        # else: processing/submitted — keep polling

    raise TimeoutError(
        f"Task {task_id} did not complete within "
        f"{MAX_POLL_ATTEMPTS * POLL_INTERVAL_SECONDS}s"
    )


def download_video(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": DOWNLOAD_USER_AGENT}
    with requests.get(url, stream=True, timeout=300, headers=headers) as r:
        r.raise_for_status()
        with out_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=64 * 1024):
                if chunk:
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
# Main render loop
# -----------------------------------------------------------------------------

def render_shot(
    access: str, secret: str, *,
    shot: dict[str, Any],
    project_root: Path,
    state: dict[str, Any],
    model_default: str,
    aspect_ratio: str,
) -> dict[str, Any]:
    shot_id = shot["id"]

    if state.get(shot_id, {}).get("status") == "complete":
        print(f"[{shot_id}] already complete — skipping")
        return state[shot_id]

    duration = int(shot["duration"])
    model = shot.get("model", model_default)
    print(f"[{shot_id}] rendering ({duration}s, model={model})")

    image_b64: str | None = None
    if shot.get("chain_from"):
        prev_id = shot["chain_from"]
        prev_mp4 = project_root / "film" / "render" / "kling" / f"{prev_id}.mp4"
        if not prev_mp4.exists():
            raise RuntimeError(
                f"chain_from={prev_id} requires {prev_mp4} which does not exist; "
                f"render {prev_id} first"
            )
        last_frame_path = (
            project_root / "film" / "render" / "kling" / "_chain_frames" /
            f"{prev_id}_last.png"
        )
        extract_last_frame(prev_mp4, last_frame_path)
        image_b64 = encode_image_b64(last_frame_path)
    elif shot.get("keyframe"):
        kf_path = (
            project_root / "film" / "render" / "kling" / "keyframes" /
            shot["keyframe"]
        )
        if not kf_path.exists():
            raise RuntimeError(f"Keyframe missing: {kf_path}")
        image_b64 = encode_image_b64(kf_path)

    mode = shot.get("mode") or ("image" if image_b64 else "text")

    backoff = INITIAL_BACKOFF_SECONDS
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if mode == "image" and image_b64:
                task_id = submit_image_to_video(
                    access, secret,
                    image_b64=image_b64,
                    prompt=shot["prompt"],
                    duration=duration,
                    model=model,
                    aspect_ratio=aspect_ratio,
                )
            else:
                task_id = submit_text_to_video(
                    access, secret,
                    prompt=shot["prompt"],
                    duration=duration,
                    model=model,
                    aspect_ratio=aspect_ratio,
                )
            print(f"[{shot_id}] submitted task_id={task_id}")
            break
        except requests.HTTPError as e:
            last_error = e
            if e.response is not None and e.response.status_code == 429:
                print(
                    f"[{shot_id}] HTTP 429 (rate limited); backing off {backoff}s "
                    f"(attempt {attempt}/{MAX_RETRIES})"
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF_SECONDS)
                continue
            raise
    else:
        raise RuntimeError(
            f"failed to submit {shot_id} after {MAX_RETRIES} retries: {last_error}"
        )

    video_url = poll_task(access, secret, task_id, mode)
    print(f"[{shot_id}] complete; downloading...")

    out_path = project_root / "film" / "render" / "kling" / f"{shot_id}.mp4"
    download_video(video_url, out_path)
    print(f"[{shot_id}] saved to {out_path.relative_to(project_root)}")

    return {
        "status": "complete",
        "task_id": task_id,
        "duration": duration,
        "mode": mode,
        "model": model,
        "rendered_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "output": str(out_path.relative_to(project_root)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Kling shots from a production doc.")
    parser.add_argument("doc", help="Path to .kling.md (script reads sidecar .kling.shots.json)")
    parser.add_argument("--pace", type=int, default=DEFAULT_PACING_SECONDS,
                        help="Seconds between submissions (default 30)")
    parser.add_argument("--only", help="Comma-separated shot IDs (default: all pending)")
    args = parser.parse_args()

    doc_path = Path(args.doc).resolve()
    if not doc_path.exists():
        sys.stderr.write(f"ERROR: doc not found: {doc_path}\n")
        return 1

    # <name>.kling.md  ->  <name>.kling.shots.json
    if doc_path.name.endswith(".kling.md"):
        shots_path = doc_path.with_name(doc_path.name.replace(".kling.md", ".kling.shots.json"))
    else:
        shots_path = doc_path.with_suffix(".shots.json")

    if not shots_path.exists():
        sys.stderr.write(f"ERROR: shots sidecar not found: {shots_path}\n")
        return 1

    # Walk up from film/screenplay/<doc> -> project root
    project_root = doc_path.parents[2]
    print(f"Project root: {project_root}")

    config = json.loads(shots_path.read_text())
    shots = config["shots"]
    if not shots:
        sys.stderr.write(
            f"ERROR: no shots found in {shots_path}. Check that the JSON sidecar's "
            f"'shots' array is populated.\n"
        )
        return 1
    model_default = config.get("model_default", "kling-v2-master")
    aspect_ratio = config.get("aspect_ratio", "16:9")

    state_path = project_root / "film" / "render" / "kling" / "_render_state.json"
    state = load_state(state_path)

    only = set(args.only.split(",")) if args.only else None
    access, secret = get_credentials()
    check_ffmpeg()

    submitted_count = 0
    for shot in shots:
        if only and shot["id"] not in only:
            continue
        # Check completion BEFORE pacing sleep — otherwise re-runs sleep
        # the full --pace interval per already-complete shot.
        if state.get(shot["id"], {}).get("status") == "complete":
            print(f"[{shot['id']}] already complete — skipping")
            continue
        if submitted_count > 0:
            time.sleep(args.pace)
        try:
            shot_state = render_shot(
                access, secret,
                shot=shot,
                project_root=project_root,
                state=state,
                model_default=model_default,
                aspect_ratio=aspect_ratio,
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
    print(f"State: {state_path.relative_to(project_root)}")
    print("Re-run to retry failed shots; completed shots are skipped automatically.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
