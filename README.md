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
