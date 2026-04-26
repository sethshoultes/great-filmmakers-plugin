# Great Filmmakers

Twelve filmmaker personas (6 directors + 2 writers + 4 craft specialists) plus slash commands for scene breakdown and film-craft work. A Claude Code plugin. Third in the Caseproof persona trilogy:

- [`great-minds-plugin`](https://github.com/sethshoultes/great-minds-plugin) — strategic decision-makers
- [`great-authors-plugin`](https://github.com/sethshoultes/great-authors-plugin) — prose craft
- **`great-filmmakers-plugin`** (this repo) — film craft

📖 **[Read the User Manual](docs/user-manual.md)** for the complete reference — install, all twelve personas, all five commands, the bible structure, backend selection, Veo 3 constraints, style presets, an end-to-end walkthrough, patterns, and troubleshooting.

## Install

```
/plugin marketplace add sethshoultes/great-filmmakers-plugin
/plugin install great-filmmakers@sethshoultes
```

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
