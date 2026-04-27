---
name: filmmakers-critique
description: Fast 3-bullet verdict on a source file from 3 filmmaker personas in parallel. Haiku-dispatched for speed and cost. Default triad covers director + writer + craft specialist (e.g., Scorsese + Rhimes + Deakins) — three dimensions of feedback in one shot. Use when you want triage before investing in a full /filmmakers-edit or /filmmakers-crew pass.
---

# /filmmakers-critique <file> [filmmaker...]

Fast gut-check triage.

## When to use

- You want a directional read on a scene or script before running the full pipeline.
- You're deciding which filmmakers to run `/filmmakers-edit` with — use critique to narrow down.
- You want to see which of three disciplines (direction, writing, craft) has the strongest reaction.

Not for: marked-up breakdowns (that's `/filmmakers-edit`); 2-round debates (that's `/filmmakers-debate`); full pipeline output (that's `/filmmakers-crew`).

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
