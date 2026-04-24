# Great Filmmakers v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans.

**Goal:** Ship v1.0 of the `great-filmmakers` Claude Code plugin — four orchestration slash commands (`/filmmakers-edit`, `/filmmakers-critique`, `/filmmakers-debate`, `/film-crew`) that fan out to the twelve v0.1 personas and consolidate their output. The unique value-add is `/film-crew`, a backend-aware pipeline that produces HeyGen / Veo 3 / Remotion-ready artifacts.

**Architecture:** Four new skill SKILL.md files under `skills/`. No agent changes. All orchestration lives in the skills themselves — the fan-out instructions to Claude tell it which personas to dispatch and how to consolidate. `/film-crew` is the biggest of the four, with distinct execution models per backend (HeyGen sequential+parallel vs. Veo 3 parallel-then-sequential). Output formats already documented in `docs/output-formats.md` from v0.1 — skills emit against that spec.

**Tech stack:** Same as v0.1 — bash + markdown + YAML frontmatter. No runtime code. Claude Code's Agent tool handles the sub-agent dispatch with optional `model: "haiku"` override for `/filmmakers-critique`.

**Prerequisites:**
- v0.1 is pushed (`origin/main` at `26cc4e0`, tag `v0.1.0` exists)
- Clean working tree on `main`
- All 12 persona agents exist and validate

---

## File structure for v1.0

```
great-filmmakers-plugin/
├── skills/                            # 2 existing + 4 new
│   ├── filmmakers-channel/SKILL.md    # (v0.1, unchanged)
│   ├── film-project-init/SKILL.md     # (v0.1, unchanged)
│   ├── filmmakers-edit/SKILL.md       # Task 3 (new)
│   ├── filmmakers-critique/SKILL.md   # Task 4 (new, Haiku dispatch)
│   ├── filmmakers-debate/SKILL.md     # Task 5 (new)
│   └── film-crew/SKILL.md             # Task 6 (new, backend-aware pipeline)
├── .claude-plugin/plugin.json         # Task 2 (version bump)
├── .claude-plugin/marketplace.json    # Task 2 (description)
├── package.json                       # Task 2 (version bump)
└── README.md                          # Task 7 (add 4 commands to table, roadmap cleanup)
```

No agent changes. No `docs/` changes — `docs/output-formats.md` already covers the formats these skills emit against.

---

## Tasks

### Task 1: Verify state

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git branch --show-current && git status && \
  git fetch origin && git log --oneline origin/main..main && \
  git tag --list | grep v0.1
```

Expected: `main`, clean, synced with origin, `v0.1.0` tag exists.

No commit.

---

### Task 2: Version bump

- [ ] **Step 1: Update manifests**

- `.claude-plugin/plugin.json`: `"version": "0.1.0"` → `"version": "1.0.0"`
- `package.json`: same bump
- `.claude-plugin/marketplace.json` — replace the plugin description with the v1.0 scope:
  ```
  "description": "12 filmmaker personas + 6 slash commands including /film-crew (backend-aware pipeline that emits HeyGen, Veo 3, or Remotion-ready artifacts). Shares the .great-authors/ bible with great-authors-plugin."
  ```

- [ ] **Step 2: Validate + commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))" && \
  python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))" && \
  python3 -c "import json; json.load(open('package.json'))" && \
  git add .claude-plugin/ package.json && \
  git commit -m "chore: bump version to 1.0.0"
```

---

### Task 3: Write /filmmakers-edit skill

**Files:** Create `skills/filmmakers-edit/SKILL.md`

Fan-out + consolidation pattern, adapted from `/authors-edit`. Auto-selects filmmakers by content type when none specified.

- [ ] **Step 1: Write the SKILL.md**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/skills/filmmakers-edit/SKILL.md`:

```markdown
---
name: filmmakers-edit
description: Run a multi-filmmaker editorial pass on a source file (blog post, manuscript chapter, screenplay, scene notes). Usage - /filmmakers-edit <file> [filmmaker1 filmmaker2 ...]. If no filmmakers specified, auto-picks 2 based on genre signals. Each returns a scene breakdown in their role's format; consolidation merges into one view with consensus, disagreement, and handoff suggestions. Use when you want deep multi-discipline feedback before drafting film artifacts.
---

