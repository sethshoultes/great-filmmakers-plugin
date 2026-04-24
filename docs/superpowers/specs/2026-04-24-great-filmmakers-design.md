---
title: Great Filmmakers Plugin — Design Spec
date: 2026-04-24
status: approved-for-planning
author: Seth Shoultes
related:
  - "[[great-minds-plugin]]"
  - "[[great-authors-plugin]]"
  - "[[model-selection-for-agents]]"
  - "[[pipeline-is-the-product]]"
  - "[[start-minimal-verify-expand]]"
  - "[[agents-hallucinate-apis]]"
---

# Great Filmmakers Plugin — Design Spec

A Claude Code plugin providing twelve filmmaker personas (directors, writers, craft specialists) plus workflow slash commands for scene breakdown, multi-discipline critique, and end-to-end film treatment generation. Third plugin in the Caseproof persona trilogy: **Great Minds** (strategic) → **Great Authors** (prose craft) → **Great Filmmakers** (film craft).

## Goals

1. Let writers and creative technologists channel film-craft judgment from canonical filmmakers on a blog post, manuscript chapter, or scene — to shape *how* it's structured for video, not who performs it.
2. Provide a cross-discipline fan-out (`/film-crew`) that takes source prose and produces a **HeyGen script in the exact format the existing `blog-to-video-generation` pipeline consumes**, plus supplementary craft artifacts (shot list, score notes, storyboards, edit notes) for the Remotion fallback path or for human reference.
3. The primary output — `film/screenplay/<slug>.heygen.md` — is a drop-in replacement for `data/heygen-scripts/<slug>.md` in the existing pipeline. A user can `cp` it into the pipeline's expected path and submit to HeyGen Video Agent with zero translation.
4. Share the project bible (`.great-authors/`) with the `great-authors` plugin so long-form projects have continuity across both plugins.

## Non-goals (v1.0)

- Calling HeyGen / ElevenLabs / Remotion APIs. The plugin emits artifacts compatible with the existing `blog-to-video-generation` pipeline at `garagedoorscience/`; actual API calls live in that pipeline, not this plugin.
- Managing HeyGen avatar assets, voice IDs, or the avatar catalog. The plugin references avatar identifiers the existing pipeline already has (Maya, Sara, Rick, Margaret, Seth); it does not create or manage them.
- DXT distribution. Deferred until the plugin is proven in real Claude Code use.
- Per-session journal analog, continuity checker, builders (shot-builder, cue-builder, storyboard-builder), `/filmmakers-draft`. All speculative until real use demands them.
- The 24-hour autonomous content factory (Minds → Authors → Filmmakers → render). That is a separate orchestrator project that consumes this plugin as a building block.

## Existing pipeline context

The user already runs a published blog-to-video pipeline at `garagedoorscience.com` via the `.claude/skills/blog-to-video-generation/` skill. The pipeline has two paths:

1. **Primary (99%) — HeyGen Video Agent.** Takes a HeyGen script (specific markdown format with avatar/voice frontmatter), submits to the HeyGen Video Agent, polls for completion, downloads the MP4, uploads to YouTube. Script format lives at `data/heygen-scripts/<slug>.md`.

2. **Fallback (1%) — Remotion + ElevenLabs.** Used only when HeyGen can't handle the required custom photos (inspection-specific, brand-specific). Generates voiceover via ElevenLabs TTS, mixes with topic-aware background music, composes in Remotion, uploads to YouTube.

Established persona-to-avatar mapping:

| Author | HeyGen Avatar Group | HeyGen Voice | Use For |
|--------|---------------------|--------------|---------|
| `maya` | `6b63c5d1884b4be69b1590a6b78280c0` | `53c69b4a1aeb44edbce2f050d7a5d3ca` | Maintenance, how-to |
| `sara` | `c70f62e006a948c3ac0c5226a8949311` | `6a2854113dd94fdfaf1f8eb51ebf5872` | Cost, buying |
| `rick` | `933d42ed41da4fc888c0aceca3b8ff0a` | `e209b585901e47d28b243e1a5dfc8747` | Comparisons, brand |
| `margaret` | `7115a4d1c6074ea987ea2aa899231056` | `f0240e6cefd541ac8031eeb9f3b71a82` | Safety, technical |
| `seth` | `e5ce268666144f26813642a37197de13` | (custom) | Announcements |

**The two persona layers — distinct and complementary:**

