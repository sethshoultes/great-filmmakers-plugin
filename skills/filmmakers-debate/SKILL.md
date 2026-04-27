---
name: filmmakers-debate
description: Run a 2-round craft debate between two named filmmakers on a specific passage or craft question. Round 1 - each states their position; Round 2 - each responds to the other. Consolidation names the real tension and picks a winner, a third way, or flags it as a genre/register call. Use when you genuinely don't know how to handle a craft choice (e.g., Kubrick vs. Scorsese on how to shoot this scene).
---

# /filmmakers-debate <passage-or-topic> <filmmaker-A> <filmmaker-B>

Two-round craft dispute resolution.

## When to use

- You have a craft choice and two filmmakers would clearly disagree. You want the real tension surfaced, not a split-the-difference answer.
- Classic pairings: Kubrick vs. Scorsese (control vs. kinetic); Hitchcock vs. Spielberg (suspense vs. emotion); Deakins vs. Ferretti (light vs. set); Kaufman vs. Rhimes (structural invention vs. serial momentum); Lynch vs. Kubrick (dream vs. composition).

Not for: general feedback (`/filmmakers-critique`); marked-up editorial pass (`/filmmakers-edit`); pipeline output (`/filmmakers-crew`).

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