# /filmmakers-edit <file> [filmmaker...]

The multi-discipline editorial command. Fans out to 1-2 filmmaker personas; consolidates their output.

## When to use

- You have a draft scene (prose or screenplay) and want two or more craft voices on it.
- You want both a director's take AND a specialist's take (e.g., Scorsese + Deakins, or Kubrick + Zimmer).
- You're deciding between two directors for the same material — `/filmmakers-edit` runs both in parallel and shows you where they agree and diverge.

Not for: fast 3-bullet gut checks (use `/filmmakers-critique`); 2-round debates between two voices (use `/filmmakers-debate`); full pipeline output (use `/film-crew`).

## Instructions for Claude

When this skill is invoked:

1. **Parse arguments:**
   - First positional: file path (required). If missing, ask.
   - Remaining positionals: zero or more filmmaker names. Valid slugs: `scorsese`, `kubrick`, `kurosawa`, `hitchcock`, `spielberg`, `lynch`, `rhimes`, `kaufman`, `deakins`, `schoonmaker`, `zimmer`, `ferretti`. Short forms accepted (marty, stanley, hitch, shonda, etc.).

2. **Verify the file exists.** If not, stop.

3. **If no filmmakers named, auto-select 2** based on content signals:
   - Inspect the first 500 words.
   - **Kinetic drama / character-driven fiction** → Scorsese + Schoonmaker
   - **Cold formal / procedural** → Kubrick + Deakins
   - **Suspense / thriller** → Hitchcock + Zimmer
   - **Populist / family / wonder** → Spielberg + Zimmer
   - **Dream-logic / uncanny** → Lynch + Ferretti
   - **Weather / group / historical** → Kurosawa + Ferretti
   - **Serialized TV / dialogue-heavy** → Rhimes + Schoonmaker
   - **Structural / metafictional** → Kaufman + Schoonmaker
   - **Purely visual / shot-specific** → Deakins + Ferretti
   - **Ambiguous** → Scorsese + Deakins (safe generalist pair)

   Announce your selection: "No filmmakers specified — picking <A> and <B> based on <signal>. Ok, or override?" Accept "ok" or a new list.

4. **Fan out via Agent tool.** Dispatch all selected filmmakers in parallel (single message, multiple Agent calls):
   - `subagent_type: <slug>-persona`
   - Prompt includes:
     - The full text of the file
     - Instructions: "Read the source. Apply your `## How to <primary utility>` workflow. Return:
       - **Top-line verdict** — one sentence, what you think of this as a piece you'd work on.
       - **Breakdown** — your role's structured output (scene breakdown for directors, shot list for Deakins, cut notes for Schoonmaker, cue sheet for Zimmer, design notes for Ferretti, script-level notes for writers).
       - **One handoff** — if a different filmmaker in the roster would serve this better, name them and why. Omit if you're the right voice.
     - The `## Before you work` protocol — read the bible if it exists.

5. **Consolidate.** Produce one output:

   ```markdown
   # /filmmakers-edit on <filename> — <filmmaker A> + <filmmaker B>

   **<A>'s verdict:** <one sentence>
   **<B>'s verdict:** <one sentence>

   ## Where they agree
   (1-3 concrete points both filmmakers raised)

   ## Where they disagree
   (1-2 points of divergence, or "no significant disagreement")

   ## Highest-leverage change
   (pick ONE thing that would most improve the piece)

   ## Breakdowns

   ### <A>'s breakdown
   <A's structured output verbatim>

   ### <B>'s breakdown
   <B's structured output verbatim>

   ## Handoffs
   (Any cross-reference suggestions from the filmmakers, listed here with next-step commands.)
   ```

6. **Output to stdout.** Does NOT write files. The user saves via `/filmmakers-channel` save triggers afterward if desired.

## Notes

- All sub-agents inherit cwd; if `.great-authors/` or `film/` exists, they'll read per their `## Before you work` protocol.
- Fan-out should be parallel — dispatch all Agent calls in a single message using multiple tool-use blocks.
- If any sub-agent returns thin or off-topic output, consolidate with what succeeded. Don't block the whole command on one failure.
- If the user passes >2 filmmakers, dispatch all of them. Consolidation scales.
```

- [ ] **Step 2: Verify frontmatter**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  head -3 skills/filmmakers-edit/SKILL.md && \
  grep -E "^(name|description): " skills/filmmakers-edit/SKILL.md
```