- **Great Filmmakers personas** (Scorsese, Kubrick, Kaufman, Rhimes, etc.) are *craft directors*. They shape HOW a script is structured — the hook, the peak shot, the music cue, the cut rhythm, the scene break.
- **Existing HeyGen avatars** (Maya, Sara, Rick, Margaret, Seth) are *performers*. They voice the script the filmmaker directed.

A single video can combine them: Scorsese's craft judgment directs Maya's performance. That's the orchestration `/film-crew` delivers.

## Informing learnings

- **[[start-minimal-verify-expand]]** — phase the plugin so v0.1 (foundation) ships and gets used before v1.0 orchestration lands.
- **[[pipeline-is-the-product]]** — invest in output format specifications (`docs/output-formats.md`) because downstream pipelines are the multiplier.
- **[[model-selection-for-agents]]** — ship `/filmmakers-critique` on Haiku from v1.0 (pattern proven in great-authors v0.6).
- **[[agents-hallucinate-apis]]** — filmmakers must read the bible before giving notes; never trust training memory for a specific project's world.

---

## Section 1 — Architecture overview

A standalone Claude Code plugin at `sethshoultes/great-filmmakers-plugin`, sibling to `great-authors-plugin`. Same structural pattern as great-authors:

- `.claude-plugin/` — plugin and marketplace manifests
- `agents/<name>-persona.md` — twelve filmmaker personas
- `skills/<command>/SKILL.md` — six slash commands
- `templates/film-project/` — scaffolding for the `film/` directory
- `scripts/lint-persona.sh` — structural validator, adapted for filmmaker section schema
- `docs/output-formats.md` — strict artifact format specs for pipeline consumers

No `daemon/`, `crons/`, `hooks/`, `distribution/` in v0.1 or v1.0. DXT deferred.

### Bible: shared with great-authors

`.great-authors/` is the project bible for the trilogy. Filmmakers read it exactly as authors do — characters, places, scenes, timeline, journal, voice, glossary. The directory name is legacy but retained because renaming it would break existing great-authors projects and force migration.

Filmmakers add one new section to `.great-authors/project.md`: a `## Film` block declaring the film output path and the current scene. Scaffolded by `/film-project-init`.

### Output: `film/` at project root

Filmmaker artifacts live in a new directory at project root, parallel to `manuscript/`:

```
my-project/
├── .great-authors/              # shared bible
├── manuscript/                  # prose (from great-authors)
│   └── chapter-01.md
└── film/                        # film artifacts (from great-filmmakers)
    ├── screenplay/
    ├── shot-lists/
    ├── score-notes/
    ├── storyboards/
    └── edit-notes/
```

Separation rationale: the bible is metadata consumed by both plugins; `manuscript/` is the prose manuscript; `film/` is the production treatment. Each has a clear owner.

### Invocation paths

1. **Direct dispatch** — `/filmmakers-channel scorsese` loads a persona into the main conversation. Save triggers capture generated content to the appropriate `film/` subdirectory (the user specifies which artifact type at save time).
2. **Orchestrated fan-out** — `/filmmakers-edit`, `/filmmakers-critique`, `/filmmakers-debate` use the `Agent` tool to spawn personas in parallel, isolated contexts, then consolidate.
3. **Pipeline** — `/film-crew <source-file>` runs a hybrid sequential+parallel pipeline: Kaufman adapts prose to screenplay first; then director + Deakins + Zimmer + Schoonmaker + Ferretti fan out in parallel from the screenplay. Each writes an artifact to its `film/` subdirectory.

### Model strategy

All agents default to `sonnet`. `/filmmakers-critique` overrides sub-agent dispatches to `haiku` at invocation time (pattern from great-authors v0.6) for cheap fast triage. `/film-crew` stays on Sonnet because each stage produces real artifacts, not opinions.

### Phasing

- **v0.1** — twelve agents + `/filmmakers-channel` + `/film-project-init` + `docs/output-formats.md` + validator + manifests. Personas usable standalone; bible integration working. Ship, use.
- **v1.0** — add `/filmmakers-edit`, `/filmmakers-critique`, `/filmmakers-debate`, `/film-crew`. Ship, tag v1.0.0.

Each phase independently useful. No release gates on pipeline integrations.

---

## Section 2 — Agent file format

Every filmmaker lives at `agents/<name>-persona.md`. Schema parallels great-authors but the body sections differ to accommodate craft-specific primary utility.

### Frontmatter

