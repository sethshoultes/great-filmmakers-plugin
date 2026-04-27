---
name: filmmakers-project-init
description: Scaffold the film/ output directory at the project root (sibling to manuscript/) and add a ## Film section to .great-authors/project.md for tracking the current scene. Use when starting a writing project that will produce film artifacts via /filmmakers-channel save triggers or /filmmakers-crew. Assumes .great-authors/ already exists (run /authors-project-init from great-authors-plugin first if not).
---

# /filmmakers-project-init

Scaffold the `film/` directory and register it in the project bible.

## What this does

Creates a `film/` folder at the current working directory's project root with five empty subdirectories, plus a `scripts/` directory at the project root with three render-script templates copied in:

```
film/
├── screenplay/   # HeyGen scripts (.heygen.md), Veo 3 production docs (.veo3.md), Remotion scripts (.remotion.md)
├── shot-lists/   # DP shot breakdowns with timing
├── score-notes/  # Composer cue sheets with music prompt tags
├── storyboards/  # Production design notes with color palette, props, references
└── edit-notes/   # Director notes + editor cut notes

scripts/
├── render_keyframes.py        # gpt-image-1 → PNG keyframes / book illustrations from a director PROMPTS.md
├── render_kling.py            # Kling 2.5 image-to-video → MP4 (with chain conditioning)
├── render_veo.py              # Veo 3.0 Fast text-to-video → MP4 (durations quantized)
└── wire_book_illustrations.py # Wires rendered PNGs into Astro chapter MDX (fuzzy anchor matching)
```

The render scripts are project-owned once copied — edit them freely. Re-running this skill will not overwrite an existing `scripts/` directory.

Then adds a `## Film` section to `.great-authors/project.md`:

```markdown
## Film

**Path:** `film/` (at project root, sibling to `.great-authors/` and `manuscript/`)
**Current scene:** `<user-chosen-slug>`

Commands that generate film artifacts (`/filmmakers-channel` save triggers, `/filmmakers-crew` in v1.0) write to `film/<subdir>/<current-scene>.md` by default. Update `Current scene` when moving to the next scene.
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

5. **Copy render-script templates.** Resolve `../../templates/scripts/` relative to this SKILL.md and copy each `*.py` file into `<project>/scripts/`. Create `scripts/` if it doesn't exist. **Do not overwrite** existing scripts in the destination — if `<project>/scripts/render_kling.py` already exists, leave it alone and report which scripts were skipped. After copying, `chmod +x` each new script so they're directly runnable.

6. **Update `.great-authors/project.md`.** Read the existing file. If it already has a `## Film` section, ask whether to overwrite it. If not, append the `## Film` block documented above, substituting the user's chosen slug into `Current scene`.

7. **Report:**
   ```
   Created film/ with subdirs:
     screenplay/  shot-lists/  score-notes/  storyboards/  edit-notes/

   Copied render scripts into scripts/:
     render_keyframes.py  render_kling.py  render_veo.py  wire_book_illustrations.py
   (skipped <list> — already present)

   Updated .great-authors/project.md with ## Film section.
   Current scene: <slug>

   Next:
   - /filmmakers-crew <source-file> [--backend heygen|veo3|remotion] to generate a production doc.
   - Then run scripts/render_<backend>.py to turn the prompts into PNGs and MP4s.
     Source ~/.config/dev-secrets/secrets.env first so the API keys load.
   ```

## Notes

- This skill does not commit to git. The user owns their repository.
- The `film/` directory is for ARTIFACTS. The project bible stays at `.great-authors/`; the prose manuscript stays at `manuscript/`. Each has its own owner.
- If the user's project has no `.great-authors/` directory at all (working on a standalone scene or blog post), the skill still creates `film/` but emits a warning that personas won't have bible context to read before working.