Expected: valid frontmatter.

- [ ] **Step 3: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add skills/filmmakers-edit/ && \
  git commit -m "feat: add /filmmakers-edit skill"
```

---

### Task 4: Write /filmmakers-critique skill (Haiku dispatch)

**Files:** Create `skills/filmmakers-critique/SKILL.md`

Fast 3-bullet verdict from 3 filmmakers in parallel. Haiku-dispatched per the model-split pattern proven in great-authors v0.6.

- [ ] **Step 1: Write the SKILL.md**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/skills/filmmakers-critique/SKILL.md`:

```markdown
---
name: filmmakers-critique
description: Fast 3-bullet verdict on a source file from 3 filmmaker personas in parallel. Haiku-dispatched for speed and cost. Default triad covers director + writer + craft specialist (e.g., Scorsese + Rhimes + Deakins) — three dimensions of feedback in one shot. Use when you want triage before investing in a full /filmmakers-edit or /film-crew pass.
---

# /filmmakers-critique <file> [filmmaker...]

Fast gut-check triage.

## When to use

- You want a directional read on a scene or script before running the full pipeline.
- You're deciding which filmmakers to run `/filmmakers-edit` with — use critique to narrow down.
- You want to see which of three disciplines (direction, writing, craft) has the strongest reaction.

Not for: marked-up breakdowns (that's `/filmmakers-edit`); 2-round debates (that's `/filmmakers-debate`); full pipeline output (that's `/film-crew`).

## Instructions for Claude

When this skill is invoked:

1. **Parse arguments:** file path (required) + optional filmmaker names.

2. **Verify the file exists.**

3. **If no filmmakers named, pick 3** using a triad strategy — one director, one writer, one craft specialist, selected by content signal:
   - **Kinetic drama** → Scorsese + Rhimes + Deakins
   - **Cold formal** → Kubrick + Kaufman + Deakins
   - **Suspense** → Hitchcock + Kaufman + Zimmer
   - **Populist** → Spielberg + Rhimes + Zimmer
   - **Arthouse / dream** → Lynch + Kaufman + Ferretti
   - **Historical / weather** → Kurosawa + Rhimes + Ferretti
   - **Ambiguous** → Scorsese + Rhimes + Deakins (safe triad)

4. **Fan out via Agent tool. USE HAIKU.** Dispatch all 3 in parallel in a single message. For each:
   - `subagent_type: <slug>-persona`
   - **`model: "haiku"`** (override — critique is opinion-style and tolerates the cheaper model)
   - Prompt:
     ```
     CRITIQUE MODE — TERSE OUTPUT ONLY.

     Read this source and respond with EXACTLY 3 bullets. Each bullet is one sentence. No introduction. No structured breakdown. No rewrites. Just the three most important things you notice.

     End with one line: "If I'm not the right voice here, try <X>." — or omit if you are.

     Source:
     <full file contents>
     ```

5. **Consolidate:**

   ```markdown
   # /filmmakers-critique on <filename> — <A>, <B>, <C>

   ## <A>
   - <bullet 1>
   - <bullet 2>
   - <bullet 3>

   ## <B>
   ...

   ## <C>
   ...

   ## Consensus
   (one sentence naming what all or most flagged)

   ## Sharpest disagreement
   (one sentence, or "no significant disagreement")

   ## Handoffs
   (if any filmmaker suggested a different voice, name them with next-step command)
   ```

6. **Output to stdout.** No file writes.

## Notes

- Haiku override is critical — the whole point of this command is speed and cost. If you find critiques losing quality on Haiku (personas drift off-voice, cross-refs hallucinate), drop the override in the Agent call and fall back to the agent's default Sonnet.
- TERSE prefix is already in the dispatch prompt. Haiku honors it.
- Sub-agents inherit cwd; bible read per `## Before you work` protocol.
```

- [ ] **Step 2: Verify**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  head -3 skills/filmmakers-critique/SKILL.md && \
  grep "model: \"haiku\"" skills/filmmakers-critique/SKILL.md
```

Expected: frontmatter present; haiku override instruction present.

- [ ] **Step 3: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add skills/filmmakers-critique/ && \
  git commit -m "feat: add /filmmakers-critique skill (Haiku-dispatched triage)"
