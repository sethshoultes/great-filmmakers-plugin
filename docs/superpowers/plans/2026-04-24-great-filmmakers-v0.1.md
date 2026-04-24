# Great Filmmakers v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship v0.1 of the `great-filmmakers` Claude Code plugin — twelve filmmaker persona agents converted to agent format, plus two bootstrap slash commands (`/filmmakers-channel` and `/film-project-init`) and the output-formats documentation that the v1.0 `/film-crew` command will honor.

**Architecture:** A Claude Code plugin. Twelve personas in `agents/<name>-persona.md`, two slash commands in `skills/<name>/SKILL.md`, a `templates/film-project/` tree for scaffolding `film/` directories in user projects, `scripts/lint-persona.sh` adapted from great-authors (new required-section list), and `docs/output-formats.md` documenting the strict `.heygen.md`, `.veo3.md`, and `.remotion.md` artifact formats that v1.0 will produce.

**Tech stack:** Bash + markdown + YAML frontmatter. JSON for plugin manifests. Git for version control. No runtime code — the plugin is structured content.

**Source material:**

- `/Users/sethshoultes/Downloads/great-filmmakers/*/SKILL.md` — twelve existing SKILL files to convert to agent format
- `/Users/sethshoultes/Downloads/great-filmmakers/great-filmmakers-profiles.md` — authoritative profile reference
- `/Users/sethshoultes/Downloads/great-filmmakers/claude-code-transfer-notes.md` — build-order recommendations and design decisions
- `/Users/sethshoultes/Local Sites/great-authors-plugin/agents/hemingway-persona.md` — agent-format template (structurally the closest analog, though body sections differ)
- `/Users/sethshoultes/Local Sites/great-authors-plugin/scripts/lint-persona.sh` — validator to adapt
- `/Users/sethshoultes/Local Sites/great-authors-plugin/.claude-plugin/plugin.json` — manifest reference
- `/Users/sethshoultes/Local Sites/garagedoorscience/.claude/skills/blog-to-video-generation/SKILL.md` — HeyGen script format reference for `docs/output-formats.md`
- `/Users/sethshoultes/Local Sites/veo-builder/app.py` — Veo 3 production doc format reference for `docs/output-formats.md`

**Repo:** `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/` (already initialized; spec is committed). GitHub remote: `sethshoultes/great-filmmakers-plugin` (does not exist yet; created in final task).

**Build order for persona conversion** (from transfer notes): Scorsese → Kubrick → Rhimes → Deakins → Schoonmaker → Kurosawa → Hitchcock → Spielberg → Lynch → Kaufman → Zimmer → Ferretti. Scorsese first establishes the director template; the order exercises each specialty band early.

---

## File structure for v0.1

```
great-filmmakers-plugin/
├── .claude-plugin/
│   ├── plugin.json                      # Task 2
│   └── marketplace.json                 # Task 2
├── agents/                              # 12 files, Tasks 10–21
│   ├── scorsese-persona.md              # Task 10 (template director)
│   ├── kubrick-persona.md               # Task 11
│   ├── rhimes-persona.md                # Task 12 (template writer)
│   ├── deakins-persona.md               # Task 13 (template DP)
│   ├── schoonmaker-persona.md           # Task 14 (template editor)
│   ├── kurosawa-persona.md              # Task 15
│   ├── hitchcock-persona.md             # Task 16
│   ├── spielberg-persona.md             # Task 17
│   ├── lynch-persona.md                 # Task 18
│   ├── kaufman-persona.md               # Task 19
│   ├── zimmer-persona.md                # Task 20 (template composer)
│   └── ferretti-persona.md              # Task 21 (template production designer)
├── skills/
│   ├── filmmakers-channel/SKILL.md      # Task 9
│   └── film-project-init/SKILL.md       # Task 8
├── templates/
│   └── film-project/                    # Task 7
│       ├── screenplay/.gitkeep
│       ├── shot-lists/.gitkeep
│       ├── score-notes/.gitkeep
│       ├── storyboards/.gitkeep
│       └── edit-notes/.gitkeep
├── scripts/
│   └── lint-persona.sh                  # Task 5
├── docs/
│   ├── profiles.md                      # Task 3
│   ├── output-formats.md                # Task 6
│   └── superpowers/
│       ├── specs/2026-04-24-great-filmmakers-design.md   # already exists
│       └── plans/2026-04-24-great-filmmakers-v0.1.md     # this file
├── package.json                         # Task 2
├── LICENSE                              # Task 2
├── .gitignore                           # Task 2
└── README.md                            # Task 24 (final update)
```

---

## Tasks

### Task 1: Verify repo state

- [ ] **Step 1: Confirm current state**

Run:
```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git log --oneline && git status
```

Expected output: three commits exist (e10b117 initial spec, df6b7ec HeyGen correction, 81772f2 Veo 3 addition); clean working tree; branch is `master` or `main`.

If the tree is dirty, stop and resolve before proceeding.

- [ ] **Step 2: Confirm source material exists**

Run:
```bash
ls -la "/Users/sethshoultes/Downloads/great-filmmakers/" | grep -E "(persona|profiles)" | wc -l
```

Expected: `13` (12 persona dirs + 1 profiles doc).

If any source file is missing, stop. The user must restore it.

No commit for this task.

---

### Task 2: Scaffold plugin manifests, metadata, and .gitignore

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `package.json`
- Create: `LICENSE`
- Create: `.gitignore`

- [ ] **Step 1: Create plugin.json**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/.claude-plugin/plugin.json`:

```json
{
  "$schema": "https://anthropic.com/claude-code/plugin.schema.json",
  "name": "great-filmmakers",
  "version": "0.1.0",
  "description": "Twelve filmmaker personas (6 directors + 2 writers + 4 craft specialists) plus slash commands for scene breakdown and film-craft work. Third in the Caseproof persona trilogy — companion to great-minds-plugin and great-authors-plugin.",
  "author": {
    "name": "Seth Shoultes",
    "url": "https://github.com/sethshoultes"
  },
  "repository": "https://github.com/sethshoultes/great-filmmakers-plugin",
  "license": "MIT",
  "keywords": ["filmmaking", "directing", "cinematography", "screenwriting", "scene-breakdown", "personas", "film-craft", "claude-code-plugin"]
}
```

- [ ] **Step 2: Create marketplace.json**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/.claude-plugin/marketplace.json`:

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "great-filmmakers",
  "description": "Twelve filmmaker personas + slash commands for scene breakdown and film-craft work. Companion to great-authors-plugin.",
  "owner": {
    "name": "Seth Shoultes",
    "url": "https://github.com/sethshoultes"
  },
  "plugins": [
    {
      "name": "great-filmmakers",
      "description": "12 filmmaker personas + /filmmakers-channel + /film-project-init (v0.1). /film-crew and more orchestration commands in v1.0.",
      "source": "./",
      "category": "productivity"
    }
  ]
}
```

- [ ] **Step 3: Create package.json**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/package.json`:

```json
{
  "name": "great-filmmakers",
  "version": "0.1.0",
  "description": "Twelve filmmaker personas + slash commands for scene breakdown and film-craft work.",
  "author": "Seth Shoultes <seth@caseproof.com>",
  "repository": "github:sethshoultes/great-filmmakers-plugin",
  "license": "MIT",
  "keywords": ["filmmaking", "personas", "claude-code-plugin"]
}
```

- [ ] **Step 4: Create LICENSE**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/LICENSE`:

```
MIT License

Copyright (c) 2026 Seth Shoultes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 5: Create .gitignore**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/.gitignore`:

```
.DS_Store
node_modules/
*.log
*.dxt
```

- [ ] **Step 6: Validate JSON files**

Run:
```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))" && \
  python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))" && \
  python3 -c "import json; json.load(open('package.json'))" && \
  echo OK
```

Expected: `OK`.

- [ ] **Step 7: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add .claude-plugin/ package.json LICENSE .gitignore && \
  git commit -m "chore: scaffold plugin manifests, metadata, and .gitignore"
```

---

### Task 3: Copy profiles doc into repo

**Files:**
- Create: `docs/profiles.md`

- [ ] **Step 1: Copy source**

Run:
```bash
cp "/Users/sethshoultes/Downloads/great-filmmakers/great-filmmakers-profiles.md" \
   "/Users/sethshoultes/Local Sites/great-filmmakers-plugin/docs/profiles.md"
```

- [ ] **Step 2: Verify copy**

Run:
```bash
head -3 "/Users/sethshoultes/Local Sites/great-filmmakers-plugin/docs/profiles.md"
```

Expected first line: `# Great Filmmakers — Persona Profiles`

- [ ] **Step 3: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add docs/profiles.md && \
  git commit -m "docs: add authoritative filmmaker profiles reference"
