---
name: filmmakers-build-keyframes
description: Dispatch a director persona to read source prose + the project bible, identify illustration cue points, and produce a structured PROMPTS.md artifact (TOC + per-prompt blocks with style anchor, composition, subject, light, production design, negative prompt). The shared upstream of book-illustration work, video-keyframe work, and cover-art briefs. Default director Hitchcock for genre fiction; override with --director (deakins for natural-light register, kurosawa for landscape-driven, etc.). Usage - /filmmakers-build-keyframes <source-file> [--director <name>] [--count <N>] [--include-prose-anchors] [--out-dir <path>] [--style-preset <slug>].
---

# /filmmakers-build-keyframes <source-file> [options]

Generate a structured `PROMPTS.md` for image-generation backends from a prose source.

## When to use

- A chapter or scene needs illustrations for a book site, MDX inline placement, or print.
- An image-to-video render (Kling, Runway) needs conditioning keyframes.
- A book cover or marketing visual needs a brief grounded in the actual work.
- Any time the same brief that's been hand-written before is about to be hand-written again.

This skill is intentionally upstream of every render pass. The output is a creative artifact (PROMPTS.md); the actual rendering happens via the project-level `scripts/render_keyframes.py` (which handles both video keyframes and book illustrations from the same PROMPTS.md format) — copied in from `templates/scripts/`.

## What this does

1. Reads the source file (a chapter, scene, or section of prose).
2. Reads the project bible (`.great-authors/`) — `project.md`, `voice.md`, the new `visual-lints.md` if present (per the v1.7+ convention), and any character/place files relevant to the source.
3. Dispatches a director persona via the Agent tool. The director identifies illustration cue points in the source — moments where an image carries something the prose alone doesn't.
4. The director writes structured prompt blocks for each cue point in the canonical PROMPTS.md format.
5. Saves to `<out-dir>/PROMPTS.md` (default `film/render/book-illustrations/PROMPTS.md`).

## Arguments

- `<source-file>` (required) — path to the source prose. Typically a chapter under `manuscript/`, a scene file, or any markdown/MDX file with substantive prose.
- `--director <name>` (optional) — director persona to dispatch. Default `hitchcock` for genre fiction. Valid: `hitchcock`, `scorsese`, `kubrick`, `kurosawa`, `spielberg`, `lynch`, `deakins` (DP-as-director when natural-light register matters most).
- `--count <N>` (optional) — target number of cue points. Default is the director's judgment based on source length (typically 4-6 per chapter).
- `--include-prose-anchors` (optional flag) — for each cue point, include the prose snippet (~50-150 chars) immediately preceding it. Downstream wiring tools like `wire_book_illustrations.py` use these anchors to place the illustration at the correct point in MDX.
- `--out-dir <path>` (optional) — output directory. Default `film/render/book-illustrations/`. Common alternatives: `film/render/kling/keyframes/` (image-to-video), `publishers/covers/` (cover briefs, when great-publishers is in use).
- `--style-preset <slug>` (optional) — slug from `docs/style-presets.md` (e.g., `pen-and-ink-editorial`, `photoreal-cinematic`). The director uses the preset's style anchor as the verbatim opening of every prompt block. If `.great-authors/project.md` has a `## Visual` section with a `Style preset` field (per v1.5+ of great-authors), that takes precedence unless `--style-preset` overrides explicitly.

## Instructions for Claude

When this skill is invoked:

1. **Verify the source file exists** at the given path (or interpret as relative to the current working directory).

