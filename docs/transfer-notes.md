# Notes for Claude Code Transfer — Persona Plugin Trilogy

**Date:** April 24, 2026
**Context:** Building three companion persona plugins — Great Minds, Great Authors, Great Filmmakers — following the same skill-based pattern. This file captures design decisions, recommendations, and open questions so nothing is lost when transferring to Claude Code for automation and integration work.

---

## The trilogy at a glance

| Plugin | Focus | Utility | Status |
|---|---|---|---|
| `great-minds` | Strategic decisions, leadership thinking | "What would they decide?" | Partially built (Jobs, Musk, Huang, Oprah, Rhetorician, Hemingway confirmed in `/mnt/skills/user/`) |
| `great-authors` | Prose craft, voice, editing | "How would they write/edit this?" | **Complete — 10 skills built** this session |
| `great-filmmakers` | Film craft across disciplines | "How would they shoot/write/cut/score/design this?" | Profile doc built; **12 skills pending** |

---

## Design decisions locked in (across all three plugins)

### Naming convention
- Plugin-level: `great-minds`, `great-authors`, `great-filmmakers` (no "persona" suffix on the plugin)
- Skill-level: `first-last-persona` format (e.g. `ernest-hemingway-persona`, `martin-scorsese-persona`)
- Matches existing `steve-jobs-persona`, `elon-musk-persona` convention

### Frontmatter pattern
```yaml
---
name: first-last-persona
description: "Roleplay as [Name] for [primary utility]. Use this skill whenever [clear triggers]. Also trigger when someone mentions [specific phrases]. Do NOT use for [exclusions]."
---
```
Description should include: primary utility, trigger phrases, and explicit exclusions (biography, literary/film analysis, reproducing actual work).

### Skill file structure (shared pattern)
1. Opening identity paragraph — "You are X. Not a summary. Not an impression."
2. Voice and temperament
3. Core principles (or "The X rules" for writers/directors with codified rules)
4. Primary utility section (specialty-specific — see below)
5. How to draft/create in their voice (secondary mode)
6. Things you never do
7. When another [mind/author/filmmaker] would serve better (cross-references)
8. Staying in character

### Primary utility sections by plugin
| Plugin | Primary utility section |
|---|---|
| Great Minds | Decision framework / strategic breakdown |
| Great Authors | How to edit a draft (numbered sequence of moves) |
| Great Filmmakers (directors) | How to break down a scene |
| Great Filmmakers (writers) | How to structure a script / hook an opening |
| Great Filmmakers (DP) | How to shot-list a scene |
| Great Filmmakers (editor) | How to find the cut |
| Great Filmmakers (composer) | How to score a scene |
| Great Filmmakers (prod designer) | How to build the world of a frame |

### Copyright boundary — non-negotiable
Every skill file must include, in its own language: **"Never reproduce your actual published work — write new things in the same way."** Same for films, scores, designs. This sidesteps the IP issue cleanly.

### Editorial/breakdown mode as default
When source material is in context (a draft, a script, a book, a blog post), the skill opens in **critique/breakdown mode** — that's the highest utility. Generation mode ("write something new in this voice") only when explicitly asked.

### Cross-references
One sentence per sibling, naming specific failure modes they fix better. Cross-**plugin** references are valid — e.g., the Shonda Rhimes filmmaker skill can point to `great-minds/aaron-sorkin-persona` for political-drama dialogue, because Sorkin is already in Great Minds. **Bake these into the skill files directly — no additional routing infrastructure needed.**

---

## Great Filmmakers — the 12

**Directors (6):** Kubrick, Kurosawa, Scorsese, Hitchcock, Spielberg, Lynch
**Writers (2):** Shonda Rhimes, Charlie Kaufman
**Specialists (4):** Roger Deakins (DP), Thelma Schoonmaker (editor), Hans Zimmer (composer), Dante Ferretti (production designer)

**Spielberg debated, kept.** He's not redundant with Scorsese — Scorsese is kinetic stylist; Spielberg is master of blocking-for-emotion. Different craft.

**Not included in v1, flagged for v2:**
- Tarkovsky (too specialized for broad utility)
- Wong Kar-wai (adjacent to Deakins; revisit if needed)
- Varda (humanist/documentary — worth revisiting)
- Coppola (overlap with Scorsese)
- Miyazaki (animation-specific; worth a whole animation bundle someday)
- Morricone (considered over Zimmer — Zimmer won for teachability and genre range)
- Additional production designers (Rick Carter, Stuart Craig) considered; Ferretti chosen for range

**Shonda special case:** She's a showrunner, not a film director. Her skill file calls this out explicitly — her utility is TV/streaming pilot structure, serialized drama, ensemble scenes, dialogue. The naming "filmmaker" is loose; she's included because what most writers today actually need is scene-to-scene momentum for serialized content, which is her superpower.

---

## Claude Code integration — recommendations

### Installation strategy
Each plugin lives in its own repo or folder:
```
~/.claude/skills/great-minds/
~/.claude/skills/great-authors/
~/.claude/skills/great-filmmakers/
```
Each skill inside its own subdirectory:
```
~/.claude/skills/great-authors/ernest-hemingway-persona/SKILL.md
```

### Plugin-level README files
Each plugin needs a top-level README.md that:
- Explains the philosophy (what this plugin is for)
- Lists all personas with one-line use cases
- Provides a "which persona when" decision guide
- Notes cross-plugin relationships
- Includes install instructions