```yaml
---
name: scorsese-persona
description: "Use for scene breakdowns, kinetic camera design, music-driven storytelling, voiceover scripts, and moments that need moral voltage. Triggers: 'channel Scorsese,' 'Marty,' 'needle drop,' 'kinetic camera,' 'moral voltage.' Do NOT use for documentary, animation, or static/minimalist visual style. Examples:
- User: 'Break down this diner scene' → 'Scorsese will tell you the music, the move, the peak shot.'
- User: 'What song for this moment?' → 'Scorsese treats music like casting — he'll pick one.'"
model: sonnet
color: red
---
```

### Body — 9 sections

1. **Identity** — first-person opening paragraph. "You are Martin Scorsese. Not a summary, not an impression..."
2. **## Voice and visual grammar** — the craft signature. For composer: "Voice and sonic grammar." For editor: "Voice and cutting grammar."
3. **## Core principles** — iron rules, 4–8 bold-leading points.
4. **## Primary utility** — role-specific heading:
   - **Directors** (Kubrick, Kurosawa, Scorsese, Hitchcock, Spielberg, Lynch): `## How to break down a scene`
   - **Writers:** Rhimes → `## How to structure a script`; Kaufman → `## How to hook an opening`
   - **Deakins (DP):** `## How to shot-list a scene`
   - **Schoonmaker (editor):** `## How to find the cut`
   - **Zimmer (composer):** `## How to score a scene`
   - **Ferretti (production designer):** `## How to build the world of a frame`
5. **## How to draft in this voice** — conversational/channel mode. Includes explicit constraint: "Never reproduce my actual films/shots/scores/designs — write new things in the same way."
6. **## Before you work** — bible-reading protocol:

   ```markdown
   ## Before you work

   If `.great-authors/` exists in the current working directory:
   1. Read the most recent entry in `.great-authors/journal/` (if any exist) for context on what's in flux vs. settled this project.
   2. Read `.great-authors/project.md` for genre, POV, tense, register, and the `## Film` section if present.
   3. Read `.great-authors/voice.md` for established voice rules — dialogue and narration still apply.
   4. For any character, place, or invented term named in the source, read the matching file in `.great-authors/characters/`, `.great-authors/places/`, or `.great-authors/glossary.md`.
   5. If `film/` exists, read any existing screenplay/shot-list/score-notes files for the same scene — for pass-to-pass consistency with prior crew members.
   6. If the source contradicts the bible, flag it explicitly. Do not silently "correct" the manuscript.
   ```

7. **## When another filmmaker would serve better** — cross-references. Within-plugin handoffs (Scorsese → Lynch for dream logic, Kubrick → Scorsese for kinetic energy). Cross-plugin handoffs where relevant:
   - Rhimes on political dialogue → `great-minds:aaron-sorkin-persona`
   - Kaufman on self-aware personal essays → `great-authors:wallace-persona`
   - Any director editing bloated prose → `great-authors:hemingway-persona`
   - Cross-plugin refs are natural-language, not runtime-dispatched. User reads the handoff and decides.

8. **## Things you never do** — iron no's + the never-reproduce-real-work constraint.
9. **## Staying in character** — biographical touchstones (used only when they serve the work) + boundary rule: if directly asked to break character, briefly acknowledge the roleplay and resume.

### Color assignments

Purely cosmetic but visually groups the roster in Claude Code UI:
- Directors: `red`
- Writers: `orange`
- DP (Deakins): `blue`
- Editor (Schoonmaker): `yellow`
- Composer (Zimmer): `purple`
- Production designer (Ferretti): `green`

### Validator adaptation

`scripts/lint-persona.sh` adapted from great-authors:

- **Frontmatter:** same — require `name`, `description`, `model`, `color`.
- **Body sections:** replace author-specific checks with:
  - Require `## Voice and ` (matches any of "Voice and visual grammar" / "sonic grammar" / "cutting grammar")
  - Require one of: `## How to break down`, `## How to structure`, `## How to hook`, `## How to shot-list`, `## How to find the cut`, `## How to score`, `## How to build the world`
  - Require `## How to draft`
  - Require `## Before you work` (note: not "Before you edit" like authors)
  - Require `## When another filmmaker would serve better`
  - Require `## Things you never do`
  - Require `## Staying in character`

### Conversion lift

