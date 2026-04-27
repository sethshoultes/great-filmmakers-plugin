# Great Filmmakers — Output Format Specifications

Strict format specs for the three primary artifact types the `/filmmakers-crew` command (v1.0) will produce. Downstream pipelines consume these artifacts directly; changes require a major version bump or additive-only edits.

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

The `director` and `adapter` fields are new for this plugin (additive; the existing pipeline's YAML parser should ignore unknown keys). Implementation must verify this assumption before shipping `/filmmakers-crew`.

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

These are real, empirically-verified API constraints. Production docs that violate them get rejected at submit time — Schoonmaker, the writer, and `/filmmakers-crew` MUST honor all of them.

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

## Image-generation prompt format (v1.7+)

### `<dir>/PROMPTS.md`

Produced by `/filmmakers-build-keyframes`. Read by `scripts/render_keyframes.py` (which renders both video keyframes and book illustrations from the same PROMPTS.md format) and downstream by `scripts/wire_book_illustrations.py` (which places rendered PNGs into Astro chapter MDX). Both are project-level scripts, copied in from `templates/scripts/`.

Used for: book illustrations (chapter inline placement, MDX), video keyframes (image-to-video conditioning), cover concept briefs.

### Required structure

```markdown
# <Source title> — Illustration Prompts

<One paragraph naming what these illustrations carry. The director's editorial judgment about the source — which moments, what register, why these and not others.>

---

### <chapter-or-prefix>-<scene-slug>.png

**Style anchor (verbatim, prepend to every prompt):**
<style anchor block — exact text from style preset or visual-lints.md; the line must repeat verbatim across every block in the file>

**Composition:** <The frame.>

**Subject:** <Who/what is in the frame, with continuity locks honored.>

**Light:** <The lighting register.>

**Production design:** <Materials, period, props, setting.>

**Negative prompt (must NOT appear):** <Forbidden elements — visual-lints.md baseline + cue-specific refusals.>

**Aspect ratio:** <16:9 / 3:2 / 4:3 — director chooses per cue>
**Format:** PNG

[Optional, when --include-prose-anchors:]
**Prose anchor:** "<50-150 char prose snippet from the source, immediately preceding this cue point — used by wire_book_illustrations.py to place the illustration in MDX>"

---

### <next slug>.png

[same structure]
```

### Slug convention (canonical, v1.8+)

**Single naming convention across all PROMPTS.md files in the constellation:** `<prefix>-<scene-slug>`.

The prefix names the role or location of the cue point; the scene-slug names the specific moment. Together they produce a unique, sortable, render-script-safe filename.

**Common prefixes:**

| Prefix | Use case | Example slugs |
|---|---|---|
| `ch01`, `ch02`, … | Chapter illustrations (per-chapter, in-line) | `ch01-hands-folding`, `ch02-compound-gate` |
| `kf` | Keyframes for image-to-video conditioning | `kf-truck-departing`, `kf-figure-walking` |
| `cover` | Cover concept stills | `cover-hero`, `cover-back` |
| `social` | Social-promo stills derived from the same source | `social-square-1`, `social-vertical-2` |
| `<custom>` | Project-specific (named in the brief) | `prologue-roadside`, `epilogue-cemetery` |

**The regex that matches all of them:**

```
### ([a-z][a-z0-9_\-]*)\.png
```

This regex appears in `render_keyframes.py` and `wire_book_illustrations.py` (templated as of great-filmmakers v1.8). One pattern, one render script per backend, no per-project regex divergence.

**Why this matters:** earlier projects produced `### kf-<name>.png` for chapter-1 and `### ch<NN>-<name>.png` for chapters 2-N, and the divergence required two different render scripts and two different regexes. The single naming convention lets one regex handle both chapter keyframes (image-to-video) and book illustrations (chapter inline). The render script doesn't need to know whether a slug is `kf-*` or `ch01-*` — it just iterates matched blocks.

**Naming guidance for `/filmmakers-build-keyframes`:**

When the source file's name signals a chapter (e.g., `chapter-01-yellow-knolls.md`), use the `chNN-` prefix. When it signals video keyframes (the `--out-dir` is a `keyframes/` directory or `--style-preset` indicates video), use the `kf-` prefix. When the use case is cover or marketing visual, use the explicit prefix (`cover-`, `social-`). The director persona makes this choice; the orchestrator may override via the brief.

### Style anchor handling

The style anchor is the verbatim opening of every render prompt. Sources, in priority order:

1. `--style-preset <slug>` argument to `/filmmakers-build-keyframes`
2. `.great-authors/project.md`'s `## Visual` section's `Style anchor (verbatim)` field (great-authors v1.5+)
3. `docs/style-presets.md` defaults by genre

Render scripts prepend the style anchor to every shot prompt before submission. If `.great-authors/visual-lints.md` exists, render scripts also prepend the consolidated negative-prompt section to every block.

---

## Image-generation backends

Like the four video paths (Path A through D), the image-generation backends are documented here so render scripts can target them consistently. Empirical comparison data informing this section: `~/brain/learnings/image-gen-engine-comparison-editorial-illustration-and-book-covers.md`.

### Path E — gpt-image-1 (OpenAI Images API) — default

The practical default for editorial-register work. Best brief adherence among non-verification-gated models.

- **Model ID:** `gpt-image-1`
- **Endpoint:** `POST https://api.openai.com/v1/images/generations`
- **Auth:** `OPENAI_API_KEY` (Bearer)
- **Sizes:** `1024x1024`, `1024x1536` (portrait), `1536x1024` (landscape ~3:2)
- **Quality tiers:** `low`, `medium`, `high`
- **Pricing:** ~$0.19/image at high quality, $0.07 at medium, $0.011 at low
- **Prompt length:** 3,000+ chars (no hard limit observed in normal use)
- **Content policy:** strict on real people, brand logos, sexual content; permissive on violence-adjacent imagery for narrative fiction; flagged terms produce `image_generation_user_error` rather than silent compromise
- **Honors negative prompts:** strongly. The killer feature for stylized work with strict refusal lists.
- **Text rendering:** competent on short, clean title typography (good enough for book covers in v1.7); not reliable for long copy or unusual typefaces
- **Edits endpoint:** none (gpt-image-1 is generation-only)
- **Use when:** the project has a strict visual register, a long negative-prompt list, or a style anchor that must be honored across many images

### Path F — gpt-image-2 (OpenAI Images API)

State-of-the-art at time of writing. **Requires organization verification on the OpenAI platform** — non-owners cannot self-verify; plan around this when picking models for a workflow.

- **Model ID:** `gpt-image-2` (snapshot `gpt-image-2-2026-04-21`)
- **Endpoint:** `POST https://api.openai.com/v1/images/generations` and `POST /v1/images/edits`
- **Auth:** `OPENAI_API_KEY` on a verified org
- **Sizes:** same as gpt-image-1 plus expanded options
- **Pricing:** higher than gpt-image-1 (varies by quality tier)
- **Edits endpoint:** present — supports image-to-image with prompt; useful for variant generation
- **Use when:** the org is verified AND the project needs the edits endpoint OR slightly stronger brief adherence than gpt-image-1
- **Don't use when:** org isn't verified (the API returns 401 with a verification-required error)

### Path G — Imagen 4 Ultra (Gemini API)

When text rendering is the load-bearing requirement.

- **Model IDs:** `imagen-4.0-ultra-generate-001`, `imagen-4.0-generate-001`, `imagen-4.0-fast-generate-001`
- **Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/<model-id>:predict`
- **Auth:** `GEMINI_API_KEY` or `GOOGLE_API_KEY` via `x-goog-api-key` header
- **Sizes:** controlled via `aspectRatio` parameter (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`)
- **Pricing:** $0.06 (Fast) to $0.04-0.08 (standard) to higher for Ultra; verify in Google Cloud console
- **Prompt length:** 3,000+ chars handled
- **Content policy:** **`personGeneration: allow_adult`** parameter required for any prompt featuring human subjects; without it, the API refuses
- **Honors negative prompts:** moderate. Tends to leak forbidden elements (color through specified-monochrome scenes; secondary props the prompt didn't request).
- **Text rendering:** the strongest of the four for rendered text within an image (titles, signs, captions)
- **Use when:** the image must contain readable text (book covers with title typography; signage; captions in editorial illustration)
- **Verify model availability:** call `GET /v1beta/models` first; the model ID set drifts. Do NOT assume `imagen-3.0-generate-002` or other older IDs work.

### Path H — Leonardo Phoenix

Avoid for editorial-register work; acceptable for tasks where the user will manually correct.

- **Model ID:** Phoenix-family slugs (varies by Leonardo plan — Phoenix 1.0, Phoenix Lightning, etc.)
- **Endpoint:** `POST https://cloud.leonardo.ai/api/rest/v1/generations`
- **Auth:** `LEONARDO_API_KEY` Bearer
- **Sizes:** parameterized by `width` / `height` in pixels; common book-cover sizes 832×1216 (2:3 portrait), 1024×1024
- **Pricing:** consumes "tokens" from a Leonardo plan; varies
- **Prompt length:** **1,500-character hard limit** — meaningfully shorter than other backends
- **Content policy:** moderate; permissive on stylized violence
- **Honors negative prompts:** **weak** — empirically fights negative prompts and invents content (saguaros where forbidden, color floods, frame borders, additional figures). Do not trust for stylized register with strict refusal lists.
- **Text rendering:** poor; garbles titles routinely (observed: "MURDER ON THE / THE ARIZONA / —ARIZONA / —STRIP")
- **Use when:** the brief is loose, the user will manually accept/reject many candidates, and the cost is lower than alternatives for the project budget
- **Critical quirk: download User-Agent.** Leonardo's CDN returns 403 to default Python `urllib` User-Agents. Render scripts MUST set a browser User-Agent (`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36`) on download requests, or the image generates successfully and the download fails.

### Backend selection by use case

| Use case | Default | Fallback |
|---|---|---|
| Editorial illustration with strict register | gpt-image-1 (E) | gpt-image-2 (F) if org verified |
| Book cover with rendered title text | gpt-image-1 (E) | Imagen 4 Ultra (G) if title fidelity is critical |
| Video keyframes for image-to-video | gpt-image-1 (E) | none — keyframes feed Kling/Runway, not the image-gen choice |
| High-volume informal generation | Leonardo Phoenix (H) | gpt-image-1 at low quality |
| When org verification blocks gpt-image-2 | gpt-image-1 (E) | Imagen Fast (G) for cost-sensitive work |

### Render script contract

Project-level render scripts (`scripts/render_keyframes.py` for image generation, plus `scripts/wire_book_illustrations.py` for placing rendered PNGs into chapter MDX) read PROMPTS.md, prepend the style anchor and visual-lints negative prompt to each block, submit per the backend's API shape, and download with the appropriate User-Agent (browser-style for Leonardo). The scripts handle:

- Idempotency (skip-if-exists; `--force` regenerates; `--only <slug>` filters)
- Pacing between submissions
- Error surfacing with the backend's specific error code (e.g., `MOVIO_PAYMENT_INSUFFICIENT_CREDIT`, `image_generation_user_error`, `personGeneration` policy refusal)
- Save state so re-runs skip completed items

These scripts are templated in `templates/scripts/` (great-filmmakers v1.6+) and copied into projects by `/filmmakers-project-init`.

---

## Format stability guarantee

v0.1 and v1.0 share this footer schema. Future changes must be additive (new fields) or require a major version bump. Downstream pipelines pin against a specific footer version via the `backend` field's presence and shape.

The PROMPTS.md format and image-gen backend contract introduced in v1.7 follow the same stability rule. Slug regex, block structure, and field names are stable; new fields can be added; renames or removals require a major bump.