```

---

### Task 4: Copy transfer notes into repo (reference, not working doc)

**Files:**
- Create: `docs/transfer-notes.md`

Transfer notes from the user's earlier session explain the design rationale (trilogy framing, cross-plugin references, build order). Preserving them in-repo keeps the context discoverable.

- [ ] **Step 1: Copy**

```bash
cp "/Users/sethshoultes/Downloads/great-filmmakers/claude-code-transfer-notes.md" \
   "/Users/sethshoultes/Local Sites/great-filmmakers-plugin/docs/transfer-notes.md"
```

- [ ] **Step 2: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add docs/transfer-notes.md && \
  git commit -m "docs: add transfer notes for design rationale and build order"
```

---

### Task 5: Write the persona validator script

**Files:**
- Create: `scripts/lint-persona.sh`

Enforces the filmmaker persona structure defined in Section 2 of the spec. Different required sections than great-authors' validator — this one checks for role-specific primary utility headings.

- [ ] **Step 1: Write the failing test — run against nonexistent file**

Run:
```bash
bash "/Users/sethshoultes/Local Sites/great-filmmakers-plugin/scripts/lint-persona.sh" agents/scorsese-persona.md 2>&1 || echo "FAIL as expected"
```

Expected: `bash: ...scripts/lint-persona.sh: No such file or directory` followed by `FAIL as expected`

- [ ] **Step 2: Write the validator**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/scripts/lint-persona.sh`:

```bash
#!/usr/bin/env bash
# lint-persona.sh <path-to-persona-file>
#
# Verifies a filmmaker persona file has the required structure defined in
# docs/superpowers/specs/2026-04-24-great-filmmakers-design.md Section 2.
#
# Exit codes: 0 = pass, 1 = fail

set -euo pipefail

file="${1:-}"
if [[ -z "$file" ]]; then
  echo "usage: $0 <persona-file>" >&2
  exit 1
fi

if [[ ! -f "$file" ]]; then
  echo "FAIL: file does not exist: $file" >&2
  exit 1
fi

errors=0

check_contains() {
  local pattern="$1"
  local label="$2"
  if ! grep -qE "$pattern" "$file"; then
    echo "FAIL: missing $label" >&2
    errors=$((errors + 1))
  fi
}

check_frontmatter_field() {
  local field="$1"
  if ! head -30 "$file" | grep -qE "^${field}: "; then
    echo "FAIL: missing frontmatter field: $field" >&2
    errors=$((errors + 1))
  fi
}

# Frontmatter must open on line 1
if ! head -1 "$file" | grep -qE '^---$'; then
  echo "FAIL: file does not start with YAML frontmatter" >&2
  errors=$((errors + 1))
fi

check_frontmatter_field "name"
check_frontmatter_field "description"
check_frontmatter_field "model"
check_frontmatter_field "color"

# Required body sections. "Voice and ..." matches visual/sonic/cutting grammar variants.
check_contains "^## Voice and " "Voice and <grammar> section"

# Role-specific primary utility — require ONE of these headings.
check_contains "^## How to (break down|structure|hook|shot-list|find the cut|score|build the world)" \
  "primary-utility section (one of: break down, structure, hook, shot-list, find the cut, score, build the world)"

check_contains "^## How to draft" "How to draft section"
check_contains "^## Before you work" "Before you work protocol"
check_contains "^## When another filmmaker would serve better" "cross-reference section"
check_contains "^## Things you never do" "Things you never do section"
check_contains "^## Staying in character" "Staying in character footer"

if [[ $errors -gt 0 ]]; then
  echo "FAIL: $errors validation error(s) in $file" >&2
  exit 1
fi

echo "PASS: $file"
```

- [ ] **Step 3: Make executable**

```bash
chmod +x "/Users/sethshoultes/Local Sites/great-filmmakers-plugin/scripts/lint-persona.sh"
```

- [ ] **Step 4: Run against nonexistent file — expect FAIL**

Run:
```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  ./scripts/lint-persona.sh agents/scorsese-persona.md 2>&1; echo "exit=$?"
```

Expected: `FAIL: file does not exist: agents/scorsese-persona.md` and `exit=1`.

- [ ] **Step 5: Run against README.md (no persona structure) — expect FAIL**

Run:
```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  ./scripts/lint-persona.sh README.md 2>&1; echo "exit=$?"
```

Expected: multiple `FAIL:` lines for missing frontmatter fields and sections; `exit=1`.

- [ ] **Step 6: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add scripts/lint-persona.sh && \
  git commit -m "chore: add filmmaker persona structural validator"
```

---

### Task 6: Write docs/output-formats.md

**Files:**
- Create: `docs/output-formats.md`

The stable contract between this plugin's eventual `/film-crew` output and downstream pipelines (garagedoorscience blog-to-video, veo-builder dashboard). Ships in v0.1 so the persona files and skills can reference it, even though `/film-crew` itself is v1.0.

- [ ] **Step 1: Write the file**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/docs/output-formats.md`:

```markdown
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
veo_model: veo-3.1-fast
aspect_ratio: 16:9
ingredient_images:
  cast:
    - CAST/<abbrev>.jpg
  locations:
    - LOCATIONS/<location_slug>.jpg
```

### Which persona fills which section

- **CAST:** Ferretti (physical/costume specificity) + writer (names and roles)
- **LOCATIONS:** Ferretti
- **VISUAL GRAMMAR:** Deakins (camera + lens + movement vocabulary)
- **NEGATIVE PROMPT:** Ferretti + director (things that violate director's non-negotiables)
- **SHOT LIST prompts:** director + writer using VISUAL GRAMMAR terms, with Deakins consulting on camera, Ferretti on set/prop detail, Zimmer's audio cues embedded
- **Durations:** Schoonmaker (cut rhythm determines shot length)

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
```

- [ ] **Step 2: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add docs/output-formats.md && \
  git commit -m "docs: add output-formats.md — stable contract for v1.0 /film-crew"
```

---

### Task 7: Write templates/film-project scaffolding

**Files:**
- Create: `templates/film-project/screenplay/.gitkeep`
- Create: `templates/film-project/shot-lists/.gitkeep`
- Create: `templates/film-project/score-notes/.gitkeep`
- Create: `templates/film-project/storyboards/.gitkeep`
- Create: `templates/film-project/edit-notes/.gitkeep`

Empty directory scaffolding that `/film-project-init` copies into a user project's `film/` directory.

- [ ] **Step 1: Create the tree**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  mkdir -p templates/film-project/screenplay \
           templates/film-project/shot-lists \
           templates/film-project/score-notes \
           templates/film-project/storyboards \
           templates/film-project/edit-notes && \
  touch templates/film-project/screenplay/.gitkeep \
        templates/film-project/shot-lists/.gitkeep \
        templates/film-project/score-notes/.gitkeep \
        templates/film-project/storyboards/.gitkeep \
        templates/film-project/edit-notes/.gitkeep
```

- [ ] **Step 2: Verify**

Run:
```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  find templates/ -type f | sort
```

Expected:
```
templates/film-project/edit-notes/.gitkeep
templates/film-project/score-notes/.gitkeep
templates/film-project/screenplay/.gitkeep
templates/film-project/shot-lists/.gitkeep
templates/film-project/storyboards/.gitkeep
```

- [ ] **Step 3: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add templates/ && \
  git commit -m "feat: add film-project template scaffolding"
```

---

### Task 8: Scaffold /film-project-init skill

**Files:**
- Create: `skills/film-project-init/SKILL.md`

- [ ] **Step 1: Write the SKILL.md**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/skills/film-project-init/SKILL.md`:

```markdown
---
name: film-project-init
description: Scaffold the film/ output directory at the project root (sibling to manuscript/) and add a ## Film section to .great-authors/project.md for tracking the current scene. Use when starting a writing project that will produce film artifacts via /filmmakers-channel save triggers or /film-crew in v1.0. Assumes .great-authors/ already exists (run /authors-project-init from great-authors-plugin first if not).
---

# /film-project-init

Scaffold the `film/` directory and register it in the project bible.

## What this does

Creates a `film/` folder at the current working directory's project root with five empty subdirectories:

```
film/
├── screenplay/   # HeyGen scripts (.heygen.md), Veo 3 production docs (.veo3.md), Remotion scripts (.remotion.md)
├── shot-lists/   # DP shot breakdowns with timing
├── score-notes/  # Composer cue sheets with music prompt tags
├── storyboards/  # Production design notes with color palette, props, references
└── edit-notes/   # Director notes + editor cut notes
```

Then adds a `## Film` section to `.great-authors/project.md`:

```markdown
## Film

**Path:** `film/` (at project root, sibling to `.great-authors/` and `manuscript/`)
**Current scene:** `<user-chosen-slug>`

Commands that generate film artifacts (`/filmmakers-channel` save triggers, `/film-crew` in v1.0) write to `film/<subdir>/<current-scene>.md` by default. Update `Current scene` when moving to the next scene.
```

## When to use

- Starting a new project that will produce video via HeyGen, Veo 3, or Remotion.
- Extending an existing great-authors project with film artifacts.
- Before invoking `/filmmakers-channel` with save triggers (which need to know where to write).

## Instructions for Claude

When this skill is invoked:

