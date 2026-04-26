# Great Filmmakers — Output Format Specifications

Strict format specs for the three primary artifact types the `/film-crew` command (v1.0) will produce. Downstream pipelines consume these artifacts directly; changes require a major version bump or additive-only edits.

## Overview

| Backend | Primary artifact | Use case | Consumer |
|---------|------------------|----------|----------|
| `heygen` | `film/screenplay/<slug>.heygen.md` | Single-avatar educational / talking-head | `garagedoorscience/.claude/skills/blog-to-video-generation/` |
| `veo3` | `film/screenplay/<slug>.veo3.md` | Multi-character cinematic scenes | `~/Local Sites/veo-builder/app.py` (parses via regex) |
| `remotion` | `film/screenplay/<slug>.remotion.md` | Slideshow fallback with custom photos | `garagedoorscience/remotion/scripts/generate-video-from-blog.ts` |

Plus four supplementary artifacts consumed differently by each backend:

| Artifact | heygen | veo3 | remotion |
|----------|--------|------|----------|
| `film/shot-lists/<slug>.md` | ignored | feeds SHOT LIST section | timing input |
| `film/score-notes/<slug>.md` | ignored | embedded in Veo prompts as audio cues | music_prompt_tags |
| `film/storyboards/<slug>.md` | ignored | feeds CAST + LOCATIONS | asset hints |
| `film/edit-notes/<slug>.md` | director/editor notes | informs SHOT LIST durations | cut points |

---

## HeyGen script format — `film/screenplay/<slug>.heygen.md`

Exact-match format from `garagedoorscience/.claude/skills/blog-to-video-generation/SKILL.md`. Drop-in replacement for `data/heygen-scripts/<slug>.md`.

### Frontmatter (required — existing pipeline reads these fields)

```yaml
---
avatar_group_id: 6b63c5d1884b4be69b1590a6b78280c0
avatar_name: Maya
voice_id: 53c69b4a1aeb44edbce2f050d7a5d3ca
background: "#FFFFFF"
target_duration_seconds: 45
tone: warm, diagnostic, reassuring
slug: garage-door-opener-lifespan
blog_url: https://garagedoorscience.com/blog/garage-door-opener-lifespan
director: scorsese
adapter: kaufman
---
```