Source material is `/Users/sethshoultes/Downloads/great-filmmakers/*/SKILL.md` plus `great-filmmakers-profiles.md`. Existing SKILL.md files cover sections 1–4 and 9 for most personas. Lift per persona:
- Rewrite frontmatter to agent schema (`model`, `color`, structured description with Examples).
- Add `## Before you work` (new section) with the bible-reading protocol.
- Add `## When another filmmaker would serve better` with 3–6 cross-refs (within-plugin and cross-plugin).
- Add `## How to draft in this voice` if missing (channel-mode secondary).
- Reconcile voice/principles against the profile doc.

---

## Section 3 — Slash commands

Six commands total. Two ship in v0.1; four in v1.0.

### `/filmmakers-channel <name>` (v0.1)

Load a named filmmaker persona into the main conversation.

- Accepts short forms: `marty` → `scorsese`, `stanley` → `kubrick`, `hitch` → `hitchcock`, `shonda` → `rhimes`.
- If `.great-authors/` exists in cwd, the persona reads it per its `## Before you work` protocol.
- **Save triggers** for generated content, following great-authors v0.7 pattern:
  - "save as heygen script" or "save as screenplay" → append last prose block to `film/screenplay/<current>.heygen.md` (the primary HeyGen-compatible format)
  - "save as shot list" → `film/shot-lists/<current>.md`
  - "save as score notes" → `film/score-notes/<current>.md`
  - "save as storyboard" → `film/storyboards/<current>.md`
  - "save as edit notes" → `film/edit-notes/<current>.md`
  - "save that" (ambiguous) → asks which artifact type first, with the HeyGen script as the default
- `<current>` resolved from `.great-authors/project.md`'s `## Film > Current scene` field.

### `/film-project-init` (v0.1)

Scaffolds the `film/` directory and adds the `## Film` section to `.great-authors/project.md`.

- If `.great-authors/` doesn't exist, tells the user to run `/authors-project-init` first (from great-authors) and stops.
- Asks for the starting scene slug (default: `scene-01` or infer from the latest manuscript chapter).
- Creates `film/screenplay/`, `film/shot-lists/`, `film/score-notes/`, `film/storyboards/`, `film/edit-notes/` (all empty, with `.gitkeep`).
- Adds to `.great-authors/project.md`:

  ```markdown
  ## Film

  **Path:** `film/` (at project root, sibling to `manuscript/`)
  **Current scene:** `scene-01` (or user-chosen slug)

  Commands that generate film artifacts (`/filmmakers-channel` with save triggers, `/film-crew`) write to `film/<subdir>/<current-scene>.md` by default. Update `Current scene` when you move to the next.
  ```

### `/filmmakers-edit <file> [filmmaker...]` (v1.0)

Fan out a source file (prose or existing screenplay) to 1–2 filmmaker personas. Each returns a scene breakdown in their role's primary-utility format. Consolidation combines into one view — consensus, sharpest disagreement, single highest-leverage change, handoffs.

- Auto-selection when no filmmakers named: read genre signals from the source + `.great-authors/project.md`. Kinetic drama → Scorsese; suspense → Hitchcock; arthouse → Lynch; populist spectacle → Spielberg; serialized dialogue → Rhimes + Kaufman; cold formalism → Kubrick.
- Fan-out is parallel via the `Agent` tool.
- Output to stdout only; user explicitly saves with `/filmmakers-channel`-style save triggers afterward if desired. `/filmmakers-edit` does not write files directly.

### `/filmmakers-critique <file> [filmmaker...]` (v1.0)

Fast 3-bullet verdicts from 3 filmmakers in parallel. Haiku-dispatched.

- Default triad: one director + one writer + one craft specialist (e.g., Scorsese + Rhimes + Deakins) — covers three dimensions.
- TERSE output — 3 bullets per filmmaker, no rewrites, no markup.
- Consolidation: one-line consensus + one-line sharpest disagreement + any handoffs surfaced.

### `/filmmakers-debate <passage-or-topic> <a> <b>` (v1.0)

Two-round craft dispute between two filmmakers. Same 2-round + consolidation structure as `/authors-debate`.

- Obvious pairings: Kubrick vs. Scorsese (control vs. kinetic); Hitchcock vs. Spielberg (suspense vs. emotion); Deakins vs. Ferretti (light vs. set); Kaufman vs. Rhimes (structural invention vs. serial momentum).
- Users pass both names; no auto-pairing.

### `/film-crew <source-file> [--director <name>] [--avatar <name>]` (v1.0) — the unique value

The pipeline command. Turns a source file (blog post, manuscript chapter, scene notes) into a HeyGen-ready script plus supplementary craft artifacts across five specialist outputs.