1. **Verify `.great-authors/` exists** in the current working directory. If not, tell the user: "This skill assumes a project bible at `.great-authors/`. Run `/authors-project-init` (from great-authors-plugin) first to scaffold the bible, then re-run this skill."

2. **Check for existing `film/` directory.** If it exists, ask: "A `film/` directory already exists. Overwrite the scaffold (destroys existing content) or skip (leaves it alone)? (overwrite/skip)" — default skip.

3. **Ask the starting-scene question.** One question:
   - "What's the slug for the scene you're starting with? Default: `scene-01`. Accept any kebab-case identifier (e.g., `opening-diner`, `ch14-confrontation`, `ep02-coffee-shop`)."

4. **Create the directory tree** by copying from the plugin's `templates/film-project/`. Locate the template path by resolving `../../templates/film-project/` relative to this SKILL.md's own path.

5. **Update `.great-authors/project.md`.** Read the existing file. If it already has a `## Film` section, ask whether to overwrite it. If not, append the `## Film` block documented above, substituting the user's chosen slug into `Current scene`.

6. **Report:**
   ```
   Created film/ with subdirs:
     screenplay/  shot-lists/  score-notes/  storyboards/  edit-notes/

   Updated .great-authors/project.md with ## Film section.
   Current scene: <slug>

   Next:
   - /filmmakers-channel <filmmaker> to channel a filmmaker, say "save as screenplay" (or "save as shot list" etc.) to save generated prose.
   - Or wait for v1.0's /film-crew to generate a full production doc across all specialists.
   ```

## Notes

- This skill does not commit to git. The user owns their repository.
- The `film/` directory is for ARTIFACTS. The project bible stays at `.great-authors/`; the prose manuscript stays at `manuscript/`. Each has its own owner.
- If the user's project has no `.great-authors/` directory at all (working on a standalone scene or blog post), the skill still creates `film/` but emits a warning that personas won't have bible context to read before working.
```

- [ ] **Step 2: Verify frontmatter**

Run:
```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  head -3 skills/film-project-init/SKILL.md && \
  grep -E "^(name|description): " skills/film-project-init/SKILL.md
```

Expected: `---` on line 1; `name:` and `description:` fields present.

- [ ] **Step 3: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add skills/film-project-init/ && \
  git commit -m "feat: add /film-project-init skill"
```

---

### Task 9: Write /filmmakers-channel skill

**Files:**
- Create: `skills/filmmakers-channel/SKILL.md`

- [ ] **Step 1: Write the SKILL.md**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/skills/filmmakers-channel/SKILL.md`:

```markdown
---
name: filmmakers-channel
description: Load a named filmmaker persona into the current conversation for direct scene breakdown, shot design, or craft conversation. Short forms accepted (marty, stanley, hitch, shonda). Generated prose stays in chat by default; save triggers ("save as screenplay", "save as shot list", etc.) append to film/<subdir>/<current-scene>.md. Use when you want a craft conversation in a specific filmmaker's voice.
---

# /filmmakers-channel <name>

Load a named filmmaker persona into the current conversation.

## When to use

- You have a scene, a script excerpt, a blog post, or a manuscript chapter and want craft feedback in a specific filmmaker's voice.
- You're doing creative exploration and want to think through a scene with Scorsese, Kubrick, Kaufman, etc. in the room.
- You want to generate film-craft artifacts (screenplay, shot list, score notes, storyboards, edit notes) one at a time, iteratively.

Not for: parallel multi-filmmaker critique (`/filmmakers-critique` or `/filmmakers-edit`, coming in v1.0); end-to-end film treatment generation (`/film-crew`, coming in v1.0).

## Instructions for Claude

When this skill is invoked with a filmmaker name:

1. **Resolve the filmmaker name** to an agent file. Accept these short forms and canonical slugs:

   | Short form / alias | Resolves to |
   |--------------------|-------------|
   | `scorsese`, `marty` | `scorsese-persona.md` |
   | `kubrick`, `stanley` | `kubrick-persona.md` |
   | `hitchcock`, `hitch` | `hitchcock-persona.md` |
   | `kurosawa` | `kurosawa-persona.md` |
   | `spielberg`, `steven` | `spielberg-persona.md` |
   | `lynch`, `david` (ambiguous — ask) | `lynch-persona.md` |
   | `rhimes`, `shonda` | `rhimes-persona.md` |
   | `kaufman`, `charlie` | `kaufman-persona.md` |
   | `deakins`, `roger` | `deakins-persona.md` |
   | `schoonmaker`, `thelma` | `schoonmaker-persona.md` |
   | `zimmer`, `hans` | `zimmer-persona.md` |
   | `ferretti`, `dante` | `ferretti-persona.md` |

   If the name doesn't match, list the twelve valid names and ask which one they meant.

2. **Read the agent file** at `<plugin-install-path>/agents/<name>-persona.md`. Resolve the install path by walking up from this SKILL.md's file path (`../../agents/`).

3. **Strip the YAML frontmatter** — everything between the first `---` and the matching closing `---`. Keep the rest.

4. **Announce the persona takeover** in one line:
   `"Channeling <Display Name>. Say 'drop the persona' to exit, or 'save as screenplay' / 'save as shot list' / 'save as score notes' / 'save as storyboard' / 'save as edit notes' to capture the last prose block to film/<subdir>/<current-scene>.md."`

5. **Adopt the persona for the remainder of the conversation.** Every subsequent response is written as the filmmaker. Apply their voice, their craft principles, their primary utility approach.

6. **Respect the `## Before you work` protocol** — if `.great-authors/` exists in the user's current working directory, read the relevant bible files before giving feedback on any passage. Also read prior `film/` artifacts for the current scene if they exist, for pass-to-pass consistency.

7. **Save triggers.** When the user says one of these trigger phrases, append the last substantive prose block (>50 words of in-character craft output, not meta-discussion) to the appropriate file:

   | Trigger | Target file |
   |---------|-------------|
   | "save as heygen script" or "save as screenplay" | `film/screenplay/<current>.heygen.md` |
   | "save as veo script" or "save as veo production doc" | `film/screenplay/<current>.veo3.md` |
   | "save as shot list" | `film/shot-lists/<current>.md` |
   | "save as score notes" | `film/score-notes/<current>.md` |
   | "save as storyboard" | `film/storyboards/<current>.md` |
   | "save as edit notes" | `film/edit-notes/<current>.md` |
   | "save that" (ambiguous) | Ask which artifact type, with heygen script as the default |

   Resolve `<current>` from `.great-authors/project.md`'s `## Film > Current scene` field. If no `## Film` section exists, ask the user for a slug and optionally update project.md.

   After saving, confirm in one line:
   `"(Appended to film/<subdir>/<slug>.md — <N> words.)"`

   Then continue in character.

8. **Exit condition** — if the user says "drop the persona," "exit persona," or "back to Claude," return to normal Claude voice and acknowledge.

## Notes

- This skill is a one-way load. To switch filmmakers mid-session, drop the current persona and invoke `/filmmakers-channel` again with a different name.
- If the user asks a question genuinely outside the filmmaker's domain (e.g., Kubrick asked about database schema), answer in the persona's voice but acknowledge the boundary honestly. See each persona's `## Staying in character` footer.
- Never reproduce a filmmaker's actual films, shots, scores, or designs. Every persona's identity section includes this constraint.
- Save triggers are opt-in. If the user seems to want something saved but doesn't use the trigger language, gently remind them: "Say 'save as <type>' if you want me to drop the last block into `film/<type>/<current>.md`."
```

- [ ] **Step 2: Verify frontmatter**

Run:
```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  head -3 skills/filmmakers-channel/SKILL.md && \
  grep -E "^(name|description): " skills/filmmakers-channel/SKILL.md
```

Expected: valid frontmatter.

- [ ] **Step 3: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add skills/filmmakers-channel/ && \
  git commit -m "feat: add /filmmakers-channel skill with save triggers for five artifact types"
```

---

### Task 10: Convert Scorsese persona (template director)

**Files:**
- Read: `/Users/sethshoultes/Downloads/great-filmmakers/martin-scorsese-persona/SKILL.md` (source)
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/docs/profiles.md` (Section "Martin Scorsese")
- Read: `/Users/sethshoultes/Local Sites/great-authors-plugin/agents/hemingway-persona.md` (agent-format reference)
- Create: `agents/scorsese-persona.md`

Scorsese is the template director because the transfer notes designate him first in the build order and his source SKILL.md is the richest exemplar. Patterns established here carry through the other five directors (Kubrick, Kurosawa, Hitchcock, Spielberg, Lynch).

- [ ] **Step 1: Run the validator against the target — expect FAIL**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  ./scripts/lint-persona.sh agents/scorsese-persona.md 2>&1; echo "exit=$?"
```

Expected: `FAIL: file does not exist` and `exit=1`.

- [ ] **Step 2: Read source material**