2. **Verify project structure:**
   - `.great-authors/` should exist; if not, warn the user but proceed (the director's brief will be thinner without bible context).
   - The `--out-dir` path will be created if it doesn't exist.

3. **Resolve the style preset:**
   - If `--style-preset` is provided, use it. Read the style anchor from `<plugin>/docs/style-presets.md` for that slug.
   - Else if `.great-authors/project.md` has a `## Visual` section with a `Style preset:` field, use that.
   - Else default to `pen-and-ink-editorial` for fiction; `photoreal-cinematic` for nonfiction (genre signal from `.great-authors/project.md`).
   - If no style-presets.md exists or the slug isn't found, dispatch with no preset — the director writes a custom style anchor based on the project's voice.

4. **Resolve the director:**
   - `--director` if provided
   - Else default `hitchcock` for fiction (mystery, thriller, crime, literary fiction)
   - For very landscape-driven work (Western, nature writing), default to `kurosawa`
   - For natural-light intimate register (literary nonfiction, family memoir), default to `deakins`
   - Document the choice in the output file's frontmatter

5. **Read the bible files** the director will need:
   - `.great-authors/project.md`
   - `.great-authors/voice.md`
   - `.great-authors/visual-lints.md` (if present — v1.5+ of great-authors)
   - Character files for any character named in the source
   - Place files for any location named in the source

6. **Dispatch the director persona** via the Agent tool with `subagent_type: "great-filmmakers:<director>-persona"`. The brief must include:
   - The source prose (full text, or the relevant section if `<source-file>` is a long manuscript chapter)
   - The bible files read above
   - The style preset and its anchor (verbatim)
   - The visual-lints negative-prompt section (verbatim, to be appended to every block's negative prompt)
   - The target cue count (or "use your judgment based on source length")
   - Whether to include prose anchors
   - The output format spec (below)
   - The output target path (`<out-dir>/PROMPTS.md`)

7. **Output format** — the director produces this exact structure:

```markdown
# <Source title> — Illustration Prompts

<One paragraph naming what these illustrations carry: which moments, what register, why these and not others. The director's editorial judgment about the source.>

---

### <slug-1>.png

**Style anchor (verbatim, prepend to every prompt):**
<style anchor block — exact text from style preset or visual-lints.md>

**Composition:** <The frame. Where the camera/eye sits, what occupies which thirds, what's in foreground vs. background.>

**Subject:** <Who or what is in the frame. Specific details — gestures, postures, objects in hand. Resolves character continuity locks from visual-lints.md.>

**Light:** <The lighting register. Natural / artificial, time of day, key source, contrast level.>

**Production design:** <Materials, period markers, props, setting details.>

**Negative prompt (must NOT appear):** <Forbidden elements — lifted from visual-lints.md if present, augmented with cue-specific refusals.>

**Aspect ratio:** <e.g., 16:9, 3:2, 4:3 — director chooses per cue>
**Format:** PNG

<If --include-prose-anchors:>
**Prose anchor:** "<50-150 char prose snippet from the source, immediately preceding this cue point>"

---

### <slug-2>.png

[same structure]

---

[...continues for all cue points...]
```

8. **Filename convention:** slugs follow `<chapter-or-prefix>-<scene-slug>` (e.g., `ch01-hands-folding`, `ch02-compound-gate`). For single-source files without chapter context, use just `<scene-slug>`. This matches the unified format adopted in trilogy-improvement #6.

9. **Save the output** to `<out-dir>/PROMPTS.md`. If a file exists at that path, ask whether to overwrite, append, or save as `PROMPTS-v2.md`.

10. **Report:**
    ```
    📝 Saved to <out-dir>/PROMPTS.md (<N> cue points, drafted by <director>).

    Source:        <source-file>
    Style preset:  <slug or 'custom'>
    Cue points:    <list of slugs>
    With prose anchors: yes / no

    Next:
    - Render with: python3 scripts/render_keyframes.py --prompts-file <out-dir>/PROMPTS.md
    - Or wire into MDX with: python3 scripts/wire_book_illustrations.py (requires --include-prose-anchors set)
    ```

## What the skill does NOT do

- Does not render the images. That's downstream — `scripts/render_keyframes.py` (in the project, copied from `templates/scripts/`) handles the actual gpt-image-1 / Imagen / Leonardo calls.
- Does not deploy. The PROMPTS.md is a creative artifact; the user reviews; the render pass follows.
- Does not invent the visual register. The style anchor comes from `style-presets.md` or `.great-authors/project.md`'s `## Visual` section. The director's job is composition and subject choice within the established register, not register invention.
- Does not write prose. If the user wants a prose change to better support the illustration, dispatch back to `great-authors`.

## Cross-plugin orchestration

This skill produces an artifact that flows into multiple downstream pipelines:

- **Book illustrations** for great-publishers' book-site builder (`/publishers-build-book-site` v0.2+) — the matched illustrations are wired into chapter MDX
- **Video keyframes** for great-filmmakers' Kling/Runway image-to-video renders — keyframes condition the first frame of each shot
- **Cover concepts** for great-publishers' cover-design skills (`/publishers-design-cover` v1.0+) — the brief grounds the cover concept in actual scenes

The output format is intentionally backend-agnostic so the same PROMPTS.md can drive different render scripts.

## Notes

- **The director's editorial judgment matters.** Hitchcock identifying cue points in a mystery is different from Kurosawa identifying them in a Western. The director's voice carries through which moments they choose to render visually. This is the value the skill provides over hand-writing prompts.
- **Re-running the skill on the same source** with a different director produces a meaningfully different PROMPTS.md. Useful for: comparing visual interpretations; producing a primary illustration set + an alternate cover-art set from the same source.
- **The PROMPTS.md format is the canonical contract** — see `docs/output-formats.md` § "Image-generation backends" for the full spec including negative-prompt conventions per backend, aspect-ratio considerations per use case, and prompt-length limits per model. (Image-gen backend section landed in v1.7.)
- **Visual-lints awareness:** when `.great-authors/visual-lints.md` exists (v1.5+ of great-authors), the director reads it before identifying cue points. The forbidden-elements list becomes the baseline of every prompt's negative-prompt section; the director adds cue-specific refusals on top.