The `director` and `adapter` fields are new for this plugin (additive; the existing pipeline's YAML parser should ignore unknown keys). Implementation must verify this assumption before shipping `/film-crew`.

#### Avatar registry (v1.5)

Avatar IDs (`avatar_group_id`, `talking_photo_id`, `voice_id`) are project-spanning configuration, not secrets, but they belong in the canonical secrets file at `~/.config/dev-secrets/secrets.env` so any project can submit videos without hardcoding the IDs. The convention:

- Production-doc frontmatter sets `avatar_name:` (e.g. `Seth`, `Maya`, `Rick`).
- The submit script (`scripts/heygen-submit.py`) resolves `avatar_name` to canonical secret env vars: `$HEYGEN_<NAME>_TALKING_PHOTO_ID` and `$HEYGEN_<NAME>_VOICE_ID`. The name is uppercased, dashes become underscores.
- If the env vars aren't set, the script falls back to `talking_photo_id` and `voice_id` in the doc itself; if those are missing or `TBD`, the script errors with a clear message naming the env var to set.

Example canonical secrets entries:

```bash
HEYGEN_SETH_AVATAR_GROUP_ID=e5ce268666144f26813642a37197de13
HEYGEN_SETH_TALKING_PHOTO_ID=35da87bc92d344efb3e27960521b6788
HEYGEN_SETH_VOICE_ID=6ce72775faf344a9b47224e4393d7b65
```

Production doc frontmatter then becomes minimal:

```yaml
avatar_name: Seth
voice_id: TBD                    # resolved at submit time from $HEYGEN_SETH_VOICE_ID
background: "#1C1C1A"
target_duration_seconds: 50
tone: confident, warm, tour-guide
```

The `voice_id: TBD` placeholder is the convention. The writer (Kaufman/Rhimes) doesn't pick the voice; the registry does.

### Body sections (fixed order)

```markdown
# <Title> — HeyGen Script

## Visual Setup
- **Avatar:** <avatar_name> (<brief direction>)
- **Background:** <background>
- **Aspect Ratio:** 9:16
- **On-screen text:** <what graphics, cards, stats appear>

## Scene Breakdown

### Scene 1 — <name> (0:00–0:08)
**Narration:** "<spoken text>"
**On-screen text:** "<graphic>"
**Director's note:** <one-line hint from the filmmaker — peak shot, pace shift, cut rhythm>

### Scene 2 — <name> (0:08–0:18)
...

## Full Spoken Script (continuous)
<Complete narration, one paragraph per scene, ready for HeyGen Video Agent submission.>
```

### Machine-readable footer

```yaml
## Machine-readable footer

scene_id: <slug>
source_file: <path>
adapter: kaufman | rhimes
director: <filmmaker slug>
avatar: maya | sara | rick | margaret | seth
target_duration_seconds: <int>
scenes:
  - id: scene-1
    name: <name>
    start_sec: <int>
    end_sec: <int>
total_scenes: <int>
voiceover_only: true
```

---

## Veo 3 production doc format — `film/screenplay/<slug>.veo3.md`

Exact-match format parsed by `~/Local Sites/veo-builder/app.py`. Drop into `VEO_SCRIPTS_DIR` for dashboard parsing.

### Required sections (in this order; veo-builder regexes them)

```markdown
# <Title>

<Brief premise paragraph, 2–3 sentences. Human context; not parsed.>

## CAST

**<CHARACTER NAME> (<ABBREV>)**
<Physical description with specific visual tells: hair, clothing, props. Ferretti's voice.>

**<SECOND CHARACTER NAME> (<ABBREV>)**
<...>

## LOCATIONS

**<LOCATION NAME>**
<Spatial description. Ferretti's voice.>

## VISUAL GRAMMAR

**PUSH-IN ON FACE**
<Deakins's definition: lens, framing, motion, when to use.>

**WIDE ESTABLISHING**
<...>

## NEGATIVE PROMPT

```
<Comma-separated list of what NOT to include.>
```

## SHOT LIST

### SHOT 1 — <Shot title>

**Scene type:** <establishing | dialogue | action | reaction | insert | transition>
**Duration:** <e.g., 6 seconds>

```
<Veo 3 prompt. One paragraph. References characters by full description (not abbreviation). Uses VISUAL GRAMMAR terms by name. Ends with audio cues.>
```

### SHOT 2 — <...>

<... repeat for each shot ...>
```

### Machine-readable footer

```yaml
## Machine-readable footer

scene_id: <slug>
source_file: <path>
adapter: kaufman | rhimes
director: <filmmaker slug>
backend: veo3
total_shots: <int>
total_duration_seconds: <int>
characters:
  - abbrev: <abbrev>
    name: <name>
locations:
  - <location_slug>
veo_model: veo-3.0-fast-generate-001
aspect_ratio: 16:9
ingredient_images:
  cast:
    - CAST/<abbrev>.jpg
  locations:
    - LOCATIONS/<location_slug>.jpg
```

### Veo 3 production constraints (Gemini API mldev tier)

These are real, empirically-verified API constraints. Production docs that violate them get rejected at submit time — Schoonmaker, the writer, and `/film-crew` MUST honor all of them.

**Two paths, pick per project:**

#### Path A — Veo 3.0 Fast + inline character anchoring (default, cheapest)

- **Model:** `veo-3.0-fast-generate-001` ($0.10/sec at 720p). Standard `veo-3.0-generate-001` is the fallback when Fast hits its daily quota — same content gates, ~4× the cost.
- **Shot durations are quantized to {4, 6, 8} seconds.** The error message says "between 4 and 8 inclusive" but 5- and 7-second shots get rejected. Schoonmaker's cut rhythm must round to one of {4, 6, 8}.
- **Do NOT pass `personGeneration`** on tier 1 — every value is rejected. On the upgraded tier it's accepted but optional. Stylized/animated humans render fine without it.
- **Do NOT pass `referenceImages`** to Veo 3.0 — explicitly rejected with *"referenceImages isn't supported by this model."* Use inline character anchoring instead: full character description repeated verbatim in every shot the character appears in.
- **Pacing:** 45–60s between submits to avoid per-minute 429s.

#### Path B — Veo 3.1 Fast preview + reference images (stronger continuity)

Available on the upgraded Gemini API tier. Use when character continuity matters more than mixed cut rhythm.

- **Model:** `veo-3.1-fast-generate-preview`.
- **Shot durations:** ALL shots must be `durationSeconds: 8`. 4- and 6-second clips silently reject when reference images are present. Schoonmaker's "round to {4, 6, 8}" rule collapses to "every shot is 8."
- **Aspect ratio:** `aspectRatio: "16:9"` mandatory. Other ratios reject when reference images are present.
- **Up to 3 reference images per shot.** Pass via the `referenceImages` array.
- **Cannot combine `referenceImages` with `image` (init frame) or `lastFrame`.** Pick one continuity mechanism per shot.
- **Request shape (forum-confirmed; the docs page on `ai.google.dev/gemini-api/docs/video` shows an `inlineData` wrapper that the API rejects — don't trust it):**

```json
{
  "instances": [{
    "prompt": "<style anchor + scene + action>",
    "referenceImages": [
      {
        "referenceType": "asset",
        "image": {
          "bytesBase64Encoded": "<base64>",
          "mimeType": "image/jpeg"
        }
      }
    ]
  }],
  "parameters": {
    "aspectRatio": "16:9",
    "resolution": "720p",
    "durationSeconds": 8,
    "sampleCount": 1
  }
}
```

The `ingredient_images` block in the production-doc footer feeds Path B directly when a writer chooses reference images. It also continues to support the Veo Flow UI workflow.

#### Path C — Kling 2.5 Turbo image-to-video (single-clip strength)

Available with a Kling API account (HMAC-signed JWT auth using access+secret keys). Use when one or two cinematic clips need stronger motion physics than Veo's text-to-video, AND the source still can be art-directed in advance.

- **Service:** Kling 2.5 Turbo (`kling-v2-5-turbo`) image-to-video, std mode.
- **Pipeline:** generate a composite still first (Phoenix or gpt-image-2), then animate via Kling.
- **Durations:** 5 or 10 seconds only. Schoonmaker's mixed-rhythm cuts collapse here.
- **Aspect ratios:** 16:9, 9:16, or 1:1.
- **Cost:** ~$1 per 5s clip (std mode).
- **When to choose Kling over Veo:** single cinematic shot with strong motion physics, art-directed source still, no need for multi-shot continuity.
- **When NOT to choose Kling for series work:** image-to-video composes each shot from its own still, so composition drift between shots compounds. The trilogy short re-render via Kling produced figures that read as "grounded in a stage floor" because the Phoenix stills introduced floor surfaces that Veo's text-to-video would have rendered as void. **For multi-shot stylized series work where aesthetic conventions must hold across shots, prefer Veo's text-to-video (Path A or B) over Kling's image-to-video.**

#### Path D — Leonardo Motion 2.0 image-to-video (cheap atmospheric)

Available with a Leonardo API account.

- **Service:** Leonardo Motion 2.0 (`generations-image-to-video`), 720p resolution.
- **Pipeline:** chain Phoenix `imageId` directly into Motion 2.0 (no upload needed; `imageType: "GENERATED"`).
- **Durations:** 5 seconds.
- **Cost:** ~$0.05 per 5s clip — by far the cheapest of the three video-gen services.
- **When to choose Leonardo Motion:** background motion, atmospheric clips, B-roll, anywhere character continuity doesn't matter. Cost floor.
- **When NOT to choose Leonardo Motion:** any shot with character identity that must hold. Motion 2.0 has documented character drift — figures shift unnaturally even when prompted to hold poses. The trilogy multi-character test showed all three figures shifting in unintended ways.

### Choosing between A, B, C, D

| Project shape | Path |
|---------------|------|
| Multi-shot stylized series with character continuity | **A** (Veo 3.0 Fast + inline anchoring) — mixed durations, project-scale composition consistency |
| Stronger character continuity than inline anchoring | **B** (Veo 3.1 Fast preview + reference images) — every shot 8 seconds at 16:9 |
| Single cinematic clip with art-directed still + strong motion physics | **C** (Kling 2.5 Turbo image-to-video) — 5 or 10s, image-to-video grounding |
| Cheap atmospheric B-roll, character continuity not required | **D** (Leonardo Motion 2.0) — $0.05/clip, drift acceptable |

The default for trilogy/series work is **Path A**. Promote to Path B for character-heavy continuity work. Pick Path C for one-off cinematic shots. Pick Path D when cost is the primary constraint.

### Which persona fills which section

- **CAST:** Ferretti (physical/costume specificity) + writer (names and roles)
- **LOCATIONS:** Ferretti
- **VISUAL GRAMMAR:** Deakins (camera + lens + movement vocabulary)
- **NEGATIVE PROMPT:** Ferretti + director (things that violate director's non-negotiables)
- **SHOT LIST prompts:** director + writer using VISUAL GRAMMAR terms, with Deakins consulting on camera, Ferretti on set/prop detail, Zimmer's audio cues embedded. For Path A (Veo 3.0), each shot prompt MUST include the full character description for every character in frame — inline anchoring is the continuity mechanism. For Path B (Veo 3.1 with refs), the prompt may reference characters more loosely ("the man depicted in the first reference image") since the refs do the continuity work.
- **Durations:** Schoonmaker (cut rhythm determines shot length, **rounded to {4, 6, 8}** for Path A, **fixed at 8** for Path B, **5 or 10** for Path C, **5 only** for Path D)
- **Style anchor:** A style preset paragraph is prepended verbatim to every shot prompt. See `docs/style-presets.md` (pen-and-ink editorial is the v1.1 default; future presets: noir, photoreal, Ghibli)

---

## Remotion script format — `film/screenplay/<slug>.remotion.md`

Format matches the existing `garagedoorscience/remotion/scripts/generate-video-from-blog.ts` input shape. TBD details resolved at v1.0 implementation time when the actual pipeline input format is confirmed.

High-level: narration paragraphs + `musicPromptFor()` tags (category + tags) + per-segment timing hints.

### Machine-readable footer

```yaml
scene_id: <slug>
source_file: <path>
backend: remotion
total_duration_seconds: <int>
segments:
  - start_sec: 0
    end_sec: 8
    narration: "<text>"
music_prompt:
  category: <safety | maintenance | buying | fundamentals | ...>
  tags: [<tag>, <tag>]
```

---

## Supplementary artifact formats

### `film/shot-lists/<slug>.md`

Table format. Used by veo3 (feeds SHOT LIST section) and remotion (feeds timing).

```markdown
| # | Shot type         | Duration | Description | B-roll / notes |
|---|-------------------|----------|-------------|----------------|
| 1 | Wide establishing | 3s       | ...         | ...            |
```

Machine-readable footer includes `total_shots`, `total_duration_seconds`, `pipeline_hints.remotion.{frame_rate, total_frames}`.

### `film/score-notes/<slug>.md`

Cue list. Used by veo3 (embedded in Veo prompts as audio cues) and remotion (feeds `musicPromptFor()`).

Machine-readable footer includes `cues[]` array with `id`, `start_sec`, `end_sec`, `mood`, `instrumentation`, `reference_track`, plus top-level `music_prompt_tags`.

### `film/storyboards/<slug>.md`

Ferretti's per-shot production design notes. Used by veo3 (feeds CAST + LOCATIONS) and remotion (asset hints).

Machine-readable footer includes `location`, `period`, `key_props`, `color_palette`, `mood_references`.

### `film/edit-notes/<slug>.md`

Director's notes followed by `---` followed by Schoonmaker's cut notes.

Machine-readable footer includes `director`, `editor`, `pace`, `peak_shot_id`, `voiceover_required`, `cut_points[]`.

---

## Format stability guarantee

v0.1 and v1.0 share this footer schema. Future changes must be additive (new fields) or require a major version bump. Downstream pipelines pin against a specific footer version via the `backend` field's presence and shape.
