# Changelog

All notable changes to `great-filmmakers` are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/) with [SemVer](https://semver.org/) versioning. The README's "What's new in vX.Y" sections are the authoritative narrative; this file is the per-release index for tooling and quick reference.

## [1.10.0] — 2026-04-26

The DXT-bundle release. Brings `great-filmmakers` to parity with the rest of the constellation by adding a Claude Desktop extension bundle.

### Added

- **`distribution/dxt/`** — full DXT bundle for Claude Desktop. `manifest.json`, `package.json`, `server/index.js` with handlers for all 7 skills (`filmmakers_channel`, `filmmakers_crew`, `filmmakers_project_init`, `filmmakers_build_keyframes`, `filmmakers_critique`, `filmmakers_debate`, `filmmakers_edit`), `server/personas/` with copies of all 12 persona files. Build with `cd distribution/dxt && npm install && npx @anthropic-ai/dxt pack`.
- **`marketplace.json`** updated to register the DXT bundle as a sibling install entry.
- **CHANGELOG.md** — this file. Until v1.10, version history lived in README sections only.

### Fixed

- Smoke test lexicographic semver compare (`[ "$X" \> "1.6" ]`) replaced with numeric major.minor compare (would have silently broken at v1.10).
- `datetime.utcnow()` deprecation in `templates/scripts/render_kling.py` and `render_veo.py` — replaced with `datetime.now(timezone.utc)` to track the upcoming Python 3.12+ removal.

### Companion changes

- Smoke test now validates persona-count alignment with the new DXT bundle (matches publishers/marketers smoke test pattern).

## [1.9.0] — 2026-04-26

Skill renames for plugin-internal consistency. Two skills used `film-*`; five used `filmmakers-*`. With no existing users, renamed the outliers:

- `/film-crew` → `/filmmakers-crew`
- `/film-project-init` → `/filmmakers-project-init`

All seven skills now use the `filmmakers-*` prefix. Cross-plugin references updated in great-authors, great-publishers, great-minds, brain.

## [1.8.1] — 2026-04-26

Quality-pass fixes from cross-plugin review.

### Documentation

- Removed phantom `render_book_illustrations.py` references (4 places). The script doesn't exist; book illustrations use `render_keyframes.py`.
- `film-project-init` SKILL.md success report now lists 4 templates (was 3 — `wire_book_illustrations.py` was missing).

### Template hardening

- `render_kling.py` — pacing-sleep no longer fires for already-complete shots on re-runs.
- `render_kling.py` — fails loudly when shots config is empty (was silent no-op).
- `render_veo.py` — fails loudly when `parse_doc` returns 0 shots; surfaces em-dash vs hyphen hint.
- `render_veo.py` — `relative_to(project_root)` wrapped in try/except; no longer crashes when `--out-dir` is outside project.
- `wire_book_illustrations.py` — validates `--book-root` exists and chapters directory present before creating destination dirs.
- `render_keyframes.py` — `--only` accepts comma-separated slugs (was single-slug; now consistent with `render_kling.py` / `render_veo.py`).

## [1.8.0] — 2026-04-26

Papercut fixes from real production use, plus a unified slug naming convention and a content-policy pre-flight scanner.

### Added

- Unified slug convention `<prefix>-<scene-slug>` — single regex matches all PROMPTS.md files. Common prefixes documented: `chNN-`, `kf-`, `cover-`, `social-`.
- `templates/scripts/wire_book_illustrations.py` — new template. Reads PROMPTS.md, copies rendered PNGs into Astro `public/illustrations/`, inserts `<Illustration>` tags into chapter MDX. Three-pass anchor matcher (substring-60 → substring-30 → fuzzy via `difflib.SequenceMatcher`, default threshold 0.7). Stdlib only.
- `templates/scripts/render_kling.py` and `render_veo.py` — browser User-Agent default on all download requests (preventative; Leonardo's CDN returns 403 to default Python urllib UA).
- `templates/scripts/render_veo.py` — `--check-content-policy` flag (off / warn / strict). Reads `.great-authors/project.md` for genre, scans shot prompts for refusal-prone keywords if mystery/crime/thriller/noir/horror.

### Companion changes in great-authors v1.6

Phase 7 closing of `/authors-orchestrate-novel` now surfaces publication, visual, and marketing handoffs to publishers / filmmakers / marketers.

## [1.7.0] — 2026-04-26

Codifies the keyframe-prompt brief and documents the image-gen backend choices.

### Added

- **`/filmmakers-build-keyframes <source-file>`** — new skill. Dispatches a director persona to read source + bible, identify cue points, produce structured PROMPTS.md (style anchor + composition + subject + light + production design + negative prompt). Default director Hitchcock; `--director` overrides accept Deakins, Kurosawa, Scorsese, Kubrick, Lynch, Spielberg.
- **`docs/output-formats.md` image-gen backends section** — Path E (gpt-image-1), F (gpt-image-2), G (Imagen 4 Ultra), H (Leonardo Phoenix). Model IDs, sizes, prompt-length limits, pricing, content-policy notes, known quirks.
- **`tests/smoke.sh`** — new for great-filmmakers (publishers / marketers had it; this plugin didn't). Validates frontmatter, version coherence, style preset slug consistency, v1.7+ feature presence.

### Companion changes in great-authors v1.5

`templates/project-bible/visual-lints.md` (new template) and `## Visual` section in `project.md`. `/filmmakers-build-keyframes` reads both.

## [1.6.0] — 2026-04-26

Render-script templates copied into `<project>/scripts/` on init.

### Added

- **`templates/scripts/render_keyframes.py`** — gpt-image-1 → PNG keyframes from a director PROMPTS.md.
- **`templates/scripts/render_kling.py`** — Kling 2.5 image-to-video → MP4 (with chain conditioning via ffmpeg last-frame extraction).
- **`templates/scripts/render_veo.py`** — Veo 3.0 Fast text-to-video → MP4 (durations quantized to {4, 6, 8}).

All three: stdlib-first, env-key auth from canonical secrets, idempotent state file, `--only` and `--dry-run` flags. `/film-project-init` now copies them into `<project>/scripts/` without overwriting.

## [1.5.0] — 2026-04-26

Direct HeyGen submission with verbatim scripts + avatar registry.

### Added

- **`scripts/heygen-submit.py`** — submits a `.heygen.md` doc to HeyGen `POST /v3/videos` (the verbatim-script endpoint). The `/v3/video-agents` endpoint always rewrites prompts and is the wrong tool for tight Kaufman scripts.
- **Avatar registry** — frontmatter `avatar_name:` resolves to `$HEYGEN_<NAME>_TALKING_PHOTO_ID` and `$HEYGEN_<NAME>_VOICE_ID` from `~/.config/dev-secrets/secrets.env`.
- **Kaufman persona** tuned for HeyGen drafts: read-aloud test, numbers must land, paths and commands stay on screen rather than in the mouth.

## [1.4.0] — 2026-04-26

Four render paths and an image-gen tier system, derived from a head-to-head shootout between Veo 3.1 Fast preview, Kling 2.5 Turbo, and Leonardo Motion 2.0 plus a three-way image-gen comparison (Imagen 4 Fast, Leonardo Phoenix, gpt-image-2 high).

### Added

- Path A (Veo 3.0 Fast text-to-video, default), Path B (Veo 3.1 Fast preview with reference images), Path C (Kling 2.5 Turbo image-to-video), Path D (Leonardo Motion 2.0 image-to-video). Each path documented with model IDs, durations, aspect ratios, content-policy notes.
- Image-gen tier system — Imagen 4 Fast / Leonardo Phoenix / gpt-image-2 with empirical comparison data.

## [1.3.0] — 2026-04-25

Reference images do work on Veo 3.1 — correcting v1.1's wrong claim. Path B (Veo 3.1 Fast preview + reference images) added as a real option.

## [1.1.0] — 2026-04-24

Veo 3 production-grade fixes from the first real-world short. Path A (Veo 3.0 Fast + inline character anchoring) documented with the empirical constraints (durations quantized to {4, 6, 8}, no `personGeneration` on tier 1, no `referenceImages` to veo-3.0-fast).

## [1.0.0] — 2026-04-24

Initial release. Twelve filmmaker personas (6 directors + 2 writers + 4 craft specialists) plus the slash commands for scene breakdown and film-craft work. Third in the Caseproof persona trilogy.
