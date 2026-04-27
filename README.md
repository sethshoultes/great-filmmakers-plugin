# Great Filmmakers

Twelve filmmaker personas (6 directors + 2 writers + 4 craft specialists) plus slash commands for scene breakdown and film-craft work. A Claude Code plugin. Third in the Caseproof persona trilogy:

- [`great-minds-plugin`](https://github.com/sethshoultes/great-minds-plugin) — strategic decision-makers
- [`great-authors-plugin`](https://github.com/sethshoultes/great-authors-plugin) — prose craft
- **`great-filmmakers-plugin`** (this repo) — film craft

> **New to the Caseproof persona constellation?** Start with [`/constellation-start`](https://github.com/sethshoultes/great-minds-plugin) in `great-minds` — it asks 2-3 questions about your project shape and routes to the right plugin.

📖 **[Read the User Manual](MANUAL.md)** for the complete reference — install, all twelve personas, all five commands, the bible structure, backend selection, Veo 3 constraints, style presets, an end-to-end walkthrough, patterns, and troubleshooting.

## Install

```
/plugin marketplace add sethshoultes/great-filmmakers-plugin
/plugin install great-filmmakers@sethshoultes
```

## What's new in v1.8

Papercut fixes from real production use, plus a unified slug naming convention and a content-policy pre-flight scanner.

### Unified slug convention

`<prefix>-<scene-slug>` across all PROMPTS.md files. One regex matches all backends:

```
### ([a-z][a-z0-9_\-]*)\.png
```

Common prefixes documented: `chNN-` (chapter illustrations), `kf-` (keyframes for image-to-video), `cover-` (cover concepts), `social-` (social-promo stills). One naming convention, one render script per backend, no per-project regex divergence. See `docs/output-formats.md` § "Slug convention (canonical, v1.8+)" for the full guidance.

### `templates/scripts/wire_book_illustrations.py` — new template

Lifts the wiring script from a real project into the plugin's templates. Reads PROMPTS.md (with `--include-prose-anchors`), copies rendered PNGs into the book site's `public/illustrations/`, inserts `<Illustration>` components into chapter MDX at the matched prose-anchor paragraph.

**Fuzzy anchor matching (the v1.8 fix):** when the director's prose anchor was paraphrased slightly from the manuscript source (common during Hitchcock-style cue identification), the previous substring matcher missed the placement. The template now does three passes: substring-60, substring-30, then `difflib.SequenceMatcher.ratio()` with a configurable threshold (default 0.7). Stdlib only — no RapidFuzz dependency.

### Browser User-Agent default in render scripts

Leonardo's CDN returns 403 to default Python urllib User-Agents. `render_kling.py` and `render_veo.py` templates now set a browser User-Agent (`Mozilla/5.0 ... Chrome/120.0.0.0 Safari/537.36`) on every download request preventatively, regardless of backend. Saves the next debugging round when a future CDN does the same thing.

### `--check-content-policy` flag for `render_veo.py`

Veo refuses many body/violence-adjacent prompts in crime fiction. The new flag (default `warn`; modes `off`, `warn`, `strict`) reads `.great-authors/project.md` for the genre, scans each shot's prompt for refusal-prone keywords, and surfaces flagged shots before submission.

```
→ content-policy pre-flight scan
   project genre is 'literary mystery' — scanning shots for refusal-prone prompts.
   ⚠️  3 shot(s) contain refusal-prone keywords:
     [E1a] keywords: body, blood
           preview: A wide shot of the wash. The body lies on its side...
   Recommendations:
   - Sanitize the prompts (drop the keyword; describe consequence rather than action)
   - Use Kling for these shots (more permissive on stylized content)
   - Run with --check-content-policy=off to bypass
   Continue with submission anyway? [y/N]:
```

`--check-content-policy=strict` aborts before submission instead of prompting. The check is a heuristic — Veo's policy is opaque and changes — but it surfaces risk before quota is burned.

### Companion change in great-authors v1.6

Phase 7 closing of `/authors-orchestrate-novel` now surfaces the publication handoff to `great-publishers`, the visual handoff to `great-filmmakers`, and the marketing handoff to `great-marketers`. The orchestrate-novel pipeline is no longer the end of the road — it's the bridge to the rest of the constellation.

## What's new in v1.7

Codifies the keyframe-prompt brief that's been hand-written for too many projects, and documents the image-gen backend choices that any project producing illustrations will face.

### `/filmmakers-build-keyframes <source-file>` — new skill

Dispatches a director persona to read a prose source + the project bible, identify illustration cue points, and produce a structured `PROMPTS.md` artifact (TOC + per-prompt blocks with style anchor, composition, subject, light, production design, negative prompt). The shared upstream of book-illustration work, video-keyframe work, and cover-art briefs.

Default director Hitchcock for genre fiction; `--director` overrides accept Deakins (natural-light register), Kurosawa (landscape-driven), Scorsese, Kubrick, Lynch, Spielberg. Optional flags: `--count <N>`, `--include-prose-anchors` (for downstream wiring scripts), `--out-dir <path>`, `--style-preset <slug>`.

```bash
/filmmakers-build-keyframes manuscript/chapter-01.md \
    --director hitchcock --count 5 --include-prose-anchors
# produces film/render/book-illustrations/PROMPTS.md
```

### `docs/output-formats.md` — image-gen backend section

Four image-gen paths now documented alongside the four video paths:

| Path | Backend | Use case |
|---|---|---|
| **E** | gpt-image-1 (OpenAI) | Default. Best brief adherence. ~$0.19/image at high quality. |
| **F** | gpt-image-2 (OpenAI) | State-of-the-art. *Requires org verification.* Edits endpoint. |
| **G** | Imagen 4 Ultra (Gemini) | When rendered title text is the load-bearing requirement. |
| **H** | Leonardo Phoenix | Avoid for editorial-register; CDN requires browser User-Agent. |

For each: model IDs, sizes, prompt-length limits (Phoenix is 1500-char, others 3000+), pricing, content-policy notes, known quirks. Render scripts (`templates/scripts/render_keyframes.py`) target these uniformly.

### Smoke tests

`tests/smoke.sh` is new for great-filmmakers (publishers and marketers had it; this plugin didn't). Validates SKILL.md and persona frontmatter, version coherence between `package.json` and `plugin.json`, style preset slug consistency in `docs/style-presets.md`, and the v1.7+ presence of `filmmakers-build-keyframes`.

### Companion changes in great-authors v1.5

`templates/project-bible/visual-lints.md` (new template) and the `## Visual` section in `project.md` carry the visual register and forbidden-element rules. `/filmmakers-build-keyframes` reads both. Together they eliminate per-prompt restatement of the project's visual constraints.

## What's new in v1.6

Three render-script templates that turn director-authored prompts into PNGs and MP4s. The plugin now ships the bridge between the creative artifacts (PROMPTS.md, .veo3.md, .kling.md) and the rendered files on disk.

### `templates/scripts/` — copied into `<project>/scripts/` on init

| Script | Backend | Auth | Input | Output |
|---|---|---|---|---|
| `render_keyframes.py` | OpenAI Images (gpt-image-1) | `OPENAI_API_KEY` | director's `PROMPTS.md` | PNGs alongside the prompts file |
| `render_kling.py` | Kling 2.5 image-to-video | `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` | `<slug>.kling.md` + `<slug>.kling.shots.json` | MP4s in `film/render/kling/` |
| `render_veo.py` | Gemini Veo 3.0 Fast | `GEMINI_API_KEY` | `<slug>.veo3.md` | MP4s in `film/render/veo/` |

All three share the same shape: stdlib-only (or `requests` for Kling), env-key auth from canonical secrets, idempotent state file, `--only` and `--dry-run` flags, sensible API-drift warnings in the docstring. `render_kling.py` adds chain-conditioning (extracts the final frame of a prior MP4 as input to the next shot for held-take continuity). `render_veo.py` quantizes shot durations to {4, 6, 8} at parse time.

### `/film-project-init` now copies them in

When you run `/film-project-init`, the skill scaffolds `film/` AND copies `templates/scripts/*.py` into `<project>/scripts/`. Existing scripts are not overwritten. The render scripts are project-owned once copied — edit them freely.

### Why scripts live at the project level

Render scripts depend on per-project API keys, idempotency state, and filesystem layout. They're not plugin-internal tools (which live in `scripts/` at the plugin root, like `heygen-submit.py`). Templates that projects copy in is the right boundary. See `learnings/plugin-ships-prompts-project-ships-renders.md` in the brain vault for the architectural reasoning.

## What's new in v1.5

Direct HeyGen submission, an avatar registry, and Kaufman tuned for the spoken word.

### `scripts/heygen-submit.py` — render from a `.heygen.md` doc in one command

```bash
set -a && source ~/.config/dev-secrets/secrets.env && set +a
python3 scripts/heygen-submit.py film/screenplay/<slug>.heygen.md
# MP4 lands at film/screenplay/<slug>.mp4
```

Calls HeyGen's **`POST /v3/videos`** endpoint with the `script` field — the avatar speaks Kaufman's words verbatim, no rewriting. (The `/v3/video-agents` endpoint always rewrites the prompt into its own script and is the wrong tool for tight, intentional scripts.)

### Avatar registry — one frontmatter field, IDs resolved from canonical secrets

```yaml
avatar_name: Seth   # → $HEYGEN_SETH_TALKING_PHOTO_ID + $HEYGEN_SETH_VOICE_ID
```

No more pasting talking-photo IDs into docs. Add a new avatar by setting `HEYGEN_<NAME>_TALKING_PHOTO_ID` and `HEYGEN_<NAME>_VOICE_ID` in `~/.config/dev-secrets/secrets.env`. Pattern documented in `docs/output-formats.md` § Avatar registry.

### Kaufman tuned for HeyGen scripts

The Kaufman persona now carries explicit guidance for spoken-word drafts: read-aloud test, no clauses that need rereading, numbers must land, no filler, paths and commands stay on screen rather than in the mouth, gift goes at the end.

### Pre-flight: HeyGen API tier credit

The HeyGen API tier credit is **separate from web-app credits**. If submission rejects with `MOVIO_PAYMENT_INSUFFICIENT_CREDIT`, fund the API tier at https://app.heygen.com/settings?nav=API. The script surfaces this clearly when it happens.

## What's new in v1.4

Two new render paths and a new image-gen tier system, derived from a head-to-head shootout between Veo 3.1 Fast preview, Kling 2.5 Turbo, and Leonardo Motion 2.0 plus a three-way image-gen comparison (Imagen 4 Fast, Leonardo Phoenix, gpt-image-2 high).

### Four render paths now documented (was two)

- **Path A** (Veo 3.0 Fast text-to-video, default): mixed {4, 6, 8}-second durations, inline character anchoring, $0.10/sec at 720p. **Wins for multi-shot stylized series work.**
- **Path B** (Veo 3.1 Fast preview with reference images): every shot 8s at 16:9, up to 3 character refs, stronger continuity than inline anchoring.
- **Path C** (Kling 2.5 Turbo image-to-video, NEW): 5 or 10s clips, strong motion physics, image-to-video grounding via composite still. Use for one-off cinematic shots, NOT series work — image-to-video composition drift between shots compounds.
- **Path D** (Leonardo Motion 2.0 image-to-video, NEW): 5s clips at $0.05 each — cheapest path. Documented character drift; use only for atmospheric B-roll where character identity doesn't matter.

The trilogy short (`/blog/videos/trilogy.mp4`) was re-rendered via Kling Path C as a stress test. Result: Veo Path A still won at project scale because text-to-video keeps composition consistent across shots, while image-to-video pipelines (Kling, Leonardo Motion) inherit any composition flaws from their source stills. Documented in [video-gen-services-comparison](https://github.com/sethshoultes/brain/blob/main/learnings/video-gen-services-comparison.md).

### Image-gen tier system

Ferretti's persona file now teaches three tiers for reference and hero image generation:

- **Tier 1** (Imagen 4 Fast, $0.02, 5–10s) — default for reference images, throwaway exploration, iterative work
- **Tier 1.5** (Leonardo Phoenix, $0.05, 30–45s) — stylized editorial work; "Ghibli-like" register on pen-and-ink prompts; chains directly into Leonardo Motion 2.0 via `imageId`
- **Tier 2** (gpt-image-2 high, $0.20, 3–6 min) — hero shots where the image IS the deliverable; dense in-image text rendering; 4K final assets

**Meta-lesson:** tier-2 fidelity gets bounded when the still is re-rendered downstream by Veo or Kling. Don't pay for tier-2 on a still that's going to be a Veo reference image; pay for tier-2 only when the image will be displayed at the highest resolution as the canonical asset. Documented in [image-gen-tier-system](https://github.com/sethshoultes/brain/blob/main/learnings/image-gen-tier-system.md).

### Schoonmaker's craft note expanded

Schoonmaker now teaches the cut rhythms available in all four paths:

| Path | Available durations |
|------|---------------------|
| A | {4, 6, 8} — mixed-rhythm cutting |
| B | {8} only |
| C | {5, 10} — two-beat cutting |
| D | {5} only |

The trade-off table makes the editorial cost of each path explicit. Pick the path before the cut sheet is written, not after.

### Files changed

- `docs/output-formats.md` — Path C (Kling) and Path D (Leonardo Motion) sections + four-way decision table
- `agents/ferretti-persona.md` — image-gen tier choice section, framing rule, pipeline match rule
- `agents/schoonmaker-persona.md` — render-service durations now covers all four paths
- `MANUAL.md` Section 9 — re-titled "Video gen production constraints" (was "Veo 3 production constraints"); added Path C, Path D, and the choosing-between-paths matrix
- `README.md` — v1.4 announcement (this section)
- `.claude-plugin/plugin.json` + `package.json` — version 1.4.0

## What's new in v1.3

Reference images on Veo 3.1 actually work — v1.1's claim that they don't was wrong, and a re-test on the upgraded Gemini API tier proved the error was in the probe, not the API. v1.3 corrects the documentation, adds a second production path, and ships an honest meta-learning.

**Two production paths now documented:**

- **Path A — Veo 3.0 Fast + inline character anchoring** (default, cheapest, mixed durations).
- **Path B — Veo 3.1 Fast preview + reference images** (stronger continuity, every shot 8 seconds at 16:9).

**Reference-images request shape (corrected):** flat `bytesBase64Encoded` + `mimeType`, `referenceType: "asset"` lowercase. NOT the `inlineData` wrapper Google's docs page shows — the API rejects that. Forum-confirmed shape, see `docs/output-formats.md` § "Veo 3 production constraints" Path B for the full request body.

**Hard constraints on reference-image renders (all required, all empirically verified):**
1. Veo 3.1 only — Veo 3.0 rejects `referenceImages` outright.
2. `durationSeconds: 8` — 4- and 6-second clips silently reject when refs are present.
3. `aspectRatio: "16:9"` — other ratios reject when refs are present.
4. Up to 3 reference images per shot.
5. Cannot combine `referenceImages` with `image` (init frame) or `lastFrame`.

**Schoonmaker's craft note** now explains both paths — Path A keeps the {4, 6, 8} cut rhythm; Path B collapses every shot to 8 seconds, trading rhythm for continuity. The trade-off is now explicit, not implicit.

**Related learnings:** [`brain/learnings/veo-3-api-constraints.md`](https://github.com/sethshoultes/brain/blob/main/learnings/veo-3-api-constraints.md) carries the meta-learning ("trust the probe over the docs; vary one constraint at a time before concluding a feature is unsupported"). The v1.1 release notes that called reference images unusable were wrong; the cause was a wrong duration in the probe combined with a wrong field shape from a stale docs read.

## What's new in v1.1

Production-grade fixes from the first real-world Veo 3 short ([Three Shapes of the Same Pattern](https://sethshoultes.com/blog/three-shapes.html)):

- **Default Veo model corrected** — `veo-3.0-fast-generate-001` instead of `veo-3.1-fast-generate-preview`. The 3.1 previews reject all human subjects on the standard Gemini API tier; 3.0 Fast is the working option at $0.10/sec.
- **Shot durations quantized to {4, 6, 8}** — Veo 3.0 Fast rejects 5- and 7-second shots despite docs claiming "between 4 and 8 inclusive." Schoonmaker's persona file now teaches this constraint as part of the cutting craft. `/film-crew --backend veo3` honors it.
- **`personGeneration` and `referenceImages` removed from API output** — both are rejected on the Gemini API tier. The `ingredient_images` block remains in the doc footer for the Veo Flow UI workflow but is now correctly documented as Flow-only.
- **Style presets** — pen-and-ink editorial is the new default style anchor (verified to bypass the photorealistic-human content gate). See `docs/style-presets.md` for the library and how to add more.
- **CLAUDE.md project template** — `/film-project-init` now drops a CLAUDE.md that establishes Claude as the orchestrator (dispatching personas via the Agent tool) rather than channeling them inline.
- **Schoonmaker craft note** — added a "leave silence for the visual punch" principle for shorts with VO; verified empirically by leaving the last ~10s of the trilogy short narration-free over the recognition push-in.

Full constraint reference: `docs/output-formats.md` § "Veo 3 production constraints."

## What's in v1.0

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

### 6 Slash Commands

| Command | Purpose |
|---------|---------|
| `/filmmakers-channel <name>` | Load a filmmaker persona into the conversation with save triggers for five artifact types |
| `/film-project-init` | Scaffold a `film/` directory and register it in the project bible |
| `/filmmakers-edit <file> [names...]` | Multi-filmmaker editorial pass with consolidated breakdowns |
| `/filmmakers-critique <file> [names...]` | Fast 3-bullet verdicts from 3 filmmakers in parallel (Haiku-dispatched) |
| `/filmmakers-debate <topic> <a> <b>` | 2-round craft dispute between two filmmakers |
| `/film-crew <file> [--backend ...]` | Backend-aware pipeline — produces HeyGen, Veo 3, or Remotion-ready artifacts |

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

- **Post-v1.0** — DXT distribution for Claude Desktop, builders (shot-builder, cue-builder, storyboard-builder), `/filmmakers-continuity`, additional filmmakers (Tarkovsky, Wong Kar-wai, Varda, Miyazaki, Morricone as Zimmer alternative)

All v1.0 goals shipped. Future work is driven by user feedback — open an issue at https://github.com/sethshoultes/great-filmmakers-plugin/issues.

See `docs/superpowers/specs/2026-04-24-great-filmmakers-design.md` for the full design, and `docs/superpowers/plans/` for implementation plans.

## License

MIT