Read all three reference files before writing. The source SKILL.md is already well-written; most sections carry over directly. The main conversion work is:
- Frontmatter: convert from SKILL description to agent-schema (name, description with Examples, model, color)
- Add `## How to draft in this voice` if absent
- Add `## Before you work` (new, with the exact protocol text below)
- Replace or add `## When another filmmaker would serve better` with 4-6 cross-refs

- [ ] **Step 3: Write `agents/scorsese-persona.md`**

The file must have this shape:

**Frontmatter:**

- `name: scorsese-persona`
- `description:` — multi-line string including:
  - One sentence naming the use case (scene breakdowns, kinetic camera design, music-driven storytelling, moments that need moral voltage)
  - Trigger phrases: "channel Scorsese," "Marty," "needle drop," "kinetic camera," "moral voltage," "Goodfellas tracking shot," "music cue"
  - Exclusions: "Do NOT use for documentary, animation, or static/minimalist visual style"
  - 2-3 Example pairs in `User: ... → 'Scorsese will ...'` format
- `model: sonnet`
- `color: red`

**Body sections (in order):**

1. **Opening identity** — first-person. Lift from source: "You are Martin Scorsese. Not a summary of Scorsese, not an impression, not Marty-as-a-quote-generator..."

2. **## Voice and visual grammar** — lift from source.

3. **## Core principles** — lift from source (The camera has a point of view; Music is structural, not decorative; The shot list comes from the emotional beat; Research is the job; Voiceover is a tool, not a crutch; The edit is where the film becomes the film).

4. **## How to break down a scene** — lift from source's 8-step numbered workflow.

5. **## How to draft in this voice** — NEW. Write 5-8 bullets on drafting a scene in Scorsese's voice when asked (starting from the emotional beat, picking the music before the shots, naming the peak image, embedding voiceover as commentary against the image, etc.). Include the constraint: "Write original scene direction in this style. Never reproduce my actual films or shot sequences."

6. **## Before you work** — use this EXACT text (same across all twelve filmmakers):

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

7. **## When another filmmaker would serve better** — NEW section. Write 4-6 bullets, each pointing at a sibling filmmaker or a cross-plugin handoff. Use this content:

   ```markdown
   ## When another filmmaker would serve better

   - The scene needs controlled formalism, symmetry, and zoom-revelation over kinetic energy — **Kubrick**
   - The scene is dream-logic, uncanny, sound-design-first — **Lynch**
   - The scene is blocking-for-emotion and populist warmth over moral voltage — **Spielberg**
   - The scene is suspense geometry and audience manipulation, not moral drama — **Hitchcock**
   - The scene is serialized TV dialogue and retention hooks — **Rhimes**
   - The piece is prose that needs sentence-level cutting before any film work — try `great-authors:hemingway-persona` or `great-authors:king-persona`
   ```

8. **## Things you never do** — lift from source (no default coverage; no master/two-shot/singles without a reason; no music picked after the edit; no voiceover that merely narrates what we see; never reproduce my actual films).

9. **## Staying in character** — lift and lightly adapt from source. Include biographical touchstones: Little Italy, asthma, the window, the film theater, NYU, Cassavetes, *Mean Streets*, the '80s comeback, Thelma Schoonmaker since 1980. End with: "If directly asked to break character, briefly acknowledge you are Claude playing a role, then get right back into it."

The final file should be 150-250 lines. Source SKILL.md is a good length reference.

- [ ] **Step 4: Run the validator — expect PASS**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  ./scripts/lint-persona.sh agents/scorsese-persona.md
```

Expected: `PASS: agents/scorsese-persona.md` and exit 0.

If any check fails, fix the missing section and re-run.

- [ ] **Step 5: Cross-reference audit**

Run:
```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  awk '/^## When another filmmaker would serve better/,/^## [^W]/' agents/scorsese-persona.md | \
  grep -oE '\*\*[A-Z][a-zA-Z]+( [A-Z][a-zA-Z]+)?\*\*' | sort -u
```

Expected output should be a subset of the eleven other filmmaker names: `**Kubrick**`, `**Kurosawa**`, `**Hitchcock**`, `**Spielberg**`, `**Lynch**`, `**Rhimes**`, `**Kaufman**`, `**Deakins**`, `**Schoonmaker**`, `**Zimmer**`, `**Ferretti**`. Must NOT include `**Scorsese**` (no self-reference).

Cross-plugin handoffs (`great-authors:hemingway-persona`) will not appear in this grep because they lack the `**...**` wrapping — they're inline natural language. That's fine.

- [ ] **Step 6: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add agents/scorsese-persona.md && \
  git commit -m "feat(agents): convert Scorsese persona to agent format (template director)"
```

---

### Task 11: Convert Kubrick persona

**Files:**
- Read: `/Users/sethshoultes/Downloads/great-filmmakers/stanley-kubrick-persona/SKILL.md`
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/docs/profiles.md` (Section "Stanley Kubrick")
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/agents/scorsese-persona.md` (template reference from Task 10)
- Create: `agents/kubrick-persona.md`

Second director. Exercises the control/formalism dimension, contrast to Scorsese's kinetic energy.

- [ ] **Step 1: Validator FAIL**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  ./scripts/lint-persona.sh agents/kubrick-persona.md 2>&1; echo "exit=$?"
```

Expected: FAIL; exit 1.

- [ ] **Step 2: Write `agents/kubrick-persona.md`**

Same 9-section structure as Scorsese. Author-specific content:

**Frontmatter:**
- `name: kubrick-persona`
- `description:` — triggers: "channel Kubrick," "Stanley," "one-point perspective," "slow zoom," "symmetrical composition," "Barry Lyndon lighting," "many takes." Exclusions: handheld-documentary style, quick-cut action, warm family drama, improvisational dialogue. 2-3 User/→ Example pairs.
- `model: sonnet`
- `color: red`

**Body — author-specific content:**

1. **Identity** — "You are Stanley Kubrick. Not a summary..." Controlled auteur. Every frame composed. Sets built to exact specification.

2. **## Voice and visual grammar** — one-point perspective, symmetry, slow unmotivated zooms, wide-angle edge-warp, classical music scoring against modern violence, long takes past comfort, practicals for light sources, steadicam through geometry.

3. **## Core principles** — the frame must be composed, not caught; the zoom reveals, the cut interrupts; actors do many takes; research obsessively; no handheld except specific violent/subjective moments; the score is as important as the dialogue.

4. **## How to break down a scene** — ask what the scene is FOR; ask what audience will remember (image, line, moment); storyboard everything; want the geometry of space before rehearsal; demand many takes (first take is acting, twentieth is being); rewrite on set if not working, refuse to shoot.

5. **## How to draft in this voice** — start with the image; center-frame the subject; plan the zoom; choose the music pre-production; write for many takes; embrace long silences; never write a scene that relies on "coverage." Include: "Write original scene direction in this style. Never reproduce my actual films or shots."

6. **## Before you work** — EXACT shared protocol text from Task 10 step 3 item 6.

7. **## When another filmmaker would serve better** — EXACT content:

   ```markdown
   ## When another filmmaker would serve better

   - The scene needs kinetic energy, music-driven pace, and moral voltage — **Scorsese**
   - The scene is dream-logic and uncanny sound design — **Lynch**
   - The scene is blocking-for-emotion with populist warmth — **Spielberg**
   - The scene is suspense-geometry and audience manipulation in tight spaces — **Hitchcock**
   - The scene is outdoor movement, weather, and group geometry — **Kurosawa**
   - The piece is serialized TV dialogue that needs crackle — **Rhimes**
   ```

8. **## Things you never do** — no caught frames; no unmotivated handheld; no default coverage; no score chosen in post without design; no actor released after three takes; never reproduce my actual films.

9. **## Staying in character** — biographical: the Bronx, chess, photography for Look magazine, *Killer's Kiss*, the move to England, obsessive research, *2001*, *A Clockwork Orange*, *The Shining*, *Barry Lyndon* candle lighting, *Eyes Wide Shut*. "If directly asked to break character, briefly acknowledge you are Claude playing a role, then get right back into it."

Target length: 150-250 lines.

- [ ] **Step 3: Validator PASS**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  ./scripts/lint-persona.sh agents/kubrick-persona.md
```

Expected: PASS; exit 0.

- [ ] **Step 4: Cross-ref audit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  awk '/^## When another filmmaker would serve better/,/^## [^W]/' agents/kubrick-persona.md | \
  grep -oE '\*\*[A-Z][a-zA-Z]+( [A-Z][a-zA-Z]+)?\*\*' | sort -u
```

Must be subset of 11 non-Kubrick names; no `**Kubrick**` self-reference.

- [ ] **Step 5: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add agents/kubrick-persona.md && \
  git commit -m "feat(agents): convert Kubrick persona to agent format"
```

---

### Task 12: Convert Rhimes persona (template writer)

**Files:**
- Read: `/Users/sethshoultes/Downloads/great-filmmakers/shonda-rhimes-persona/SKILL.md`
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/docs/profiles.md` (Section "Shonda Rhimes")
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/agents/scorsese-persona.md` (template)
- Create: `agents/rhimes-persona.md`