```

---

### Task 5: Write /filmmakers-debate skill

**Files:** Create `skills/filmmakers-debate/SKILL.md`

Two-round craft dispute, parallel to `/authors-debate`.

- [ ] **Step 1: Write the SKILL.md**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/skills/filmmakers-debate/SKILL.md`:

```markdown
---
name: filmmakers-debate
description: Run a 2-round craft debate between two named filmmakers on a specific passage or craft question. Round 1 - each states their position; Round 2 - each responds to the other. Consolidation names the real tension and picks a winner, a third way, or flags it as a genre/register call. Use when you genuinely don't know how to handle a craft choice (e.g., Kubrick vs. Scorsese on how to shoot this scene).
---

# /filmmakers-debate <passage-or-topic> <filmmaker-A> <filmmaker-B>

Two-round craft dispute resolution.

## When to use

- You have a craft choice and two filmmakers would clearly disagree. You want the real tension surfaced, not a split-the-difference answer.
- Classic pairings: Kubrick vs. Scorsese (control vs. kinetic); Hitchcock vs. Spielberg (suspense vs. emotion); Deakins vs. Ferretti (light vs. set); Kaufman vs. Rhimes (structural invention vs. serial momentum); Lynch vs. Kubrick (dream vs. composition).

Not for: general feedback (`/filmmakers-critique`); marked-up editorial pass (`/filmmakers-edit`); pipeline output (`/film-crew`).

## Instructions for Claude

1. **Parse arguments:**
   - First: `<passage-or-topic>` (required). Can be a quoted passage string or a file path. If the token resolves to a file, read it.
   - Then: `<filmmaker-A>` and `<filmmaker-B>` (both required). Must be two different filmmakers from the v0.1 roster.

2. **If passage is a file path,** read the file. If inline, use as-is.

3. **Round 1 — parallel.** Dispatch both filmmakers in one message (two Agent calls):
   - `subagent_type: <slug>-persona` for each
   - Prompt:
     ```
     DEBATE ROUND 1.

     The topic: <passage or topic, full text>

     State your position in 3-5 sentences. What would you do with this, given your craft? Why? What would be wrong with treating it another way? Be specific about craft reasoning. Do NOT hedge.

     Do NOT respond to other voices — you don't know what they'll say. State your own position.
     ```

4. **Round 2 — parallel.** Once both Round 1 responses are in, dispatch again:
   - Each filmmaker receives both Round 1 responses (their own + the opponent's).
   - Prompt:
     ```
     DEBATE ROUND 2.

     In Round 1 you said:
     <author's Round 1>

     <opposing filmmaker> said:
     <opposing's Round 1>

     Respond in 3-5 sentences:
     - What do you concede? (If nothing, say so.)
     - Where do you hold your position?
     - If you'd revise Round 1, how?
     ```

5. **Consolidate** (out of voice):

   ```markdown
   # /filmmakers-debate: <A> vs. <B>

   **Topic:** <passage or topic>

   ## Round 1

   ### <A>
   <R1 position>

   ### <B>
   <R1 position>

   ## Round 2

   ### <A>
   <R2 response>

   ### <B>
   <R2 response>

   ## The real tension

   (One or two sentences naming what this dispute is actually about — usually a register, genre, or audience question.)

   ## Verdict

   Pick ONE:
   - **Winner:** <filmmaker> — <one sentence reason>
   - **Third way:** <a synthesis neither proposed>
   - **Genre call:** <the choice depends on <X>; here's how to decide>
   ```

6. **Output to stdout.** No file writes.

## Notes

- Debate requires two different filmmakers. If the user passes the same filmmaker twice, ask for a second.
- If either Round 1 is thin or off-topic, redispatch with clearer framing before moving to Round 2.
- The verdict section is the most valuable part. Don't hedge — if the tension is irreducibly genre-dependent, say so explicitly.
- Sub-agents inherit cwd; bible read per protocol. Both debaters respect `voice.md` if it exists (but can argue for what the voice SHOULD be if that's the debate).
```

- [ ] **Step 2: Verify + commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  head -3 skills/filmmakers-debate/SKILL.md && \
  git add skills/filmmakers-debate/ && \
  git commit -m "feat: add /filmmakers-debate skill (2-round craft dispute)"
