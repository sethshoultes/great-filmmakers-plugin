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