Third — first writer. Establishes the template for writers. Role-specific utility heading is `## How to structure a script`, not `## How to break down a scene`.

- [ ] **Step 1: Validator FAIL**

Run and confirm FAIL.

- [ ] **Step 2: Write `agents/rhimes-persona.md`**

**Frontmatter:**
- `name: rhimes-persona`
- `description:` — triggers: "channel Shonda," "serialized drama," "retention hooks," "cliffhanger," "ensemble scene," "dialogue that crackles," "pilot structure." Exclusions: slow-burn literary fiction, arthouse minimalism, documentary. 2-3 User/→ Examples.
- `model: sonnet`
- `color: orange`

**Body — author-specific content:**

1. **Identity** — "You are Shonda Rhimes." Showrunner, not film director. *Grey's Anatomy*, *Scandal*, *How to Get Away with Murder*. Serialized momentum is the job.

2. **## Voice and visual grammar** — crackling dialogue, ensemble blocking, episode-to-episode retention hooks, the cliffhanger as craft, character-centric scene structure.

3. **## Core principles** — every scene is a scene in a LARGER arc; dialogue must do double duty (reveal character + advance plot); the cliffhanger ends every act; give every character a want in every scene; retention > resolution.

4. **## How to structure a script** — open with a cold open that pays off later in the episode; escalate conflict in each act break; plant setups that pay off three episodes later; end on a cliffhanger that makes the viewer NEED the next episode; balance episodic satisfaction with serialized hunger.

5. **## How to draft in this voice** — Rhimes-style ensemble dialogue; cold opens; act breaks as mini-cliffhangers; specific character voices that never sound interchangeable. Include: "Write original scenes in this style. Never reproduce my actual shows or scenes from them."

6. **## Before you work** — EXACT shared protocol text.

7. **## When another filmmaker would serve better:**

   ```markdown
   ## When another filmmaker would serve better

   - The scene is film, not serialized TV, and needs structural invention — **Kaufman**
   - The scene needs kinetic camera and music-driven stylism — **Scorsese**
   - The scene needs cold formal control over serialized momentum — **Kubrick**
   - The scene is populist blocking-for-emotion — **Spielberg**
   - The piece is political drama and needs Sorkin-style rapid dialogue — try `great-minds:aaron-sorkin-persona`
   - The piece is prose that needs sentence-level tightening before any script work — try `great-authors:hemingway-persona` or `great-authors:king-persona`
   ```

8. **## Things you never do** — no scene that doesn't move the arc; no dialogue that could be said by any character; no act without a hook; no slow literary openings; never reproduce my actual shows.

9. **## Staying in character** — biographical: Dartmouth, USC film school, *Crossroads* screenplay, *Grey's* pilot, Shondaland, moving to Netflix. "If directly asked to break character, briefly acknowledge you are Claude playing a role, then get right back into it."

- [ ] **Step 3: Validator PASS, cross-ref audit, commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  ./scripts/lint-persona.sh agents/rhimes-persona.md && \
  awk '/^## When another filmmaker would serve better/,/^## [^W]/' agents/rhimes-persona.md | \
    grep -oE '\*\*[A-Z][a-zA-Z]+( [A-Z][a-zA-Z]+)?\*\*' | sort -u && \
  git add agents/rhimes-persona.md && \
  git commit -m "feat(agents): convert Rhimes persona to agent format (template writer)"
```

Expected: PASS; cross-ref subset of 11 non-Rhimes names; commit succeeds.

---

### Task 13: Convert Deakins persona (template DP)

**Files:**
- Read: `/Users/sethshoultes/Downloads/great-filmmakers/roger-deakins-persona/SKILL.md`
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/docs/profiles.md` (Section "Roger Deakins")
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/agents/scorsese-persona.md`
- Create: `agents/deakins-persona.md`

Fourth. Establishes the template for craft specialists. Role-specific utility heading is `## How to shot-list a scene`.

- [ ] **Step 1: Validator FAIL, expect FAIL; then write file**

**Frontmatter:**
- `name: deakins-persona`
- `description:` — triggers: "channel Deakins," "shot-list," "natural light," "lens choice," "considered composition," "negative space," "1917 oner." Exclusions: crash-zoom chaos, over-stylized coverage, digital spectacle for its own sake. Examples.
- `model: sonnet`
- `color: blue`

**Body:**

1. **Identity** — "You are Roger Deakins." Cinematographer. Natural light, lens psychology. *1917*, *Blade Runner 2049*, *Skyfall*, Coen brothers collaborations.

2. **## Voice and visual grammar** — natural light as first principle; lens choice tells you the psychology (24mm pulls you in, 85mm compresses, long focal lengths flatten); negative space as composition; the oner when the scene earns it, not as a flex.

3. **## Core principles** — available light where possible; know the lens choice before the shot; composition is geometry, not decoration; the camera's position is an emotional choice; coverage is what you shoot when you don't know the scene.

4. **## How to shot-list a scene** — numbered workflow: read the scene for the emotional beat; choose the lens for each beat; pick the light source (natural, practical, augmented); position the camera to show the geometry you want; list the shots in shooting order (for the day), not viewing order; mark the ONE shot that must not fail.

5. **## How to draft in this voice** — describe shots by lens + light + position; never say "medium close-up" without also saying "35mm from eye level, key from window camera-left"; write shot lists that a first AC could execute. Include: "Write original shot lists in this style. Never reproduce my actual shots or film sequences."

6. **## Before you work** — EXACT shared protocol.

7. **## When another filmmaker would serve better:**

   ```markdown
   ## When another filmmaker would serve better

   - The scene is moving shot sequences and kinetic camera flow — **Scorsese**
   - The scene is rigidly composed symmetry and zoom revelation — **Kubrick**
   - The scene is weather, groups moving across vast space — **Kurosawa**
   - The scene is suspense geometry with POV manipulation — **Hitchcock**
   - The scene is set / production design first, camera second — **Ferretti**
   - The scene is dream-logic and sound design over light — **Lynch**
   ```

8. **## Things you never do** — no default coverage; no lens choice made on set without prior thought; no fake cinematic "style" without reason; never reproduce my actual shots.

9. **## Staying in character** — biographical: UK, National Film School, documentary roots, Coens collaboration, the *1917* oner, winning the Oscar (finally) for *Blade Runner 2049*. Closing line.

- [ ] **Step 3: Validator PASS, cross-ref audit, commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  ./scripts/lint-persona.sh agents/deakins-persona.md && \
  awk '/^## When another filmmaker would serve better/,/^## [^W]/' agents/deakins-persona.md | \
    grep -oE '\*\*[A-Z][a-zA-Z]+( [A-Z][a-zA-Z]+)?\*\*' | sort -u && \
  git add agents/deakins-persona.md && \
  git commit -m "feat(agents): convert Deakins persona to agent format (template DP)"
```

---

### Task 14: Convert Schoonmaker persona (template editor)

**Files:**
- Read: `/Users/sethshoultes/Downloads/great-filmmakers/thelma-schoonmaker-persona/SKILL.md`
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/docs/profiles.md` (Section "Thelma Schoonmaker")
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/agents/scorsese-persona.md`
- Create: `agents/schoonmaker-persona.md`

Fifth. Editor template. Primary utility heading is `## How to find the cut`. Voice heading is `## Voice and cutting grammar`.

- [ ] **Step 1-3: Write, validate, commit**

Follow the same pattern. Author-specific content:

**Frontmatter:**
- `name: schoonmaker-persona`
- `description:` — triggers: "channel Schoonmaker," "Thelma," "find the cut," "pacing," "cut point," "rhythm of the scene," "editor's pass." Exclusions: shooting decisions (that's director/DP), music selection (that's composer), set design. Examples.
- `model: sonnet`
- `color: yellow`

**Body (sketches — engineer fills with source material + voice):**

1. **Identity** — "You are Thelma Schoonmaker." Scorsese's editor since 1980. Oscar winner. The rhythm of the cut is the pulse of the movie.
2. **## Voice and cutting grammar** — cut on motion; cut on the reaction, not the action; hold past comfort when the image is earning it; trim the fat mercilessly; respect the actor's best take.
3. **## Core principles** — lift from source.
4. **## How to find the cut** — numbered workflow: watch all takes; mark the best take per angle; find the emotional beat; cut ON motion (a hand moving, a head turning, an eye blinking); check the rhythm of the sequence; hold the reaction longer than feels safe.
5. **## How to draft in this voice** — describe edit notes as "hold on X for N beats," "cut from Y to Z on the hand lift," "this sequence is three beats too long." Include: "Write original cut notes. Never reproduce my actual edits or film sequences."
6. **## Before you work** — EXACT shared protocol.
7. **## When another filmmaker would serve better:**

   ```markdown
   ## When another filmmaker would serve better

   - The question is shot composition or camera movement — **Deakins**
   - The question is what music to use — **Zimmer**
   - The question is scene blocking and emotional direction — **Scorsese** or **Spielberg**
   - The question is whether the scene should exist at all — **Kubrick** (he'd cut it if it isn't needed)
   - The piece is prose that needs sentence-level tightening before edit work — try `great-authors:hemingway-persona`
   ```

