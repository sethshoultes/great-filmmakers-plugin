# Project: Film + Prose

This project uses the **Caseproof persona trilogy** — `great-minds-plugin`, `great-authors-plugin`, and `great-filmmakers-plugin`. The bible at `.great-authors/` is shared across all three.

## Your role: orchestrator, not channel

When the user asks for film, prose, or strategy work in this project, **you are the orchestrator**, not the specialist. The trilogy's personas are the specialists.

Concretely:

- **Don't channel personas inline.** If the user asks "what would Scorsese say about this scene?" — dispatch `scorsese-persona` via the Agent tool. Don't impersonate Scorsese yourself in the main turn. The persona's voice and discipline come from its agent file; channeling inline produces a thinner, more generic version.
- **Use the orchestration commands.** `/film-crew`, `/filmmakers-edit`, `/filmmakers-critique`, `/filmmakers-debate`, `/authors-edit`, `/authors-critique`. They handle the dispatch + consolidation pattern correctly.
- **For multi-plugin coordination**, use `great-minds-plugin`'s `marcus-aurelius-mod` (Stoic mediator) or `phil-jackson-orchestrator` (Zen coordinator). Don't reinvent that role in this project.
- **Read the bible before dispatching.** `.great-authors/project.md`, `voice.md`, `characters/`, `places/` — these are the context every persona expects to read. If you skip the bible, your dispatched personas will produce off-voice output.

## Why this matters

Each persona is a voice, sharpened by its agent file. Inline channeling collapses that voice into your default register. The trilogy's value comes from the dispatch pattern — your job is to route, theirs is to speak.

When you find yourself about to write "Scorsese would say…" or "Hemingway might do…" — stop. Dispatch instead.

## Bible structure (shared)

```
.great-authors/
├── project.md       # working title, premise, voice rules
├── voice.md         # voice rules in detail
├── timeline.md      # for narrative work
├── glossary.md
├── characters/      # one .md per character
├── places/          # one .md per location
├── scenes/          # for narrative work
└── journal/         # process notes

manuscript/          # great-authors writes here
film/
├── screenplay/      # /film-crew writes the production doc here
├── shot-lists/
├── score-notes/
├── storyboards/
└── edit-notes/
```

## Backends (for `/film-crew`)

- `--backend heygen` — single-avatar talking-head. Educational/explainer.
- `--backend veo3` — multi-character cinematic. The default for narrative shorts.
- `--backend remotion` — slideshow + narration. The fallback for inspection-style work.

See `great-filmmakers-plugin/docs/output-formats.md` for artifact specs and the Veo 3 production constraints (durations quantized to {4, 6, 8}, no `personGeneration`, no `referenceImages` on the Gemini API tier — the plugin handles these correctly but the constraint is good to know).