```

---

### Task 6: Write /film-crew skill — the backend-aware pipeline

**Files:** Create `skills/film-crew/SKILL.md`

The biggest skill in v1.0. Three backends with different execution models; emits against the formats in `docs/output-formats.md`.

- [ ] **Step 1: Write the SKILL.md**

Write `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/skills/film-crew/SKILL.md`:

```markdown
---
name: film-crew
description: The backend-aware pipeline command. Turns a source file (blog post, manuscript chapter, scene notes) into a complete film treatment across the appropriate specialists for a chosen video backend. Usage - /film-crew <source-file> [--backend heygen|veo3|remotion] [--director <name>] [--writer <name>] [--avatar <name>]. HeyGen backend produces a single-avatar script; Veo 3 backend produces a multi-character production doc with CAST, VISUAL GRAMMAR, SHOT LIST; Remotion backend produces a slideshow-compatible script. Auto-selects backend from source classification if omitted.
---

# /film-crew <source-file> [options]

The film treatment pipeline. Source prose → backend-ready artifacts in `film/`.

## When to use

- You have a blog post, manuscript chapter, or scene notes and want a complete film treatment in one pass.
- You want the craft layer (filmmakers) AND the production-ready artifact (script for HeyGen / production doc for Veo 3 / slideshow script for Remotion) in the same command.
- You're iterating on a scene across multiple sessions and want consistent crew output.

Not for: single-discipline feedback (use `/filmmakers-channel` or `/filmmakers-edit`); fast triage (use `/filmmakers-critique`); craft debates (use `/filmmakers-debate`).

## Instructions for Claude

When this skill is invoked:

1. **Parse arguments:**
   - `<source-file>` (required) — path to source prose.
   - `--backend {heygen|veo3|remotion}` (optional) — explicit backend.
   - `--director <name>` (optional) — override the default director. Valid: `scorsese`, `kubrick`, `kurosawa`, `hitchcock`, `spielberg`, `lynch`.
   - `--writer <name>` (optional) — override the default adapter. Valid: `kaufman` (default), `rhimes`.
   - `--avatar <name>` (HeyGen only) — `maya | sara | rick | margaret | seth`. Auto-selects from source classification if omitted (MDX frontmatter `classification: maintenance` → maya, `cost` → sara, `comparison` → rick, `safety` → margaret). Default fallback: `maya`.
   - `--voice-id <id>` (HeyGen only) — override the HeyGen voice ID.
   - `--scene <slug>` (optional) — override the slug. Defaults to the source file's basename.

2. **Verify the file exists** and `.great-authors/` is present in its parent directory tree. If no bible, tell the user: "The /film-crew command works best with a project bible. Run `/authors-project-init` (from great-authors-plugin) and `/film-project-init` first." Proceed anyway if the user confirms.

3. **Resolve the backend:**
   - If `--backend` is passed, use it.
   - Else, auto-select from classification signals in the source:
     - **Educational / maintenance / cost / safety / how-to** → `heygen`
     - **Narrative / dialogue-heavy / multi-character / scene-driven / cinematic** → `veo3`
     - **Inspection-specific / brand-photo-required** → `remotion`
     - **Ambiguous** → ask the user rather than guess.

4. **Resolve the director, writer, avatar:**
   - Director default: `scorsese` (dramatic), or `spielberg` for populist/educational, or `kubrick` for cold/procedural. User override via `--director` always wins.
   - Writer default: `kaufman` (structural). If `--avatar sara` and no `--writer` passed, auto-default to `rhimes` (scrappy serialized momentum matches her style).
   - Avatar default (HeyGen only): from classification signals above.