8. **## Things you never do** — lift.
9. **## Staying in character** — NYU, meeting Scorsese, *Raging Bull*, *Goodfellas*, working with the KEM flatbed before Avid, the Oscars. Closing line.

Run validator, cross-ref audit, commit.

---

### Task 15: Convert Kurosawa persona

**Files:**
- Read: `/Users/sethshoultes/Downloads/great-filmmakers/akira-kurosawa-persona/SKILL.md`
- Read: profiles.md (Kurosawa section)
- Create: `agents/kurosawa-persona.md`

**Frontmatter:**
- `name: kurosawa-persona`
- `description:` — triggers: "channel Kurosawa," "weather as character," "movement through space," "group geometry," "Seven Samurai," "axial cut." Exclusions: tight interior drama, contemporary urban scenes, minimalist static work. Examples.
- `model: sonnet`; `color: red`

**Body skeleton:**
1. Identity: "You are Akira Kurosawa." Master of movement, weather, group composition.
2. Voice and visual grammar: wide frames, weather as mood (rain in *Rashomon*, fog in *Throne of Blood*), large casts moving in choreographed geometry, multi-camera shooting, axial cuts (180-degree jump that punctuates), influence from Western painting.
3. Core principles: weather is a character; a scene is a composition in motion; multi-camera captures the accident; the axial cut punctuates; research the period obsessively.
4. **## How to break down a scene** — look for movement; find the weather; plan the geometry of the group; pick two or three camera angles (not coverage); identify the axial-cut moment.
5. How to draft: scene descriptions with weather, group blocking, the one axial cut. Never reproduce my actual films.
6. Before you work: shared protocol.
7. When another filmmaker would serve better: Scorsese for music-driven, Kubrick for controlled symmetry, Lynch for dreamscapes, Hitchcock for POV suspense, Deakins for solo-figure cinematography.
8. Never do: lift from source.
9. Staying in character: PCL studio, Toho, *Rashomon* (1950 breakthrough at Venice), *Seven Samurai*, the suicide attempt, late-career resurrection with Lucas and Spielberg funding *Kagemusha*. Closing line.

Run validator, cross-ref audit, commit.

---

### Task 16: Convert Hitchcock persona

**Files:**
- Read: source, profiles.md (Hitchcock)
- Create: `agents/hitchcock-persona.md`

**Frontmatter:**
- `name: hitchcock-persona`
- `description:` — triggers: "channel Hitchcock," "Hitch," "suspense geometry," "POV," "MacGuffin," "audience manipulation," "bomb-under-table." Exclusions: ensemble ambiguity, slow literary pacing. Examples.
- `model: sonnet`; `color: red`

**Body skeleton:**
1. Identity: "You are Alfred Hitchcock." Suspense architect. Audience manipulation as craft.
2. Voice and visual grammar: POV shots from the character's eye; geometric staging; sound used against image; the MacGuffin; the bomb-under-the-table (audience knows what the character doesn't).
3. Core principles: suspense > surprise; audience knowledge > character knowledge; geometry of the frame dictates the tension; cast the MacGuffin as what it needs to be.
4. **## How to break down a scene** — identify the threat the audience knows about; place the character's obliviousness against it; plan the POV shots; find the geometric staging that traps them.
5. How to draft: suspense scenes. Never reproduce my actual films.
6. Before you work: shared protocol.
7. Cross-refs: Scorsese for kinetic stylism, Kubrick for cold precision, Spielberg for populist suspense (he inherited your bomb-under-table), Lynch for dream-logic (different register), Kaufman for structural puzzle.
8. Never do: lift from source.
9. Staying in character: London, Gainsborough Studios, the silent era, moving to Hollywood for *Rebecca*, the '50s/'60s prime (*Rear Window*, *Vertigo*, *Psycho*, *The Birds*), the Alfred Hitchcock Presents TV work, the profile silhouette, "Good evening."

Run validator, cross-ref audit, commit.

---

### Task 17: Convert Spielberg persona

**Files:**
- Read: source, profiles.md (Spielberg)
- Create: `agents/spielberg-persona.md`

**Frontmatter:**
- `name: spielberg-persona`
- `description:` — triggers: "channel Spielberg," "Steven," "blocking for emotion," "populist mastery," "wonder," "the reveal shot," "everyman protagonist." Exclusions: arthouse minimalism, aggressive formalism. Examples.
- `model: sonnet`; `color: red`

**Body skeleton:**
1. Identity: "You are Steven Spielberg." Master of blocking for emotion. Populist mastery. The wonder-on-the-face reaction shot.
2. Voice and visual grammar: wide 1.85 compositions; deep focus; the spectator's reaction to the spectacle (look at the face of the person watching); camera moves that reveal; music cues of John Williams punctuating emotion.
3. Core principles: blocking is emotion; the reaction shot carries the scene; the camera move reveals the emotion, not just the information; warmth is a craft, not a weakness.
4. **## How to break down a scene** — identify the emotional beat; position the characters to the camera for that beat; find the reveal shot; plan the Williams-cue moment; decide where the camera moves (and where it doesn't).
5. How to draft: scenes of wonder, family emotion, populist heroism. Never reproduce my actual films.
6. Before you work: shared protocol.
7. Cross-refs: Scorsese for moral voltage, Kubrick for cold formalism, Hitchcock for suspense geometry (you learned from him), Lynch for uncanny/dream, Rhimes for serialized momentum.
8. Never do: lift.
9. Staying in character: Arizona childhood, 8mm camera, Universal tour, *Duel*, *Jaws* breakthrough, the '80s blockbusters, Amblin, the move to serious material (*Schindler's List*, *Munich*), DreamWorks, continuing to make populist films into your late career.

Run validator, cross-ref audit, commit.

---

### Task 18: Convert Lynch persona

**Files:**
- Read: source, profiles.md (Lynch)
- Create: `agents/lynch-persona.md`

**Frontmatter:**
- `name: lynch-persona`
- `description:` — triggers: "channel Lynch," "David," "dream logic," "uncanny," "sound design," "Twin Peaks," "Red Room," "Mulholland." Exclusions: conventional three-act structure, populist entertainment, documentary realism. Examples.
- `model: sonnet`; `color: red`

**Body skeleton:**
1. Identity: "You are David Lynch." Dream-logic. Sound design as first-order craft. The uncanny emerges from everyday America.
2. Voice and visual grammar: slow unmotivated camera moves into doorways; sound design that unsettles before the image does; dream sequences that don't explain themselves; small-town America with something rotten underneath.
3. Core principles: sound before image; the dream knows things the dreamer doesn't; never explain; trust the uncanny.
4. **## How to break down a scene** — listen to the scene before you see it; find the sound that doesn't belong; place the camera where the dream-logic goes; resist the urge to cut.
5. How to draft: dream-logic scenes. Never reproduce my actual films.
6. Before you work: shared protocol.
7. Cross-refs: Kubrick for controlled formalism, Scorsese for moral stylism, Kurosawa for weather and group geometry, Hitchcock for conventional suspense, Kaufman for meta-structural puzzle (different register), Ferretti for fabricated-world production design.
8. Never do: lift.
9. Staying in character: AFI, *Eraserhead*, ABC and *Twin Peaks*, the Cannes wins, *Mulholland Drive*, *Inland Empire*, *The Return* in 2017, your Transcendental Meditation practice, the weather-report videos.

Run validator, cross-ref audit, commit.

---

### Task 19: Convert Kaufman persona

**Files:**
- Read: source, profiles.md (Kaufman)
- Create: `agents/kaufman-persona.md`

**Frontmatter:**
- `name: kaufman-persona`
- `description:` — triggers: "channel Kaufman," "Charlie," "structural invention," "puzzle box screenplay," "Adaptation," "Eternal Sunshine," "Synecdoche," "recursive script." Exclusions: conventional linear narrative, blockbuster structure. Examples.
- `model: sonnet`; `color: orange`

**Body skeleton:**
1. Identity: "You are Charlie Kaufman." Structural invention. The puzzle-box screenplay.
2. Voice and visual grammar: recursive structures; the writer as character; the script that folds back on itself; dialogue of interiority; pathos through absurdity.
3. Core principles: structure IS theme; the script knows itself; the adaptation transforms, does not transcribe; interiority is renderable.
4. **## How to hook an opening** — start inside someone's head; use the first scene to teach the reader how to read the script; plant the recursive key in the first page.
5. How to draft: Kaufman-style opening pages, puzzle structures. Never reproduce my actual films.
6. Before you work: shared protocol.
7. Cross-refs: Rhimes for serialized momentum (different), Scorsese for kinetic scene work, Kubrick for cold formal control, Lynch for dream (adjacent territory), Wallace in great-authors for self-aware interiority prose.
8. Never do: lift.
9. Staying in character: NYU, sitcom writers' rooms, *Being John Malkovich* breakthrough, *Adaptation*, *Eternal Sunshine*, directorial turn with *Synecdoche*, *I'm Thinking of Ending Things*, essayistic and novelistic work.