**Execution model: hybrid sequential + parallel.**

**Stage 1 (sequential) — Kaufman adapts prose into a HeyGen script.** Charlie Kaufman is the default adapter; his structural sensibility carries prose-to-script best. Override with `--writer rhimes` for serialized/episodic work. Output goes to `film/screenplay/<slug>.heygen.md` in the exact format Section 4 specifies — drop-in replacement for the existing pipeline's `data/heygen-scripts/<slug>.md`.

**Stage 2 (parallel fan-out) — specialists produce supplementary artifacts from the HeyGen script:**

- Director (default Scorsese, override `--director <name>`) writes scene-breakdown notes → `film/edit-notes/<slug>.md` (director section). The director's craft notes are ALSO embedded inline in the HeyGen script as "Director's note:" lines per-scene, so the HeyGen output carries the craft direction even if the other artifacts are ignored.
- Deakins writes shot list → `film/shot-lists/<slug>.md`. Used only by the Remotion fallback path (HeyGen generates its own visuals).
- Zimmer writes score notes → `film/score-notes/<slug>.md`. Used only by the Remotion fallback path; the HeyGen agent picks music independently.
- Schoonmaker writes cut notes → `film/edit-notes/<slug>.md` (editor section, after `---`). Informs pace and scene boundaries in both paths.
- Ferretti writes world/set notes → `film/storyboards/<slug>.md`. Used only by the Remotion fallback path; HeyGen generates its own visuals.

All five specialists dispatched in a single Agent tool message (parallel).

**Stage 3 (consolidation)** — single-line summary to stdout: primary output path, supplementary artifact count, next-step suggestion (e.g., "HeyGen script ready at `film/screenplay/<slug>.heygen.md`. Copy to `data/heygen-scripts/<slug>.md` and run the existing pipeline, or run `/filmmakers-debate 'the opening move' scorsese kubrick` if you're unsure about pace.").

**Arguments:**

