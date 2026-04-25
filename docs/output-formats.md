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

- **Default model:** `veo-3.0-fast-generate-001` ($0.10/sec at 720p). Standard `veo-3.0-generate-001` is the fallback when Fast hits its daily quota — same content gates, ~4× the cost. Avoid Veo 3.1 preview models on this tier; they reject all human subjects.
- **Shot durations are quantized to {4, 6, 8} seconds.** The error message says "between 4 and 8 inclusive" but 5- and 7-second shots get rejected. Schoonmaker's cut rhythm must round to one of {4, 6, 8}.
- **Do NOT pass `personGeneration`** — every value (`allow_all`, `allow_adult`, `dont_allow`) is rejected on this tier. Stylized/animated humans render fine without it; photorealistic humans get content-gated separately.
- **Do NOT pass `referenceImages` to the API.** Not supported on `veo-3.0-fast-generate-001`; Veo 3.1 preview accepts the field but rejects the submission anyway. The `ingredient_images` block in the footer is for the Veo Flow UI workflow only — direct-API renders rely on inline character anchoring instead (full character description repeated verbatim in every shot the character appears in).
- **Pacing:** 45–60s between submits to avoid per-minute 429s. Daily/rolling-24h quota tops out around 10–15 calls on tier 1.

### Which persona fills which section

- **CAST:** Ferretti (physical/costume specificity) + writer (names and roles)
- **LOCATIONS:** Ferretti
- **VISUAL GRAMMAR:** Deakins (camera + lens + movement vocabulary)
- **NEGATIVE PROMPT:** Ferretti + director (things that violate director's non-negotiables)
- **SHOT LIST prompts:** director + writer using VISUAL GRAMMAR terms, with Deakins consulting on camera, Ferretti on set/prop detail, Zimmer's audio cues embedded. Each shot prompt MUST include the full character description for every character in frame — Veo cannot use reference images on this tier, so inline anchoring is the continuity mechanism.
- **Durations:** Schoonmaker (cut rhythm determines shot length, **rounded to {4, 6, 8}**)
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
