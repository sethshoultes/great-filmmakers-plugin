# Great Filmmakers — User Manual

**Version:** 1.1.0
**Audience:** developers and writers using Claude Code who want a virtual film crew sitting alongside their editor.

This is the long-form reference. For a quick overview, see the [README](README.md). For the underlying design philosophy, see the essay [Three Shapes of the Same Pattern](https://sethshoultes.com/blog/three-shapes.html).

## Companion manuals in the trilogy

- [Great Minds — User Manual](https://github.com/sethshoultes/great-minds-plugin/blob/main/MANUAL.md) — fourteen strategic decision-makers (Jobs, Musk, Buffett, Ive, Rubin, Huang, Winfrey, Rhimes, Blakely, Hamilton, Angelou, Sorkin, Aurelius, Jackson)
- [Great Authors — User Manual](https://github.com/sethshoultes/great-authors-plugin/blob/main/MANUAL.md) — eleven prose craft personas (Hemingway, Didion, McCarthy, Morrison, Wallace, etc., plus Gottlieb the editor)
- **Great Filmmakers — User Manual (this document)** — twelve film craft personas (Scorsese, Kubrick, Kurosawa, Hitchcock, Spielberg, Lynch, Rhimes, Kaufman, Deakins, Schoonmaker, Zimmer, Ferretti)

---

## Table of Contents

1. [What this plugin is](#1-what-this-plugin-is)
2. [Install](#2-install)
3. [The mental model](#3-the-mental-model)
4. [Quick start — your first five minutes](#4-quick-start--your-first-five-minutes)
5. [The twelve personas](#5-the-twelve-personas)
6. [The five commands](#6-the-five-commands)
7. [The project bible](#7-the-project-bible)
8. [Choosing a backend](#8-choosing-a-backend)
9. [Veo 3 production constraints](#9-veo-3-production-constraints)
10. [Style presets](#10-style-presets)
11. [End-to-end walkthrough — a 50-second cinematic short](#11-end-to-end-walkthrough)
12. [Patterns and best practices](#12-patterns-and-best-practices)
13. [Troubleshooting](#13-troubleshooting)
14. [Frequently asked questions](#14-frequently-asked-questions)
15. [Reference](#15-reference)

---

## 1. What this plugin is

Great Filmmakers is a Claude Code plugin that turns a single conversation into a working film crew. It ships twelve specialist personas — six directors, two writers, four craft specialists — plus five orchestration commands that route the work between them.

The personas are not impressionistic pastiches. Each is a named filmmaker with a specific craft slot — Schoonmaker for the cut, Deakins for the frame, Zimmer for the score, Ferretti for the world the camera sees. When you invoke them through the orchestration commands, you get craft feedback that doesn't collapse into Claude's default register.

Great Filmmakers is the third plugin in a trilogy:

- [`great-minds-plugin`](https://github.com/sethshoultes/great-minds-plugin) — strategic decision-makers (fourteen voices)
- [`great-authors-plugin`](https://github.com/sethshoultes/great-authors-plugin) — prose craft (ten voices)
- **`great-filmmakers-plugin`** (this one) — film craft (twelve voices)

All three share a single pattern: **persona + bible + save triggers + fan-out + output format**. Section 3 explains what that means and why it matters.

---

## 2. Install

### Marketplace install (recommended)

```
/plugin marketplace add sethshoultes/great-filmmakers-plugin
/plugin install great-filmmakers@sethshoultes
```

That's it. The plugin's commands (`/filmmakers-project-init`, `/filmmakers-channel`, `/filmmakers-edit`, `/filmmakers-critique`, `/filmmakers-debate`, `/filmmakers-crew`) become available in your next Claude Code session.

### Companion plugins

Most projects benefit from running great-filmmakers alongside great-authors:

```
/plugin install great-authors@sethshoultes
```

The two share the same `.great-authors/` bible at the project root. Authors writes prose into `manuscript/`; filmmakers writes film artifacts into `film/`. Section 7 covers the layout in detail.

### Required for the Veo 3 backend

If you'll use `/filmmakers-crew --backend veo3` to render multi-character cinematic scenes, you need a paid Gemini API tier (the free tier has no Veo access). Store your key at `~/.config/dev-secrets/secrets.env` as `GEMINI_API_KEY=…` and source it before any render session — see the the canonical credential-handling pattern (single source at `~/.config/dev-secrets/secrets.env`, sourced into the shell before each render session) for the convention.

---

## 3. The mental model

Every persona-driven plugin in the trilogy is built from four reusable pieces plus one piece that varies. Understanding this makes the rest of the manual much faster to absorb.

### Piece 1 — The persona

A persona is a single markdown file in `agents/` with YAML frontmatter and a body in a fixed shape: identity, voice, core principles, role-specific primary utility, *how to draft* section, before-you-work protocol, cross-references, things you never do, staying-in-character footer. All twelve filmmaker personas share this shape.

### Piece 2 — The bible

A directory at the project root, conventionally `.great-authors/`, that holds the world the personas read before speaking. Characters, places, scenes, voice rules, glossary, journal. The bible is shared across plugins — when great-filmmakers blocks a scene, it reads the same `characters/marcus.md` that great-authors uses to edit Marcus's dialogue.

### Piece 3 — The save trigger

While a persona is loaded via `/filmmakers-channel`, certain phrases tell the plugin to write the next prose block to disk. *"Save as screenplay"* writes to `film/screenplay/<current-scene>.md`. Five variants, one per artifact type. The save trigger is the seam between the conversation and a file on disk.

### Piece 4 — The fan-out

Some commands (`/filmmakers-critique`, `/filmmakers-edit`, `/filmmakers-debate`) dispatch multiple personas in parallel and consolidate their outputs into a single verdict. This is how you get fast triage from many voices without sequential back-and-forth.

### The varying piece — The output format

Authors produce prose; the artifact is the `.md` file itself. Filmmakers produce a treatment that has to become video, and the artifact is whatever the rendering tool can consume — a HeyGen avatar script, a Veo 3 production doc, or a Remotion slideshow script. The output format is the only inch of difference between great-authors and great-filmmakers. Everything else is reusable.

If you remember nothing else from this section: **every persona is a voice; every command coordinates voices; every backend is a different way to get the result onto a screen.**

---

## 4. Quick start — your first five minutes

You'll initialize a project, channel a director, and save a shot list. No video render required.

### Step 1 — Initialize the bible (skip if you already have one)

In a fresh project directory:

```
/authors-project-init      # creates .great-authors/
/filmmakers-project-init         # creates film/ and registers it in .great-authors/project.md
```

The first command (from great-authors) scaffolds the shared bible. The second adds a `film/` directory at the project root with five empty subdirectories (screenplay, shot-lists, score-notes, storyboards, edit-notes) and a `## Film` section in `project.md` that names your starting scene.

### Step 2 — Channel a director

```
/filmmakers-channel scorsese
```

Scorsese is now in the conversation. Ask him about a scene from your manuscript, paste a paragraph, or describe a moment you're trying to land:

> *"There's a moment in chapter four where Marcus walks into the diner and sees Anna at the counter. I want it to feel inevitable but charged. How do you block this?"*

Scorsese answers in his voice — kinetic camera, music as structure, moral voltage. The discipline comes from his persona file, not from prompting.

### Step 3 — Save a shot list

After Scorsese sketches the scene, say:

> *"save as shot list"*

The plugin writes the last prose block to `film/shot-lists/<current-scene>.md`. The `<current-scene>` slug comes from the `## Film` section in your bible's `project.md`.

### Step 4 — Channel a different specialist

```
/filmmakers-channel deakins
```

Show Deakins the shot list and ask about lensing. He'll pick lens lengths, blocking, and natural-light strategies. Save his pass:

> *"save as storyboard"*

Now you have two artifacts in `film/`. Repeat with Schoonmaker for cut rhythm, Zimmer for score, Ferretti for production design — each writes their own file in the appropriate subdirectory.

That's the channel-and-save loop. It's the most direct way to use the plugin.

---

## 5. The twelve personas

### Directors (6)

Each director occupies a distinct creative slot. When you don't know which director fits a scene, ask the question the table answers: *what is this scene actually trying to do?*

| Persona | Channel command | Strength | Best for |
|---------|-----------------|----------|----------|
| Martin Scorsese | `/filmmakers-channel scorsese` | Kinetic camera, music as structure, moral voltage | Scenes with momentum, character on the edge, guilt or transgression |
| Stanley Kubrick | `/filmmakers-channel kubrick` | Cold control, symmetry, the composed frame | Procedural scenes, institutional power, controlled tension |
| Akira Kurosawa | `/filmmakers-channel kurosawa` | Movement, weather, group geometry | Crowds, landscape, kinetic ensemble action |
| Alfred Hitchcock | `/filmmakers-channel hitchcock` | Suspense geometry, POV, audience manipulation | Anything where the audience must know more or less than the character |
| Steven Spielberg | `/filmmakers-channel spielberg` | Blocking for emotion, populist mastery, the wonder shot | Family scenes, awe, accessible entry points |
| David Lynch | `/filmmakers-channel lynch` | Dream logic, sound design, the uncanny | Anything where literal logic isn't enough |

### Writers' room (2)

Writers adapt source prose into the chosen backend's input format. They don't draft from scratch; they shape what's already on the page.

| Persona | Channel command | Strength | Best for |
|---------|-----------------|----------|----------|
| Charlie Kaufman | `/filmmakers-channel kaufman` | Structural invention, interiority, puzzle-box logic | Adapting essays, internal-monologue source material, structural risk |
| Shonda Rhimes | `/filmmakers-channel rhimes` | Scene architecture, serial momentum, crackling dialogue | Adapting narrative prose, multi-character scenes, episodic sequencing |

Kaufman is the default writer for `/filmmakers-crew`. If `--avatar sara` is selected for HeyGen, Rhimes is auto-assigned because her scrappy serialized voice matches Sara's avatar register.

### Craft specialists (4)

Specialists add depth on a single craft axis. They don't break down whole scenes — they sharpen one dimension of the work.

| Persona | Channel command | Strength | Best for |
|---------|-----------------|----------|----------|
| Roger Deakins | `/filmmakers-channel deakins` | Cinematography — natural light, lens psychology, considered composition | Lens choice, lighting plans, frame composition |
| Thelma Schoonmaker | `/filmmakers-channel schoonmaker` | Editing — rhythm, cut points, pace | Cut rhythm, shot durations, *find the cut* |
| Hans Zimmer | `/filmmakers-channel zimmer` | Composition — scene architecture through sound, emotional voltage | Score direction, audio cues, music tags for the rendering backend |
| Dante Ferretti | `/filmmakers-channel ferretti` | Production design — the world the camera sees | Set details, props, color palette, character costume specificity |

### When you can't decide

If the task is fundamentally about a single craft — *"what lens?"* — pick the specialist for that craft. If it's about the whole scene's identity — *"what kind of moment is this?"* — pick a director whose strengths line up with what the scene is trying to do. When in doubt for narrative shorts, default to **Scorsese**; for educational/explainer work, default to **Spielberg**; for procedural/cold work, default to **Kubrick**.

You can always switch mid-conversation:

```
/filmmakers-channel scorsese
…
/filmmakers-channel deakins
```

The new persona replaces the previous one in the active conversation.

---

## 6. The five commands

The plugin ships five orchestration commands. Three coordinate voices in real time; two write artifacts to disk.

### `/filmmakers-project-init`

Scaffolds the `film/` directory at the project root and adds a `## Film` section to `.great-authors/project.md` that names your current scene. Run once per project, after `/authors-project-init`.

```
/filmmakers-project-init
```

The command will ask one question — *"What's the slug for the scene you're starting with?"* — and accept any kebab-case identifier. Default: `scene-01`.

### `/filmmakers-channel <name>`

Loads a single persona into the current conversation. While channeled, save triggers append the next prose block to disk.

```
/filmmakers-channel scorsese
```

Save trigger phrases:

| Phrase | Writes to |
|--------|-----------|
| *"save as screenplay"* | `film/screenplay/<current-scene>.md` |
| *"save as shot list"* | `film/shot-lists/<current-scene>.md` |
| *"save as score notes"* | `film/score-notes/<current-scene>.md` |
| *"save as storyboard"* | `film/storyboards/<current-scene>.md` |
| *"save as edit notes"* | `film/edit-notes/<current-scene>.md` |

Use this command when you want a real craft conversation with a single voice. It's the most direct way to use the plugin and the one you'll reach for most often.

### `/filmmakers-critique`

Fast triage across multiple personas. Dispatches in parallel using a smaller model (Haiku). Each persona returns three bullets — one observation, one risk, one fix.

```
/filmmakers-critique scorsese,deakins,schoonmaker scenes/diner-scene.md
```

Use this when you need quick diverse perspective without long-form depth. The output consolidates the bullets into a single verdict so you can read everything in under thirty seconds.

### `/filmmakers-edit`

Deep markup pass across multiple personas in parallel. Uses Sonnet for craft-quality output. Each persona returns inline annotations on the source plus a paragraph-length summary.

```
/filmmakers-edit kubrick,deakins,ferretti film/screenplay/diner-scene.md
```

Use this when you have a draft and want craft-level revision suggestions from multiple voices. The output is consolidated into a single annotated file with attribution.

### `/filmmakers-debate`

Two personas argue a craft question. Useful when the answer depends on values that genuinely differ.

```
/filmmakers-debate scorsese kubrick "should this scene cut on the line or hold past it?"
```

The two personas trade three exchanges, then a third persona (Schoonmaker by default) summarizes the disagreement and proposes a synthesis. Use this when the debate itself is the value — for one-sided answers, channel a single persona instead.

### `/filmmakers-crew`

End-to-end pipeline. Takes a source file and a backend flag, dispatches the full crew, writes the production-ready artifact.

```
/filmmakers-crew manuscript/diner-scene.md --backend veo3
/filmmakers-crew blog/garage-door-opener-lifespan.mdx --backend heygen --avatar maya
/filmmakers-crew inspection/door-walkaround.md --backend remotion
```

This is the command you use when you've done the writing and now want a video. The chosen backend determines which personas contribute and what artifact lands on disk. Section 8 explains backend selection in detail.

---

## 7. The project bible

The bible is a directory at the project root. Both great-authors and great-filmmakers read from the same one. By convention it's named `.great-authors/` because authors shipped first; the name is legacy, the structure is portable.

### Layout

```
my-project/
├── .great-authors/           # the shared bible
│   ├── project.md            # working title, premise, voice, current scene
│   ├── voice.md              # voice rules in detail
│   ├── timeline.md           # for narrative work
│   ├── glossary.md           # terms, names, world rules
│   ├── characters/           # one .md per character
│   ├── places/               # one .md per location
│   ├── scenes/               # for narrative work
│   └── journal/              # process notes
├── manuscript/               # great-authors writes here
└── film/                     # great-filmmakers writes here
    ├── screenplay/
    ├── shot-lists/
    ├── score-notes/
    ├── storyboards/
    └── edit-notes/
```

### Why the bible matters

Personas read the bible before speaking. A character in `characters/marcus.md` is the same character whether Hemingway is editing his dialogue or Deakins is shot-listing his entrance. A place in `places/millbrook.md` is the same town across both plugins.

If you skip the bible, your dispatched personas will produce off-voice output — they'll fall back to generic register because they have no anchor. The thirty seconds you save by not writing `characters/marcus.md` will cost you the next hour in revision.

### Initialize once

```
/authors-project-init       # from great-authors-plugin
/filmmakers-project-init          # from great-filmmakers-plugin
```

The second command is idempotent — if `film/` already exists, it asks before overwriting.

---

## 8. Choosing a backend

`/filmmakers-crew` produces a production-ready artifact for one of three rendering tools. Each fits a different shape of work.

### `--backend heygen` — single-avatar talking-head

A LiveAvatar reads a script in front of a clean background. Lip-synced, adjustable voice, supports captions and on-screen text overlays.

**Use when:**
- The source is educational, diagnostic, or explanatory.
- One persona will narrate the whole video — Maya, Sara, Rick, Margaret, or Seth.
- The visual register is *"someone helpful is talking to me."*

**Output:** `film/screenplay/<slug>.heygen.md` — a script in the exact format the [garagedoorscience HeyGen pipeline](https://github.com/sethshoultes/garagedoorscience) consumes. Drop in via `cp`, run the existing submit step.

**Personas active:** Kaufman or Rhimes (writer adapts), the chosen director (provides edit notes), Schoonmaker (cut rhythm). Deakins, Zimmer, Ferretti are skipped — HeyGen generates its own visuals and audio.

### `--backend veo3` — multi-character cinematic

Veo 3 generates frame-by-frame video from text prompts. Multi-character scenes, camera moves, atmospheric shots. The look is what you describe.

**Use when:**
- The source is narrative, dialogue-heavy, or scene-driven.
- The visual register is *"this is a film."*
- The work is too cinematic for HeyGen and too multi-shot for Remotion.

**Output:** `film/screenplay/<slug>.veo3.md` — a production doc with CAST, LOCATIONS, VISUAL GRAMMAR, NEGATIVE PROMPT, and SHOT LIST. Drop into `~/Local Sites/veo-builder/` (the dashboard) for parsing, or render directly via the Gemini API.

**Personas active:** all twelve. Ferretti writes CAST and NEGATIVE PROMPT; Deakins writes VISUAL GRAMMAR; the director sketches the SHOT LIST; Kaufman/Rhimes integrates into the production doc; Schoonmaker assigns shot durations (quantized to {4, 6, 8} seconds — see Section 9); Zimmer embeds audio cues in each shot prompt.

### `--backend remotion` — slideshow with narration

Programmatic composition: narration over a sequence of slides. Custom photos, brand assets, on-screen text panels.

**Use when:**
- The source is inspection-style or photo-heavy work.
- HeyGen would be wrong (no spoken-by-a-person register) and Veo would be wrong (no real photos).
- You need brand-controlled visuals that map to specific source images.

**Output:** `film/screenplay/<slug>.remotion.md` — narration paragraphs + `musicPromptFor()` tags + per-segment timing hints. Consumed by `garagedoorscience/remotion/scripts/generate-video-from-blog.ts`.

**Personas active:** writer (narration paragraphs), Zimmer (music tags), Schoonmaker (timing).

### When you don't pass `--backend`

`/filmmakers-crew` will auto-select based on classification signals in the source — educational/maintenance/cost/safety prose → HeyGen; narrative/dialogue-heavy → Veo 3; inspection-style → Remotion. If the source is ambiguous, the command asks rather than guesses.

---

## 9. Video gen production constraints

There are now **four paths** for rendering shots in the production doc, across three different services. v1.4 added Path C (Kling) and Path D (Leonardo Motion) after a head-to-head test against Veo. The default is still Path A (Veo 3.0 Fast text-to-video) for trilogy/series work — that test confirmed Veo's text-to-video composition consistency wins at project scale. But for one-shot cinematic clips, atmospheric B-roll, or cost-floor renders, the alternative paths are real options.

### Path A — Veo 3.0 Fast + inline anchoring (default, cheapest)

Best for: dialogue-heavy or pacing-heavy work where mixed cut lengths matter.

- **Model:** `veo-3.0-fast-generate-001` ($0.10/sec at 720p).
- **Shot durations are quantized to {4, 6, 8} seconds.** Five and seven get rejected despite the error message claiming "between 4 and 8 inclusive." Schoonmaker's persona teaches this:
  > *"The four-second insert and the six-second hold are the rhythm now. The work is to choose which beats earn six and which earn four — and to leave the eight-second shot for the moment that needs the room."*
- **No `personGeneration`** on tier 1 (rejected; on the upgraded tier it's accepted but optional).
- **No `referenceImages`** on Veo 3.0 — explicitly rejected with *"isn't supported by this model."*
- **Continuity mechanism:** inline character anchoring. Repeat the full character description verbatim in every shot prompt where the character appears:

```
WRITER (WR): a man in his mid-forties drawn in pen-and-ink with crosshatch
shading, wire-rim glasses, salt-and-pepper hair, worn gray henley sweater
```

Drop that phrase into every shot the writer is in. Veo holds the rendering close enough across cuts. Token budget is generous — verified at 480 input tokens per shot prompt.

### Path B — Veo 3.1 Fast preview + reference images (stronger continuity)

Best for: multi-character scenes where face/character continuity is the dominant editorial concern. Available on the upgraded Gemini API tier.

- **Model:** `veo-3.1-fast-generate-preview`.
- **All shot durations fixed at 8 seconds.** This is a hard constraint: 4- and 6-second clips silently reject when reference images are present. Schoonmaker's "round to {4, 6, 8}" rule collapses to "every shot is 8."
- **`aspectRatio: "16:9"` mandatory.** Other ratios reject when reference images are present.
- **Up to 3 reference images per shot.** Generate them via Imagen 4 Fast (~$0.02/image) and pass them via the `referenceImages` array.
- **Cannot combine reference images with `image` (init frame) or `lastFrame`.** Pick one continuity mechanism per shot.
- **Request shape (forum-confirmed; the docs page on `ai.google.dev/gemini-api/docs/video` shows an `inlineData` wrapper that the API rejects — don't trust it):**

```json
{
  "instances": [{
    "prompt": "...",
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

Notes:
- `referenceType` is `"asset"` lowercase. `"ASSET"` rejects.
- The `image` object uses **flat** `bytesBase64Encoded` + `mimeType`, NOT the `inlineData: {mimeType, data}` wrapper Google's docs page shows. Trust the API behavior over the docs page on this field.

### Path C — Kling 2.5 Turbo image-to-video (single-clip strength)

Available with a Kling API account (HMAC-signed JWT auth using access+secret keys). Strong motion physics; image-to-video grounding. Use for one-off cinematic shots when the source still can be art-directed.

- **Service:** Kling 2.5 Turbo (`kling-v2-5-turbo`), std mode, image-to-video.
- **Pipeline:** generate a composite still first (Phoenix or gpt-image-2), then animate.
- **Durations:** **5 or 10 seconds only.**
- **Aspect ratios:** 16:9, 9:16, or 1:1.
- **Cost:** ~$1 per 5s clip.
- **Auth:** HMAC-SHA256-signed JWT with `iss` (access key), `exp` (now+1800), `nbf` (now-5).
- **Endpoint:** `POST https://api-singapore.klingai.com/v1/videos/image2video`

Request shape:

```json
{
  "model_name": "kling-v2-5-turbo",
  "image": "<base64 of source still, no data:image/png;base64, prefix>",
  "prompt": "<motion prompt>",
  "duration": "5",
  "mode": "std",
  "aspect_ratio": "16:9"
}
```

**When NOT to use Path C for series work:** the trilogy short re-render via Kling produced figures that read as "grounded in a stage floor" because the Phoenix stills introduced floor surfaces that Veo's text-to-video would have rendered as void. Image-to-video composes each shot from its own still, so composition drift between shots compounds. **For multi-shot stylized series work, prefer Path A or B over Path C.**

### Path D — Leonardo Motion 2.0 image-to-video (cheap atmospheric)

Available with a Leonardo API account.

- **Service:** Leonardo Motion 2.0, image-to-video.
- **Pipeline:** chain Phoenix `imageId` directly into Motion 2.0 (no upload step; `imageType: "GENERATED"`).
- **Durations:** **5 seconds.**
- **Resolution:** RESOLUTION_480 or RESOLUTION_720.
- **Cost:** ~$0.05 per 5s clip — **cheapest of the four paths**.
- **Endpoint:** `POST https://cloud.leonardo.ai/api/rest/v1/generations-image-to-video`

Request shape:

```json
{
  "imageType": "GENERATED",
  "imageId": "<Phoenix gen id>",
  "prompt": "<motion prompt>",
  "resolution": "RESOLUTION_720",
  "frameInterpolation": true,
  "promptEnhance": true,
  "isPublic": false
}
```

**When NOT to use Path D for character work:** Motion 2.0 has documented character drift — figures shift unnaturally even when prompted to hold pose. The trilogy three-character test showed all three figures drifting in unintended ways. **Use Path D only for atmospheric clips, B-roll, or backgrounds where character identity doesn't need to hold.**

### Choosing between A, B, C, D

| Question | Path |
|----------|------|
| Multi-shot stylized series with character continuity | **A** — Veo 3.0 Fast text-to-video, mixed {4, 6, 8} durations |
| Stronger character continuity than inline anchoring | **B** — Veo 3.1 Fast preview with refs, every shot 8s @ 16:9 |
| Single cinematic clip with art-directed still | **C** — Kling 2.5 Turbo image-to-video, 5 or 10s |
| Cheap B-roll, atmospheric clips, no character continuity needed | **D** — Leonardo Motion 2.0 image-to-video, 5s, $0.05/clip |
| Mixed durations needed (4, 6, 8 in same project) | **A only** — the other paths fix duration |
| Lowest cost | **D** ($0.05/clip) |
| Best motion physics on a single shot | **C** |

**The default is A.** Switch to B for character-heavy continuity. Pick C for one-off cinematic shots. Pick D only when cost is the primary constraint and continuity doesn't matter.

**The trilogy short** lives at Path A — the visual proof that text-to-video composition consistency wins at project scale. The Kling re-render at `/tmp/trilogy-kling/` is the counter-evidence: same prompts, image-to-video pipeline, "grounded floor" artifact across multiple shots.

### Default model

Default `veo_model` in the production doc footer is **`veo-3.0-fast-generate-001`** — $0.10/sec at 720p, the cheapest working model that allows stylized human subjects.

If Fast hits its daily quota (rolling 24-hour window, ~10–15 calls on tier 1), fall back to **`veo-3.0-generate-001`** (standard, 4× cost: $0.40/sec). Same content gates, separate quota pool.

Veo 3.1 preview models (`veo-3.1-fast-generate-preview`, `veo-3.1-generate-preview`) require an upgraded Gemini tier. On tier 1 they reject all human subjects.

### Resolution

Defaults to 720p. **1080p requires `durationSeconds: 8`** — passing 1080p with 4 or 6 seconds returns *"Resolution 1080p requires duration seconds to be 8 seconds."* The plugin doesn't pass `resolution` by default; specify it only when you've made the duration commitment.

### Pacing and rate limits

- **Per-minute:** ~1–2 requests/min is safe. Pace 45–60s between submits to avoid 429s.
- **Daily/rolling 24h:** ~10–15 video calls on tier 1; substantially higher on the upgraded tier.
- **Retry strategy:** exponential backoff starting at 60s, doubling, capped at ~10 minutes. After 4 attempts, move to the next shot rather than block the batch.

A complete reference is at [`~/brain/learnings/veo-3-api-constraints.md`](https://github.com/sethshoultes/brain/blob/main/learnings/veo-3-api-constraints.md) (private vault).

---

## 10. Style presets

A style preset is a paragraph prepended verbatim to every Veo 3 shot prompt. It locks the visual register so match-cuts and character continuity actually work.

Without a style preset, Veo defaults to a generic photorealistic register that varies subtly between shots — and content-gates photorealistic humans on this tier. With a strong stylized preset, humans render fine and the look is consistent.

### `pen-and-ink-editorial` (v1.1 default)

Verified to bypass Veo's photorealistic-human content gate without `personGeneration`. Black-and-white, draftsmanlike, never whimsical. Reads like an animated New Yorker spot illustration.

```yaml
prompt_anchor: |
  Black-and-white pen-and-ink animation in the style of an animated New Yorker
  illustration. Crosshatch shading. High-contrast linework. Spare composition.
  Editorial, adult, draftsmanlike. Never whimsical. Limited grayscale palette.
  Subtle paper-grain texture. Static frame except where motion is named.
```

### Other presets in the library

`noir`, `photoreal-cinematic`, `studio-ghibli` — present as scaffolds in `docs/style-presets.md` but **not yet verified** against Veo's content gates. Probe before relying on them.

### Adding your own

1. Add a section to `docs/style-presets.md` with a `prompt_anchor` block scalar.
2. Render at least three shots with the preset and inspect the output.
3. Mark "verified" only after rendering succeeds and the look is consistent across cuts.
4. The slug is lowercase-hyphen and stable; it ends up in the production doc footer as `style_preset:`.

---

## 11. End-to-end walkthrough

This is the path that produced [Three Shapes of the Same Pattern](https://sethshoultes.com/blog/three-shapes.html) — a 50-second cinematic short embedded in a blog post.

### Setup

```
mkdir trilogy-blog-post && cd trilogy-blog-post
/authors-project-init
/filmmakers-project-init
```

Edit `.great-authors/project.md` to set premise, voice, and characters. Edit `.great-authors/voice.md` to lock the voice rules.

### Step 1 — Draft prose with great-authors

```
/authors-channel didion
```

Channel Didion (or Hemingway, or whoever fits the voice). Have the conversation, save the result:

```
"save that"
```

The prose lands in `manuscript/trilogy.md`.

### Step 2 — Run the film crew

```
/filmmakers-crew manuscript/trilogy.md --backend veo3
```

This dispatches the full crew. The pipeline:

1. **Stage 1 (parallel):** Ferretti writes CAST + LOCATIONS + NEGATIVE PROMPT. Deakins writes VISUAL GRAMMAR. The director (Scorsese by default) sketches the SHOT LIST.
2. **Stage 2 (sequential):** Kaufman integrates all three into the final production doc with VISUAL GRAMMAR terms used by name in each shot prompt.
3. **Stage 3 (parallel):** Schoonmaker assigns shot durations (quantized to {4, 6, 8}) and flags the peak shot. Zimmer inserts audio cues into each shot prompt.

Output: `film/screenplay/trilogy.veo3.md` with CAST, LOCATIONS, VISUAL GRAMMAR, NEGATIVE PROMPT, and a SHOT LIST of 10 shots totaling 50 seconds.

### Step 3 — Render

```bash
set -a && source ~/.config/dev-secrets/secrets.env && set +a
python3 scripts/render_all.py
```

The render script (idempotent, with state persistence) submits each shot, polls until done, and downloads MP4s to `film/render/`. State is saved to `_render_state.json` — re-running skips completed shots.

For the trilogy short, this took about 25 minutes for 10 shots at $0.10/sec on Fast (≈ $5.00 total). Standard Veo 3.0 at $0.40/sec is the fallback if Fast hits its daily quota.

### Step 4 — Stitch

```bash
cd film/render
for i in 01 02 03 04 05 06 07 08 09 10; do
  echo "file 'shot-$i.mp4'" >> concat.txt
done
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy trilogy.mp4
```

DTS warnings on concat are cosmetic; playback is fine.

### Step 5 — Add narration (optional)

Use ElevenLabs to generate a voiceover timed to ~80% of the video length, leaving the last 10 seconds silent for the visual punch (Schoonmaker's *"leave silence for the visual punch"* principle).

```bash
ffmpeg -y -i trilogy.mp4 -i trilogy_vo.mp3 \
  -filter_complex "[0:a]volume=0.18[bg];[1:a]volume=1.0,apad=pad_dur=10[vo];[bg][vo]amix=inputs=2:duration=longest:dropout_transition=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k trilogy_final.mp4
```

Native audio at 0.18 (background ambient bed), VO at 1.0 (foreground), `apad=pad_dur=10` ensures the last 10 seconds is silence over ambient.

### Step 6 — Embed in your site

```html
<video controls preload="metadata" style="width:100%;max-width:780px;margin:1.5rem auto;display:block;border-radius:6px;background:#000">
  <source src="/blog/videos/trilogy.mp4" type="video/mp4">
</video>
```

Self-hosted on GitHub Pages, no third-party embed. See the [Publish Blog Post with Video Companion runbook](https://github.com/sethshoultes/brain/blob/main/runbooks/Publish%20Blog%20Post%20with%20Video%20Companion.md) for the full pattern.

---

## 12. Patterns and best practices

### Orchestrator, not channel

When you're working in a project that uses persona plugins, your role is to **dispatch**, not to **impersonate**. If you find yourself about to write *"Scorsese would say…"* — stop. Run `/filmmakers-channel scorsese` and let the persona file do the work.

The `templates/film-project/CLAUDE.md` that `/filmmakers-project-init` drops at the project root sets this expectation explicitly. When in doubt, read it.

The full essay is at [orchestrator-not-channel](https://github.com/sethshoultes/brain/blob/main/learnings/orchestrator-not-channel.md). The short version: inline impersonation collapses each voice into Claude's default register and erases the reason the personas exist.

### Read the bible before dispatching

If you skip the bible, your dispatched personas produce off-voice output. Always run `/authors-project-init` and `/filmmakers-project-init` before the first `/filmmakers-crew` invocation. Edit `project.md` and `voice.md` even if briefly.

### Leave silence for the visual punch

For Veo 3 shorts with narration, time the VO to about 80% of the video length. The last ~10 seconds of pure ambient + image will do more for the audience than another sentence. Schoonmaker's persona file teaches this; the trilogy short uses it; it works.

### One bundled commit per artifact, not per file

When `/filmmakers-crew --backend veo3` writes a production doc, it touches one file. Commit that as a unit. Don't split the CAST commit from the SHOT LIST commit — the artifact is the whole document.

### Don't try to channel multiple personas inline

If you need multiple voices, use `/filmmakers-edit`, `/filmmakers-critique`, or `/filmmakers-debate`. Don't try to alternate between them in a single channel session — switching `/filmmakers-channel` resets the active persona and loses the previous one's state.

### Use the right command for the depth you need

| Need | Command | Time | Output |
|------|---------|------|--------|
| Quick triage from many voices | `/filmmakers-critique` | <30s | 3 bullets per persona |
| Deep markup from many voices | `/filmmakers-edit` | 1–3 min | Inline annotations + paragraph |
| One voice, real conversation | `/filmmakers-channel` | as long as needed | Conversation + saved files |
| One voice, end-to-end | `/filmmakers-crew` | 1–5 min | Production-ready artifact |
| Argument between two voices | `/filmmakers-debate` | 1–2 min | Three exchanges + synthesis |

### The bible is shared but film and manuscript are not

`.great-authors/` is read by both plugins. `manuscript/` is great-authors' write target; `film/` is great-filmmakers'. Don't mix them — a `manuscript/foo.md` is prose; a `film/screenplay/foo.heygen.md` is a script in HeyGen's format. The pipeline depends on this separation.

---

## 13. Troubleshooting

### `/filmmakers-crew --backend veo3` produces 5- or 7-second shots

The plugin's v1.1 defaults round to {4, 6, 8}. If you see 5- or 7-second values, you're either on v1.0 (upgrade) or you've hand-edited the doc. Round up or down to the nearest valid duration before submitting to Veo.

### Veo returns "Your use case is currently not supported"

This error has two distinct causes — figure out which one you're hitting:

1. **You're on Gemini API tier 1 and submitting human subjects to a Veo 3.1 preview model.** Tier 1 doesn't allow human subjects on 3.1. Either switch to `veo-3.0-fast-generate-001` (Path A default) or upgrade your Gemini API tier.
2. **You're submitting `referenceImages` to a Veo 3.1 preview model with the wrong shape or wrong constraints.** Reference images work on Veo 3.1 but require:
   - `durationSeconds: 8` (4 and 6 silently reject)
   - `aspectRatio: "16:9"` (other ratios reject)
   - Flat `bytesBase64Encoded` + `mimeType` shape, NOT `inlineData` wrapper
   - `referenceType: "asset"` lowercase
   - No `image` (init frame) or `lastFrame` in the same request

   See Section 9 Path B for the full working request shape.

### Veo returns "referenceImages isn't supported by this model"

You're submitting reference images to a Veo 3.0 model. They're not supported there. Three options:

1. **Switch the model to `veo-3.1-fast-generate-preview`.** Reference images work there with constraints (every shot 8 seconds, aspectRatio 16:9 mandatory). See Section 9 Path B for the full request shape.
2. **Stay on Veo 3.0 Fast and use inline character anchoring** — repeat the full character description verbatim in every shot prompt. Cheaper and gives you mixed durations in {4, 6, 8}. This is Path A.
3. **Use the Veo Flow UI workflow** at `~/Local Sites/veo-builder/`, which does accept reference images directly. The plugin's `ingredient_images:` block in the doc footer feeds this path.

### Veo returns 429 "RESOURCE_EXHAUSTED"

You've hit the daily/rolling-24h quota. Three options:

1. Wait — the window is rolling from your first call, not midnight UTC.
2. Switch to `veo-3.0-generate-001` (standard) — 4× the cost ($0.40/sec) but a separate quota pool.
3. Upgrade your Gemini API tier — substantially higher daily caps.

### A persona's output sounds generic / not like them

You probably didn't read the bible. Run `/authors-project-init` and `/filmmakers-project-init`, edit `project.md` and `voice.md`, and re-channel. Personas without bible context fall back to Claude's default register.

### `/filmmakers-crew` says "no `.great-authors/` found"

Run `/authors-project-init` from `great-authors-plugin` first. The bible has to exist before `/filmmakers-project-init` can scaffold `film/`.

### Save trigger doesn't write to disk

You're not in a `/filmmakers-channel` session. Save triggers only work while a persona is loaded via `/filmmakers-channel`. If you've used `/filmmakers-edit` or `/filmmakers-critique`, those write directly without trigger phrases.

### The HeyGen script's frontmatter has unknown fields

The plugin adds `director:` and `adapter:` fields to HeyGen scripts. The existing pipeline's YAML parser ignores unknown keys. If your HeyGen pipeline strict-parses, drop those two fields before submission.

### A Veo render returns "no samples"

The prompt tripped a content gate. Strip suspect details (faces, brand names, weapons, modern smartphones, readable on-screen text), keep the style anchor, retry. Adding more negative-prompt language to the `NEGATIVE PROMPT` section often helps.

### My prompt has the right character description but Veo renders someone different

Check that the character description is in **every** shot prompt — not just the establishing shot. Inline anchoring requires verbatim repetition; Veo doesn't carry character state across separate API calls.

---

## 14. Frequently asked questions

### Can I run great-filmmakers without great-authors?

Technically yes — the plugin doesn't import great-authors as a dependency. Practically no — `/filmmakers-project-init` assumes a `.great-authors/` bible exists, and personas read from it. Run great-authors first; it's free and complementary.

### Do I have to use the Veo backend?

No. HeyGen and Remotion are first-class. If you don't have a Gemini API key, just use `--backend heygen` for talking-head work or `--backend remotion` for slideshow work.

### Can I add my own filmmaker persona?

Yes. Create `agents/<name>-persona.md` following the structure of the existing personas (identity, voice, core principles, role-specific primary utility, *how to draft*, before-you-work, cross-references, things you never do, staying-in-character footer). Add the slug to `/filmmakers-channel`'s alias table in `skills/filmmakers-channel/SKILL.md`. Submit a PR if it's a filmmaker the community would benefit from.

### Why is the bible called `.great-authors/` even when filmmakers are active?

Authors shipped first. Renaming would break every existing bible and force a migration for one cosmetic win. The name is legacy; the structure is portable.

### Can the plugins be used with non-Anthropic models?

Claude Code is currently Anthropic-only. The plugin's persona files are markdown with no model-specific syntax — they would port to other agent runtimes that support specialist subagent dispatch. The orchestration commands are Claude-Code-specific.

### How do I keep a Veo render under budget?

Default to Fast ($0.10/sec at 720p). Quantize all shots to {4, 6, 8} — no waste. For a 50-second short on Fast that's $5.00. Rendering on Standard quadruples the cost; only fall back when Fast hits daily quota and you can't wait.

### What happens if I hand-edit a `.veo3.md` production doc after `/filmmakers-crew` writes it?

Nothing breaks — the file is plain markdown. `/filmmakers-crew` won't overwrite without asking. Hand-editing is the expected workflow for fine-tuning before render.

### How do I rotate keys exposed in chat?

Visit each provider's dashboard, generate a new key, update only `~/.config/dev-secrets/secrets.env` (the canonical home). Every project that sources from canonical picks up the new value on next session. See [credential-handling-canonical-env](https://github.com/sethshoultes/brain/blob/main/learnings/credential-handling-canonical-env.md) for the full pattern.

---

## 15. Reference

### Plugin internals

| Path | Purpose |
|------|---------|
| `agents/<name>-persona.md` | Twelve persona files |
| `skills/filmmakers-project-init/SKILL.md` | `/filmmakers-project-init` |
| `skills/filmmakers-channel/SKILL.md` | `/filmmakers-channel <name>` |
| `skills/filmmakers-edit/SKILL.md` | `/filmmakers-edit <names> <file>` |
| `skills/filmmakers-critique/SKILL.md` | `/filmmakers-critique <names> <file>` |
| `skills/filmmakers-debate/SKILL.md` | `/filmmakers-debate <a> <b> <topic>` |
| `skills/filmmakers-crew/SKILL.md` | `/filmmakers-crew <source> --backend …` |
| `templates/film-project/CLAUDE.md` | Dropped at project root by `/filmmakers-project-init` |
| `docs/output-formats.md` | Format specs for HeyGen / Veo 3 / Remotion artifacts |
| `docs/style-presets.md` | Style preset library |
| `docs/profiles.md` | Persona profile mapping (design-time reference) |
| `docs/transfer-notes.md` | Plugin-design notes |

### External references

- [Three Shapes of the Same Pattern](https://sethshoultes.com/blog/three-shapes.html) — the design-philosophy essay
- [great-minds-plugin](https://github.com/sethshoultes/great-minds-plugin) — strategic decision-makers
- [great-authors-plugin](https://github.com/sethshoultes/great-authors-plugin) — prose craft
- [veo-builder](https://github.com/sethshoultes/veo-builder) — local Flask dashboard for parsing Veo production docs
- [garagedoorscience](https://github.com/sethshoultes/garagedoorscience) — the HeyGen / Remotion reference pipeline

### Brain references (private vault)

These are Seth's private vault notes; if you have access, they're the most current operational references:

- `learnings/veo-3-api-constraints.md` — full constraint table
- `learnings/orchestrator-not-channel.md` — dispatch-don't-impersonate pattern
- `learnings/plugin-v1.0-is-not-mature.md` — why v1.1 hardening is a required step
- `learnings/credential-handling-canonical-env.md` — secrets management
- `runbooks/Veo 3 Cinematic Short.md` — step-by-step render procedure
- `runbooks/Publish Blog Post with Video Companion.md` — text-then-video publishing pattern

### License

MIT. See [LICENSE](LICENSE) at the repo root.

### Reporting issues

[github.com/sethshoultes/great-filmmakers-plugin/issues](https://github.com/sethshoultes/great-filmmakers-plugin/issues). When reporting Veo render failures, include the exact API error message and the durationSeconds value — those two pieces of information solve most submission rejections.