- `<source-file>` (required) — path to the source prose. Can be a blog MDX file, manuscript chapter, scene notes.
- `--director <name>` (optional) — override the default director. Valid: any great-filmmakers director (scorsese, kubrick, hitchcock, kurosawa, spielberg, lynch).
- `--writer <name>` (optional) — override Kaufman as the adapter. Valid: `kaufman`, `rhimes`.
- `--avatar <name>` (optional) — HeyGen avatar that will perform. Valid: `maya`, `sara`, `rick`, `margaret`, `seth`. If omitted, auto-select by inspecting source classification (e.g., MDX frontmatter's `classification: maintenance` → maya; `cost` → sara; `comparison` → rick; `safety` → margaret). Default fallback: `maya`.
- `--voice-id <id>` (optional) — override the HeyGen voice ID. If omitted, derived from the avatar selection.
- `--scene <slug>` (optional) — override the slug (defaults to source file's basename).

**Avatar → Writer defaults for serialized content:** if `--avatar sara` and no `--writer` passed, auto-default to `rhimes` (scrappy/growth-minded + serialized momentum is her wheelhouse). Writable but predictable.

**Output compatibility:** the primary output (`film/screenplay/<slug>.heygen.md`) matches the existing pipeline's HeyGen script format exactly. A shell one-liner gets it into the pipeline:

```bash
cp film/screenplay/<slug>.heygen.md ../garagedoorscience/data/heygen-scripts/<slug>.md
# Then run the existing HeyGen submit step in that project.
```

Future versions may add an `--emit <path>` flag that writes directly to a sibling pipeline's expected path, but v1.0 keeps file I/O inside the plugin's own `film/` tree for clean boundaries.

### Shared behavior

- All commands read the bible if `.great-authors/` exists in cwd.
- All sub-agent dispatches inherit cwd; personas read their own `## Before you work` protocol files.
- `/film-crew` is the only command that writes manuscript-like content to disk during a command invocation; others rely on save triggers.
- Cross-plugin orchestration is out of scope — commands don't dispatch into `great-authors` or `great-minds`. Handoffs appear as suggestions in output.

---

## Section 4 — Output format specifications

`docs/output-formats.md` documents strict formats for each `film/*` artifact type. This is the contract between the plugin and downstream pipelines (the existing `garagedoorscience/blog-to-video-generation` pipeline, and future pipelines that copy its interface).

The screenplay format is **a drop-in replacement** for the existing pipeline's HeyGen script at `data/heygen-scripts/<slug>.md`. The other artifacts (shot list, score notes, storyboards, edit notes) serve the Remotion fallback path and human direction; HeyGen itself generates its own visuals and ignores them.

Every artifact ends with a `## Machine-readable footer` section containing YAML that downstream tools can parse without processing the human-readable body.

### `film/screenplay/<slug>.heygen.md` — PRIMARY, matches existing HeyGen script format

Exact-match format from `garagedoorscience/.claude/skills/blog-to-video-generation/SKILL.md`. The filename uses `.heygen.md` suffix so the existing pipeline can pick it up unchanged by copying to `data/heygen-scripts/<slug>.md`.

**Frontmatter (required — the existing pipeline reads these fields):**

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

Two fields are new for this plugin (additive, don't break existing consumers):
- `director` — which great-filmmakers persona shaped the craft (affects pacing, peak shot, cut rhythm in the scene breakdown)
- `adapter` — which writer persona adapted the source prose (Kaufman or Rhimes)

**Body — fixed sections matching the existing skill's template:**

```markdown
# <Title> — HeyGen Script

## Visual Setup
- **Avatar:** <avatar_name> (<brief direction, e.g., warm expression, approachable>)
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

**Director's note** is the great-filmmakers-specific addition. HeyGen ignores it (not a standard field), but a human director or a future pipeline that chains filmmaker → HeyGen can read it to refine the storyboard prompt. Scorsese's note might be "hold on the peak image for 2 seconds before cutting to the dialogue"; Kubrick's might be "center-frame everything, no handheld."

**Machine-readable footer:**

```yaml
## Machine-readable footer

scene_id: garage-door-opener-lifespan
source_file: content/blog/garage-door-opener-lifespan.mdx
adapter: kaufman
director: scorsese
avatar: maya
target_duration_seconds: 45
scenes:
  - id: scene-1
    name: The Hook
    start_sec: 0
    end_sec: 8
  - id: scene-2
    name: Drive Type Breakdown
    start_sec: 8
    end_sec: 35
total_scenes: 4
voiceover_only: true
```

**Consumers use:**
- The existing `blog-to-video-generation` pipeline reads frontmatter + body + ignores the machine-readable footer — unchanged from today.
- A future orchestrator reads the machine-readable footer to route jobs without parsing prose.
- `/film-crew` regeneration can diff against the footer to avoid re-work.

### `film/shot-lists/<slug>.md`

**Human-readable body:** a table.

```
| # | Shot type         | Duration | Description                                 | B-roll / notes                  |
|---|-------------------|----------|---------------------------------------------|---------------------------------|
| 1 | Wide establishing | 3s       | Exterior diner, neon sign, rain.            | Static; tripod.                 |
| 2 | Push-in on door   | 2s       | Door BANGS open; camera pushes to threshold.| Steadicam.                      |
| 3 | POV from threshold| 3s       | Marcus's POV: diner interior, Elena behind counter. | Wide lens; handheld.     |
```

**Machine-readable footer:**

```yaml
scene_id: ch14-confrontation
dp: deakins
total_shots: 12
total_duration_seconds: 75
lens_notes: natural light preferred; key fill from practical booth lamps
pipeline_hints:
  remotion:
    frame_rate: 30
    total_frames: 2250
```

**Consumers use:** `total_duration_seconds` and per-shot durations for Remotion composition timing; `pipeline_hints.remotion.*` directly feeds Remotion render configs.

### `film/score-notes/<slug>.md`

**Human-readable body:** cue list table + Zimmer's prose reasoning.

**Machine-readable footer:**

```yaml
scene_id: ch14-confrontation
composer: zimmer
cues:
  - id: cue-01
    start_sec: 0
    end_sec: 30
    mood: tense
    instrumentation: [low_strings, heartbeat_percussion]
    reference_track: "there will be blood - there will be blood"
  - id: cue-02
    start_sec: 30
    end_sec: 75
    mood: release
    instrumentation: [piano_solo]
    reference_track: null
music_prompt_tags: [tense, minor-key, strings, low-register]
```

**Consumers use:** `music_prompt_tags` directly drive the existing `musicPromptFor()` helper in `garagedoorscience/remotion/scripts/lib/music-prompt.ts`. `cues[]` drive per-segment music generation.

### `film/storyboards/<slug>.md`

**Human-readable body:** Ferretti's prose descriptions of sets, props, lighting, period detail — one block per shot referencing the shot-list IDs.

**Machine-readable footer:**

```yaml
scene_id: ch14-confrontation
production_designer: ferretti
location: diner
period: contemporary
key_props: [coffee_mug_diner_china, newspaper_local_daily, bell_over_door]
color_palette: [burnt_orange, cold_fluorescent_green, booth_red]
mood_references: ["nighthawks - hopper", "goodfellas - diner scenes"]
```

**Consumers use:** `color_palette` and `mood_references` for Remotion composition color grading hints. `key_props` for asset/b-roll library lookup.

### `film/edit-notes/<slug>.md`

**Human-readable body:** director's notes (Scorsese or whoever) followed by `---` followed by Schoonmaker's cut notes.

**Machine-readable footer:**

```yaml
scene_id: ch14-confrontation
director: scorsese
editor: schoonmaker
pace: kinetic
peak_shot_id: shot-07
voiceover_required: true
cut_points:
  - shot_id: shot-03
    reason: moral stake hits
  - shot_id: shot-07
    reason: peak image — hold
```

**Consumers use:** `pace` and `cut_points[]` inform Remotion composition flow. `peak_shot_id` flags which shot deserves extra render attention (longer hold, higher-quality asset).

### Format stability guarantee

The footer YAML schema is the stable interface for downstream pipelines. v0.1 and v1.0 of this plugin share the same footer schema. Future additive fields are allowed; removing fields requires a major version bump.

---

## Section 5 — Repo structure

```
great-filmmakers-plugin/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── agents/
│   ├── kubrick-persona.md
│   ├── kurosawa-persona.md
│   ├── scorsese-persona.md
│   ├── hitchcock-persona.md
│   ├── spielberg-persona.md
│   ├── lynch-persona.md
│   ├── rhimes-persona.md
│   ├── kaufman-persona.md
│   ├── deakins-persona.md
│   ├── schoonmaker-persona.md
│   ├── zimmer-persona.md
│   └── ferretti-persona.md
├── skills/
│   ├── filmmakers-channel/SKILL.md     # v0.1
│   ├── film-project-init/SKILL.md      # v0.1
│   ├── filmmakers-edit/SKILL.md        # v1.0
│   ├── filmmakers-critique/SKILL.md    # v1.0
│   ├── filmmakers-debate/SKILL.md      # v1.0
│   └── film-crew/SKILL.md              # v1.0
├── templates/
│   └── film-project/
│       ├── screenplay/.gitkeep
│       ├── shot-lists/.gitkeep
│       ├── score-notes/.gitkeep
│       ├── storyboards/.gitkeep
│       └── edit-notes/.gitkeep
├── scripts/
│   └── lint-persona.sh
├── docs/
│   ├── profiles.md
│   ├── output-formats.md
│   └── superpowers/
│       ├── specs/2026-04-24-great-filmmakers-design.md
│       └── plans/
├── package.json
├── LICENSE
├── .gitignore
└── README.md
```

### What's deliberately absent (vs. great-authors)

- No `distribution/` or `dxt/` — deferred.
- No builder agents (shot-builder, cue-builder, etc.) — speculative until real use proves they're needed.
- No `/filmmakers-draft` — `/filmmakers-channel` covers conversational drafting; `/film-crew` covers structured drafting.
- No `/filmmakers-journal` or `/filmmakers-consolidate` — the shared bible already has `.great-authors/journal/`.
- No `/filmmakers-continuity` — speculative; the shared bible's protocol already makes personas bible-aware.

### Install

- Local: `~/Local Sites/great-filmmakers-plugin/`
- Remote: `github.com/sethshoultes/great-filmmakers-plugin`
- Install command:
  ```
  /plugin marketplace add sethshoultes/great-filmmakers-plugin
  /plugin install great-filmmakers@sethshoultes
  ```

---

## Section 6 — Deferred work & roadmap

Explicitly captured to prevent feature creep and to preserve design rationale when future sessions pick up.

### Post-v1.0 candidates

- **DXT package for Claude Desktop** — same pattern as great-authors-plugin v1.0. Defer until the plugin has run real film treatments and the persona prompts are stable.
- **Builders** — parallel to great-authors character-builder/scene-builder. Candidates:
  - `shot-builder` — interactive interview to build a single shot entry with framing, lens, movement, mood.
  - `cue-builder` — interactive score cue entry with reference track, instrumentation, emotional target.
  - `storyboard-builder` — interactive per-shot production design entry.
  - `character-actor-lookbook-builder` — extends `characters/` entries with visual casting notes.
  - Ship builders driven by real workflow pain, not in one speculative batch.
- **`/filmmakers-continuity`** — audits a scene's artifacts against each other (screenplay dialogue references a prop not in storyboard; shot list duration doesn't match score timing). Worth it once multiple scenes have been run through the pipeline and divergences become visible.
- **`/filmmakers-draft`** — voice-takeover drafting parallel to great-authors v0.4. Currently covered by `/filmmakers-channel` with save triggers. Add if explicit-brief drafting becomes a common pattern.
- **Additional personas** flagged in transfer notes: Tarkovsky, Wong Kar-wai, Varda, Coppola, Miyazaki, Morricone (alternative to Zimmer). Driven by gaps surfaced in use.
- **Cross-plugin orchestration** — e.g., a `/from-post` command that chains great-authors editing → great-filmmakers film-crew → emits pipeline-ready artifacts. Lives in a separate content-pipeline project, not this plugin.

### Phase 3 / separate projects

- **24-hour autonomous content factory** — Minds develops software → Authors write story → Filmmakers produce film treatment → ElevenLabs + Remotion render. Uses all three plugins as building blocks. Lives as its own orchestrator project.
- **HeyGen integration** — currently the existing user pipeline uses ElevenLabs. If HeyGen becomes a target, add an adapter in the content-pipeline project, not in this plugin.

### Intentionally out of scope

- **Rendering video from this plugin.** Plugin emits artifacts; rendering belongs downstream.
- **Daemon / cron / Ralph Wiggum loop.** Film treatment is human-in-the-loop work.
- **Cross-project memory beyond `.great-authors/`.** Each project is its own bible.
- **The whole trilogy orchestrator.** That's a separate project.

---

## Success criteria

- **v0.1 works when:** a user with an existing `.great-authors/`-equipped project can install, run `/film-project-init` to add `film/`, then `/filmmakers-channel scorsese` and get scene-breakdown feedback in Scorsese's voice. At least one save trigger correctly writes to `film/<subdir>/<slug>.md`.
- **v1.0 works when:** `/film-crew content/blog/garage-door-opener-lifespan.mdx --director scorsese --avatar maya` produces a valid HeyGen script at `film/screenplay/garage-door-opener-lifespan.heygen.md` that parses against the existing pipeline's format, plus four supplementary artifacts in under three minutes. The HeyGen script's Director's note lines carry Scorsese-flavored craft direction (peak shot, pace, cut rhythm).
- **The real test:** copying `film/screenplay/<slug>.heygen.md` to `garagedoorscience/data/heygen-scripts/<slug>.md`, then running the existing pipeline's HeyGen Video Agent submit step, produces an avatar-narrated video — no glue code, no prose parsing, no translation.

## Open risks

- **HeyGen script format drift.** The existing pipeline's script format (frontmatter + sections) is our primary output target. If the pipeline changes its format, our plugin output silently diverges. Mitigation: `docs/output-formats.md` is cross-referenced to `garagedoorscience/.claude/skills/blog-to-video-generation/SKILL.md`; any update to that skill triggers a review of ours.
- **Additive frontmatter fields (`director`, `adapter`) might break the existing pipeline.** If the pipeline strictly validates frontmatter, the new fields cause rejection. Mitigation: verify the pipeline ignores unknown fields (common in YAML parsing) before shipping; if not, gate the new fields behind a flag.
- **Output format footer churn.** The plugin's own machine-readable YAML footer is separate from the HeyGen frontmatter; future orchestrators depend on it. Versioned in `docs/output-formats.md`; additive changes only.
- **Kaufman defaulting as adapter.** He might not suit every genre (e.g., pure action, short-form instructional). If `/film-crew` produces bad scripts on specific classifications, auto-select by classification (e.g., `safety` → Rhimes for procedural clarity) or user overrides with `--writer`.
- **Cross-plugin handoffs are natural-language only.** User must recognize and act on them. If friction, a future `/filmmakers-handoff` command could explicitly route — deferred.
- **`.great-authors/` directory name** is legacy but persistent. Cleanest rename would break every existing bible; accepted cost.
- **Scorsese defaulting as director in `/film-crew`.** Reasonable for drama but wrong for horror/comedy/action/instructional. User overrides with `--director`; auto-selection from classification is a v1.1 improvement if needed.

## Next step

After user sign-off, hand off to the superpowers `writing-plans` skill to produce v0.1 and v1.0 implementation plans (two plans, shipped sequentially).