**Not built yet for any of the three.** Do this when the plugin trilogy is complete and before any public release.

### Cross-plugin orchestration — "film crew assembler"
The natural Claude Code automation is: give Claude a source text (blog post, book chapter, script) and a target (script, scene, shot list, cue) and let it chain the right personas together. Example flow:

```
User: "Turn this blog post into a Scorsese-directed scene"

Claude Code pseudo-flow:
1. Invoke charlie-kaufman-persona to adapt prose → screenplay form
2. Invoke martin-scorsese-persona to break down the scene (blocking, camera, music)
3. Invoke roger-deakins-persona to shot-list
4. Invoke hans-zimmer-persona to suggest score approach
5. Invoke thelma-schoonmaker-persona to describe the cut
```

This could be:
- A slash command (`/film-crew`) that takes source + director
- A prompt template
- A proper agent that orchestrates specialized sub-agents

**Recommendation: start with a slash command, not an agent.** Agents add complexity. A well-crafted prompt template that invokes the right skills in sequence will solve 80% of the use case without the orchestration overhead.

### Integration with existing Caseproof work
- **Per My Last Prompt video series:** The Great Filmmakers plugin is directly useful here. Scorsese or Hitchcock personas for scene breakdown; Kaufman for script punch-up; Schoonmaker for edit rhythm guidance; Zimmer for music direction notes.
- **HeyGen scripts:** Shonda Rhimes persona for dialogue; Sorkin (in great-minds) for tech-flavored punch-up.
- **Persona skills already in use (Jobs, Oprah, Musk, Rhetorician):** These are the anchors of the great-minds plugin. Worth formalizing the plugin structure around them at some point.

### Naming decision for Great Minds
The existing personas aren't currently in a plugin structure — they're loose in `/mnt/skills/user/`. When formalizing the trilogy, decide:
- Keep them loose (they work; don't break what works)
- Consolidate into `great-minds/` (cleaner architecture, but requires moving files)
- Hybrid — keep originals in place, also package as a plugin for public distribution

**Recommendation: hybrid.** Keep working versions where they are. Create `great-minds/` as a distribution package when you're ready to share publicly.

---

## Open design questions to resolve in Claude Code

1. **Should the plugins support a "council" mode?** e.g., "Show me this blog post critiqued by all four directors at once." Low-effort to implement via prompt; high utility for creative decisions.

2. **Should there be a plugin-level `INDEX.md`?** Lists all personas with triggers. Could help Claude find the right persona when the user describes a problem vaguely ("I need help writing a moody scene"). Or could be overkill — description fields in frontmatter should handle this.

3. **Versioning.** When a persona skill gets refined based on use, how do we version it? Git tags per plugin? Semver on each skill? Probably overkill for v1 — just commit to a repo and move on.

4. **Per My Last Prompt integration.** If the Great Filmmakers plugin is live, does the next episode of Per My Last Prompt build around it? Natural subject matter.

---

## Build sequence recommendation

When you resume in Claude Code:

1. **Build the 12 Great Filmmakers skill files** following the Great Authors template. Order suggested in profile doc: Scorsese → Kubrick → Shonda → Deakins → Schoonmaker → rest.

2. **Write plugin README.md for each of the three plugins.** Template:
   - Philosophy (2-3 paragraphs)
   - Personas with use cases (table)
   - "Which persona when" decision tree
   - Cross-plugin relationships
   - Install instructions
   - License/contribution info if public

3. **Test-drive one persona from each plugin.** Real work, real output. Catch pattern issues before propagating.

4. **Build `/film-crew` slash command** (or equivalent) that orchestrates the filmmaker personas on a piece of source material.

5. **Formalize the Great Minds plugin** — decide on hybrid vs. consolidated structure, package for distribution if going public.

6. **Decide on distribution.** GitHub public repo like the existing Great Minds plugin? Caseproof internal? Personal? Each has different packaging requirements.

---

## Files produced in this session

All in `/mnt/user-data/outputs/`:

**Great Authors (10 skills + profile doc):**
- `great-authors-profiles.md`
- `ernest-hemingway-persona/SKILL.md` (already installed under `/mnt/skills/user/`)
- `george-orwell-persona/SKILL.md`
- `joan-didion-persona/SKILL.md`
- `john-mcphee-persona/SKILL.md`
- `stephen-king-persona/SKILL.md`
- `kurt-vonnegut-persona/SKILL.md`
- `james-baldwin-persona/SKILL.md`
- `cormac-mccarthy-persona/SKILL.md`
- `david-foster-wallace-persona/SKILL.md`
- `ursula-k-le-guin-persona/SKILL.md`

**Great Filmmakers (profile doc, skills pending):**
- `great-filmmakers-profiles.md`

**This file:**
- `claude-code-transfer-notes.md`

---

## Contextual reminders for future sessions

- **All deliverables in markdown only.** Per standing preferences.
- **Asana is marketing-only** at Caseproof. Don't create Asana tasks for engineering or plugin work.
- **Working solo or with small team.** Plugin architecture should be lean; don't over-engineer.
- **DFW sensitivity flagged in his skill file** — the skill includes explicit guidance to not engage with questions about his death. Keep that as a model for any future persona where a similar issue applies.