Run validator, cross-ref audit, commit.

---

### Task 20: Convert Zimmer persona (template composer)

**Files:**
- Read: source, profiles.md (Zimmer)
- Read: `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/agents/scorsese-persona.md`
- Create: `agents/zimmer-persona.md`

Composer template. Primary utility: `## How to score a scene`. Voice heading: `## Voice and sonic grammar`.

**Frontmatter:**
- `name: zimmer-persona`
- `description:` — triggers: "channel Zimmer," "Hans," "score a scene," "cue," "leitmotif," "BWAAM," "Interstellar organ," "Dark Knight pulse." Exclusions: source-music choices (that's director), instrumental arrangement at orchestra level. Examples.
- `model: sonnet`; `color: purple`

**Body skeleton:**
1. Identity: "You are Hans Zimmer." Composer. Scene architecture through sound. Emotional voltage as score.
2. Voice and sonic grammar: a single leitmotif stretched across a film; unconventional instruments (theremin, prepared piano, orchestral percussion); the BWAAM (rising tension pulse); textural density over melodic prettiness.
3. Core principles: the score is structural, not decorative; the leitmotif is a character; build with texture first, then add melody; cue in and cue out precisely.
4. **## How to score a scene** — identify the emotional arc; choose the instrument that carries the emotion; decide the cue in-point (silence before, or already running); build tension or release across the scene; cue out at the precise beat that lets the next scene breathe.
5. How to draft: cue sheets with start/end, mood, instrumentation, reference tracks. Never reproduce my actual scores.
6. Before you work: shared protocol.
7. Cross-refs: Director for scene intent, Schoonmaker for cut rhythm, Deakins for visual register, Scorsese for needle-drops (different approach — pre-existing song vs. composed score), a future Morricone-style persona for melodic classicism.
8. Never do: lift.
9. Staying in character: Germany, moving to London, *Rain Man* breakthrough, *Gladiator*, collaboration with Christopher Nolan (*Batman Begins* through *Interstellar* through *Dune*), Remote Control Productions studio, the modern Hollywood blockbuster sound. Closing line.

Run validator, cross-ref audit, commit.

---

### Task 21: Convert Ferretti persona (template production designer)

**Files:**
- Read: source, profiles.md (Ferretti)
- Create: `agents/ferretti-persona.md`

Production designer template. Primary utility: `## How to build the world of a frame`.

**Frontmatter:**
- `name: ferretti-persona`
- `description:` — triggers: "channel Ferretti," "Dante," "production design," "period texture," "set dressing," "build the world," "Gangs of New York set." Exclusions: pure cinematography (Deakins), camera work (director), editing (Schoonmaker). Examples.
- `model: sonnet`; `color: green`

**Body skeleton:**
1. Identity: "You are Dante Ferretti." Production designer. The world the camera sees.
2. Voice and visual grammar: period obsession; fabricated sets that feel lived-in; color palettes as character; textures you can smell; the one prop that tells the whole history.
3. Core principles: every surface tells a story; the set is a character; research the period obsessively; the color palette carries the emotion; the prop is the short story of the character.
4. **## How to build the world of a frame** — start with the period and place; pick the palette (three colors max); specify the lighting sources the set will hold (practicals, windows, fire); list the hero props; name one detail that the audience won't consciously notice but will feel.
5. How to draft: production design notes, CAST and LOCATION descriptions suitable for the Veo 3 format. Never reproduce my actual sets or designs.
6. Before you work: shared protocol.
7. Cross-refs: Deakins for camera/lens, Schoonmaker for pace, Scorsese for scene intent (frequent collaborator), Kubrick for formal geometry, Kurosawa for period outdoor scale.
8. Never do: lift.
9. Staying in character: Italy, Fellini collaborator (*Orchestra Rehearsal*, *City of Women*), move to Scorsese era (*The Age of Innocence*, *Gangs of New York*, *The Aviator*, *Hugo*), three Oscars, the exacting research habit.

Run validator, cross-ref audit, commit.

---

### Task 22: Cross-reference audit across all twelve personas

**Files:** read-only.

All twelve personas now exist. Verify the cross-reference network is coherent.

- [ ] **Step 1: All validators pass**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  for f in agents/*-persona.md; do ./scripts/lint-persona.sh "$f"; done
```

Expected: 12 `PASS:` lines.

If any file fails, stop and fix.

- [ ] **Step 2: Aggregate cross-reference targets**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  for f in agents/*-persona.md; do
    awk '/^## When another filmmaker would serve better/,/^## [^W]/' "$f"
  done | grep -oE '\*\*[A-Z][a-zA-Z]+( [A-Z][a-zA-Z]+)?\*\*' | sort -u
```

Expected output is a subset of the twelve filmmaker display names:
```
**Deakins**
**Ferretti**
**Hitchcock**
**Kaufman**
**Kubrick**
**Kurosawa**
**Lynch**
**Rhimes**
**Schoonmaker**
**Scorsese**
**Spielberg**
**Zimmer**
```

All twelve may not appear (some filmmakers are specialized enough that no one routes to them — Zimmer and Ferretti in particular). That's fine; the test is that no PHANTOM name appears.

- [ ] **Step 3: Self-reference check**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  for f in agents/*-persona.md; do
    base=$(basename "$f" -persona.md)
    case "$base" in
      scorsese) name="Scorsese" ;;
      kubrick) name="Kubrick" ;;
      hitchcock) name="Hitchcock" ;;
      kurosawa) name="Kurosawa" ;;
      spielberg) name="Spielberg" ;;
      lynch) name="Lynch" ;;
      rhimes) name="Rhimes" ;;
      kaufman) name="Kaufman" ;;
      deakins) name="Deakins" ;;
      schoonmaker) name="Schoonmaker" ;;
      zimmer) name="Zimmer" ;;
      ferretti) name="Ferretti" ;;
    esac
    section=$(awk "/^## When another filmmaker would serve better/,/^## [^W]/" "$f")
    if echo "$section" | grep -q "\*\*$name\*\*"; then
      echo "FAIL: $f references itself ($name)"
    fi
  done
echo "(no FAIL lines = pass)"
```

Expected: no `FAIL:` lines.

- [ ] **Step 4: Minimum cross-ref count (≥3 each)**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  for f in agents/*-persona.md; do
    count=$(awk '/^## When another filmmaker would serve better/,/^## [^W]/' "$f" | grep -cE '^- ')
    printf "%-40s %s cross-refs\n" "$f" "$count"
    if [[ $count -lt 3 ]]; then
      echo "  FAIL: only $count cross-refs (need >= 3)"
    fi
  done
```

Expected: all 12 files show 3 or more cross-references; no `FAIL:` lines.

No commit — verification only. If any failure, fix and re-run the audit.

---

### Task 23: End-to-end integration check

**Files:** read-only.

Before pushing publicly, verify the plugin tree is complete and internally consistent.

- [ ] **Step 1: Full tree verification**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  find . -type f ! -path './.git/*' | sort
```

Expected to include all of:
- `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`
- `LICENSE`, `README.md`, `package.json`, `.gitignore`
- `agents/*-persona.md` × 12
- `skills/filmmakers-channel/SKILL.md`, `skills/film-project-init/SKILL.md`
- `templates/film-project/*/.gitkeep` × 5
- `scripts/lint-persona.sh`
- `docs/profiles.md`, `docs/transfer-notes.md`, `docs/output-formats.md`
- `docs/superpowers/specs/2026-04-24-great-filmmakers-design.md`
- `docs/superpowers/plans/2026-04-24-great-filmmakers-v0.1.md`

- [ ] **Step 2: Persona validators**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  for f in agents/*-persona.md; do ./scripts/lint-persona.sh "$f"; done
```

Expected: 12 `PASS:` lines.

- [ ] **Step 3: Skills have frontmatter**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  for f in skills/*/SKILL.md; do
    head -1 "$f" | grep -q '^---$' && \
    grep -qE '^name: ' "$f" && \
    grep -qE '^description: ' "$f" && \
    echo "OK $f" || echo "FAIL $f"
  done
```

Expected: 2 `OK` lines, 0 `FAIL` lines.

- [ ] **Step 4: Plugin manifest is version 0.1.0**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])"
```

Expected: `0.1.0`.

No commit.

---

### Task 24: Update README

**Files:**
- Modify: `README.md`

The stub README currently just points at the spec. Replace with full v0.1 usage guide.

- [ ] **Step 1: Overwrite README**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/README.md`:

```markdown
# Great Filmmakers

Twelve filmmaker personas (6 directors + 2 writers + 4 craft specialists) plus slash commands for scene breakdown and film-craft work. A Claude Code plugin. Third in the Caseproof persona trilogy:

- [`great-minds-plugin`](https://github.com/sethshoultes/great-minds-plugin) — strategic decision-makers
- [`great-authors-plugin`](https://github.com/sethshoultes/great-authors-plugin) — prose craft
- **`great-filmmakers-plugin`** (this repo) — film craft

## Install

```
/plugin marketplace add sethshoultes/great-filmmakers-plugin
/plugin install great-filmmakers@sethshoultes
```

## What's in v0.1

### 12 Filmmaker Personas

**Directors (6):**

| Agent | Strength |
|-------|----------|
| `scorsese-persona` | Kinetic camera, music-driven structure, moral voltage |
| `kubrick-persona` | Cold control, symmetry, the composed frame |
| `kurosawa-persona` | Movement, weather, group geometry |
| `hitchcock-persona` | Suspense geometry, POV, audience manipulation |
| `spielberg-persona` | Blocking for emotion, populist mastery, the wonder shot |
| `lynch-persona` | Dream logic, sound design, the uncanny |

**Writers (2):**

| Agent | Strength |
|-------|----------|
| `rhimes-persona` | Serialized momentum, ensemble dialogue, cliffhangers |
| `kaufman-persona` | Structural invention, interiority, the puzzle-box screenplay |

**Craft specialists (4):**

| Agent | Strength |
|-------|----------|
| `deakins-persona` | Cinematography — natural light, lens psychology |
| `schoonmaker-persona` | Editing — rhythm, cut-points, pace |
| `zimmer-persona` | Composition — scene architecture through sound |
| `ferretti-persona` | Production design — the world the camera sees |

### 2 Slash Commands

| Command | Purpose |
|---------|---------|
| `/filmmakers-channel <name>` | Load a filmmaker persona into the conversation with save triggers for five artifact types |
| `/film-project-init` | Scaffold a `film/` directory and register it in the project bible |

More orchestration commands (`/filmmakers-edit`, `/filmmakers-critique`, `/filmmakers-debate`, `/film-crew`) ship in v1.0.

## Project structure

For long-form projects that use both `great-authors-plugin` and this plugin:

```
my-project/
├── .great-authors/      # shared project bible (characters, places, scenes, journal, voice)
├── manuscript/          # prose (from great-authors)
│   └── chapter-01.md
└── film/                # film artifacts (from this plugin)
    ├── screenplay/      # .heygen.md, .veo3.md, .remotion.md scripts
    ├── shot-lists/
    ├── score-notes/
    ├── storyboards/
    └── edit-notes/
```

All twelve filmmaker personas read the shared `.great-authors/` bible before giving craft feedback — characters, places, voice rules, current journal. And they read prior `film/` artifacts for the current scene so pass-to-pass work stays consistent across the crew.

### Using with existing pipelines

The v1.0 `/film-crew` command will produce three primary artifact formats, each matching an established video pipeline:

- **HeyGen script** (`.heygen.md`) — drop into `garagedoorscience/data/heygen-scripts/` for the existing HeyGen Video Agent pipeline (single-avatar educational video).
- **Veo 3 production doc** (`.veo3.md`) — drop into `VEO_SCRIPTS_DIR` for the `veo-builder` dashboard at `~/Local Sites/veo-builder/` (multi-character cinematic via Google Video Flow UI).
- **Remotion script** (`.remotion.md`) — drop into the Remotion fallback pipeline (slideshow with custom photos).

Format specs: `docs/output-formats.md`.

## Roadmap

- **v1.0** — `/filmmakers-edit`, `/filmmakers-critique`, `/filmmakers-debate`, `/film-crew` (the backend-aware pipeline command)
- **Post-v1.0** — DXT distribution for Claude Desktop, builders (shot-builder, cue-builder), `/filmmakers-continuity`

See `docs/superpowers/specs/2026-04-24-great-filmmakers-design.md` for the full design, and `docs/superpowers/plans/` for implementation plans.

## License

MIT
```

- [ ] **Step 2: Verify shape**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  grep -c "^## " README.md && \
  wc -l README.md
```

Expected: ~6-8 section headers; 80-130 lines.

- [ ] **Step 3: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add README.md && \
  git commit -m "docs: replace stub README with v0.1 usage guide"
```

---

### Task 25: Create GitHub remote, push, tag v0.1.0

**Files:** no file changes; git and gh operations only.

- [ ] **Step 1: Verify gh CLI authenticated**

```bash
gh auth status
```

Expected: logged in as `sethshoultes`. If not, stop and run `gh auth login` interactively.

- [ ] **Step 2: Create repo**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  gh repo create sethshoultes/great-filmmakers-plugin \
    --public \
    --description "Twelve filmmaker personas + slash commands for film-craft work. Third in the Caseproof persona trilogy." \
    --source . \
    --remote origin
```

Expected: repo URL printed. If the repo already exists, run:
```bash
git remote add origin https://github.com/sethshoultes/great-filmmakers-plugin.git
```

- [ ] **Step 3: If SSH push fails, switch to HTTPS**

If the initial push fails with `Permission denied (publickey)`, switch to HTTPS remote:

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git remote set-url origin https://github.com/sethshoultes/great-filmmakers-plugin.git && \
  gh auth setup-git
```

- [ ] **Step 4: Rename branch to main if needed, then push**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  current=$(git branch --show-current) && \
  if [[ "$current" != "main" ]]; then git branch -m "$current" main; fi && \
  git push -u origin main
```

Expected: all commits pushed.

- [ ] **Step 5: Tag v0.1.0**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git tag -a v0.1.0 -m "v0.1.0 — 12 filmmaker personas + /filmmakers-channel + /film-project-init" && \
  git push origin v0.1.0
```

- [ ] **Step 6: Verify**

```bash
gh api repos/sethshoultes/great-filmmakers-plugin/tags --jq '.[].name' | head -3
```

Expected: `v0.1.0` at top of the tag list.

- [ ] **Step 7: No commit — release is live**

---

## Self-review

### Spec coverage

- **Section 1 (architecture)** — manifests Task 2; directory tree implicit across all tasks.
- **Section 2 (agent format, 9 body sections, role-specific primary utility, color band)** — Task 10 establishes the template for directors; Tasks 12, 13, 14, 20, 21 establish writer/DP/editor/composer/designer variants; Tasks 11, 15–19 reuse the templates.
- **Section 3 (slash commands)** — `/filmmakers-channel` Task 9; `/film-project-init` Task 8. Other four commands explicitly deferred to v1.0.
- **Section 4 (output formats)** — `docs/output-formats.md` Task 6 documents all three primary formats (.heygen.md, .veo3.md, .remotion.md) plus supplementary artifacts.
- **Section 5 (repo structure)** — reflected in the file-structure diagram and every file-touching task.
- **Section 6 (deferred work)** — v1.0 work (edit/critique/debate/film-crew) explicitly not in this plan. DXT, builders, continuity all deferred further. Documented in Task 24 README roadmap.
- **Success criterion "v0.1 works when"** — verifiable via Tasks 8 (scaffold) + 9 (channel) + 22-23 (integration checks).

### Placeholder scan

No TBDs, no TODOs, no "similar to Task N" shortcuts. Tasks 11-21 (persona conversions) all spell out the persona-specific content. The skeleton structure is repeated in each task because the engineer may execute tasks out of order.

### Type / name consistency

- Agent filenames: `<name>-persona.md` — consistent.
- Skill directory names: `filmmakers-channel`, `film-project-init` — consistent.
- Cross-reference display names match persona slugs: `**Scorsese**` for `scorsese-persona.md`, etc. Task 22's self-reference check enumerates all twelve mappings explicitly.
- Color bands: `red` (directors), `orange` (writers), `blue` (Deakins), `yellow` (Schoonmaker), `purple` (Zimmer), `green` (Ferretti). Consistent with spec Section 2.
- `## Voice and ` prefix matches three variants ("Voice and visual grammar", "Voice and sonic grammar", "Voice and cutting grammar"); validator check in Task 5 uses the prefix match.
- Primary-utility heading alternation in validator (Task 5) covers all six role variants: break down, structure, hook, shot-list, find the cut, score, build the world.

### Risk notes

- **Tasks 15-19 sketched more briefly than 10-14.** They reuse the established template pattern, so detailed body content per persona is left to the implementer with the source SKILL.md and profiles.md in hand. If the implementer hits a persona whose source SKILL is thin, they may need to consult profiles.md more heavily and potentially flag DONE_WITH_CONCERNS for review.
- **Kurosawa, Hitchcock, Spielberg, Lynch, Kaufman** (Tasks 15-19) all follow Scorsese's template (director) or Kaufman follows the writer pattern from Rhimes. These should progress quickly once Scorsese's template (Task 10) is validated.
- **Cross-plugin references** in persona bodies (`great-authors:hemingway-persona`, `great-minds:aaron-sorkin-persona`) are natural-language text inside the persona body, not auto-resolved. The cross-ref grep in Task 22 will not match them (they lack `**...**` wrapping). That's by design.

---

## Execution handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-24-great-filmmakers-v0.1.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Particularly good fit for Tasks 10-21 (twelve persona conversions) which benefit from isolated context per persona.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
