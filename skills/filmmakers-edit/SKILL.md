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

Not for: fast 3-bullet gut checks (use `/filmmakers-critique`); 2-round debates between two voices (use `/filmmakers-debate`); full pipeline output (use `/filmmakers-crew`).

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