5. **Execute the backend-specific pipeline:**

   ### HeyGen backend

   **Stage 1 (sequential):** Kaufman (or Rhimes) adapts the source into a HeyGen script.
   - Dispatch `<writer>-persona` via Agent tool.
   - Prompt: read the source + bible; produce a HeyGen script in the exact format from `docs/output-formats.md`. Include scene breakdown with Director's note lines reflecting the chosen director's craft sensibility (the writer pulls from the director's voice, the director does not write the script directly).
   - Write output to `film/screenplay/<slug>.heygen.md`.

   **Stage 2 (parallel):** Director + Schoonmaker produce edit notes.
   - Dispatch both in one message.
   - Director: breakdown of the scene informing pace and peak image.
   - Schoonmaker: cut rhythm, shot durations.
   - Write combined output to `film/edit-notes/<slug>.md` (director section first, `---` separator, Schoonmaker section second).

   **Skip** Deakins, Zimmer, Ferretti — HeyGen generates its own visuals and audio; their output would be discarded.

   **Stage 3 (consolidation):**

   ```
   HeyGen script: film/screenplay/<slug>.heygen.md
   Edit notes: film/edit-notes/<slug>.md
   Director: <name>. Writer: <name>. Avatar: <name>.

   Next step:
   cp film/screenplay/<slug>.heygen.md ../garagedoorscience/data/heygen-scripts/<slug>.md
   Then run the existing HeyGen Video Agent submit step in that project.
   ```

   ### Veo 3 backend

   **Stage 1 (parallel):** Ferretti (CAST bible + LOCATIONS + NEGATIVE PROMPT), Deakins (VISUAL GRAMMAR), Director (initial SHOT LIST sketch).
   - Dispatch all three in one message.
   - Each produces their section per `docs/output-formats.md` Veo 3 format.

   **Stage 2 (sequential):** Kaufman (or Rhimes) integrates all three outputs into the final production doc.
   - Dispatch `<writer>-persona` via Agent tool with all Stage 1 outputs as context.
   - Prompt: compose the production doc in the exact format from `docs/output-formats.md`. Use VISUAL GRAMMAR terms by name in each shot prompt. Expand Ferretti's CAST with full character descriptions. Apply the NEGATIVE PROMPT to each shot.
   - Write output to `film/screenplay/<slug>.veo3.md`.

   **Stage 3 (parallel):** Schoonmaker (shot durations + peak shot flag) and Zimmer (audio cues embedded in shot prompts).
   - Dispatch both in one message.
   - Schoonmaker: reads the draft SHOT LIST, assigns durations, flags the peak shot.
   - Zimmer: reads the draft SHOT LIST, inserts audio cues (ambient sound, dialogue pacing, music direction) into each shot prompt.
   - Both their outputs are applied as edits to `film/screenplay/<slug>.veo3.md` — not written to separate files.

   **Stage 4 (consolidation):**

   ```
   Veo 3 production doc: film/screenplay/<slug>.veo3.md
   Total shots: <N>
   Total duration: <N> seconds
   Director: <name>. Writer: <name>.

   Next step:
   cp film/screenplay/<slug>.veo3.md "$VEO_SCRIPTS_DIR/<episode>/<slug>.md"
   Then load the veo-builder dashboard at ~/Local Sites/veo-builder/ to see the production doc parsed.
   ```

   ### Remotion backend

   **Stage 1 (parallel):** Director + writer produce narration paragraphs; Zimmer produces `musicPromptFor()` tags.
   - Writer adapts source prose into narration paragraphs matching `docs/output-formats.md` Remotion format.
   - Zimmer produces music tags (category + tags).

   **Stage 2 (sequential):** Schoonmaker sets per-segment timing.

   **Write** to `film/screenplay/<slug>.remotion.md`.

   **Stage 3 (consolidation):** report the output path and suggest copying it into the `garagedoorscience/remotion/scripts/` pipeline.

6. **Machine-readable footer.** Every artifact produced by `/film-crew` MUST end with the machine-readable footer specified in `docs/output-formats.md`. This is the stable contract for downstream pipelines.

## Shared notes

- All sub-agents inherit cwd and read `.great-authors/` per their `## Before you work` protocol.
- If the chosen director or writer has no established workflow for the backend (e.g., Lynch for HeyGen educational), the skill proceeds but warns the user that the combination may produce off-voice output.
- The skill writes files. This is distinct from `/filmmakers-edit` / `/filmmakers-critique` / `/filmmakers-debate`, which only output to stdout.
- Files are written to `film/<subdir>/<slug>.<backend>.md` (or `<slug>.md` for non-screenplay artifacts). Resolve `<slug>` from `--scene` arg, else from the source file's basename.

## Error handling

- If a sub-agent returns thin output, redispatch with more context before moving to the next stage. The pipeline is sequential across stages; parallelism is within a stage.
- If a required sub-agent fails completely, abort the pipeline and report which stage failed. Don't produce a partial artifact — it would silently corrupt the downstream pipeline.
```

- [ ] **Step 2: Verify frontmatter**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  head -3 skills/film-crew/SKILL.md && \
  grep -E "^(name|description): " skills/film-crew/SKILL.md
```

Expected: valid frontmatter.

- [ ] **Step 3: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add skills/film-crew/ && \
  git commit -m "feat: add /film-crew skill (backend-aware pipeline for HeyGen/Veo 3/Remotion)"
```

---

### Task 7: Update README for v1.0

- [ ] **Step 1: Update the What's In section**

Edit `/Users/sethshoultes/Local Sites/great-filmmakers-plugin/README.md`:

Replace `## What's in v0.1` with `## What's in v1.0`.

- [ ] **Step 2: Update the Slash Commands table**

Replace:

```
### 2 Slash Commands

| Command | Purpose |
|---------|---------|
| `/filmmakers-channel <name>` | Load a filmmaker persona into the conversation with save triggers for five artifact types |
| `/film-project-init` | Scaffold a `film/` directory and register it in the project bible |

More orchestration commands (`/filmmakers-edit`, `/filmmakers-critique`, `/filmmakers-debate`, `/film-crew`) ship in v1.0.
```

With:

```
### 6 Slash Commands

| Command | Purpose |
|---------|---------|
| `/filmmakers-channel <name>` | Load a filmmaker persona into the conversation with save triggers for five artifact types |
| `/film-project-init` | Scaffold a `film/` directory and register it in the project bible |
| `/filmmakers-edit <file> [names...]` | Multi-filmmaker editorial pass with consolidated breakdowns |
| `/filmmakers-critique <file> [names...]` | Fast 3-bullet verdicts from 3 filmmakers in parallel (Haiku-dispatched) |
| `/filmmakers-debate <topic> <a> <b>` | 2-round craft dispute between two filmmakers |
| `/film-crew <file> [--backend ...]` | Backend-aware pipeline — produces HeyGen, Veo 3, or Remotion-ready artifacts |
```

- [ ] **Step 3: Update roadmap**

Replace:
```
## Roadmap

- **v1.0** — `/filmmakers-edit`, `/filmmakers-critique`, `/filmmakers-debate`, `/film-crew` (the backend-aware pipeline command)
- **Post-v1.0** — DXT distribution for Claude Desktop, builders (shot-builder, cue-builder), `/filmmakers-continuity`
```

With:
```
## Roadmap

- **Post-v1.0** — DXT distribution for Claude Desktop, builders (shot-builder, cue-builder, storyboard-builder), `/filmmakers-continuity`, additional filmmakers (Tarkovsky, Wong Kar-wai, Varda, Miyazaki, Morricone as Zimmer alternative)

All v1.0 goals shipped. Future work is driven by user feedback — open an issue at https://github.com/sethshoultes/great-filmmakers-plugin/issues.
```

- [ ] **Step 4: Commit**

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git add README.md && \
  git commit -m "docs: update README for v1.0 (orchestration commands + /film-crew)"
```

---

### Task 8: Push + tag v1.0.0

```bash
cd "/Users/sethshoultes/Local Sites/great-filmmakers-plugin" && \
  git push origin main && \
  git tag -a v1.0.0 -m "v1.0.0 — orchestration commands + /film-crew backend-aware pipeline" && \
  git push origin v1.0.0 && \
  gh api repos/sethshoultes/great-filmmakers-plugin/tags --jq '.[].name' | head -3
```

Expected: `v1.0.0` at top.

---

## Self-review

- **Spec coverage:** Section 3 (slash commands) — all four new commands covered in Tasks 3-6. Section 4 (output formats) — `/film-crew` emits against the existing `docs/output-formats.md` spec.
- **Placeholder scan:** clean. All behavioral instructions for each skill are complete.
- **Type consistency:** backend names (heygen/veo3/remotion) consistent across commands. Filmmaker slugs match v0.1 persona file names.
- **Risk:** the backend-aware pipeline model is untested. First real use on a garagedoorscience blog post or a veo-builder sitcom scene will reveal whether the prompts produce usable artifacts. Mitigation: the output formats are versioned in `docs/output-formats.md`; if the pipeline produces malformed artifacts, we fix the skill prompts without changing the contract.
