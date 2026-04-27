---
name: filmmakers-crew
description: The backend-aware pipeline command. Turns a source file (blog post, manuscript chapter, scene notes) into a complete film treatment across the appropriate specialists for a chosen video backend. Usage - /filmmakers-crew <source-file> [--backend heygen|veo3|remotion] [--director <name>] [--writer <name>] [--avatar <name>]. HeyGen backend produces a single-avatar script; Veo 3 backend produces a multi-character production doc with CAST, VISUAL GRAMMAR, SHOT LIST; Remotion backend produces a slideshow-compatible script. Auto-selects backend from source classification if omitted.
---

# /filmmakers-crew <source-file> [options]

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

2. **Verify the file exists** and `.great-authors/` is present in its parent directory tree. If no bible, tell the user: "The /filmmakers-crew command works best with a project bible. Run `/authors-project-init` (from great-authors-plugin) and `/filmmakers-project-init` first." Proceed anyway if the user confirms.

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

   Next step (v1.5+ — direct submission):
   set -a && source ~/.config/dev-secrets/secrets.env && set +a
   python3 <plugin-path>/scripts/heygen-submit.py film/screenplay/<slug>.heygen.md
   # MP4 lands at film/screenplay/<slug>.mp4

   Pre-flight check: HeyGen API tier credit is separate from web-app credit.
   If the submit fails with MOVIO_PAYMENT_INSUFFICIENT_CREDIT, fund at
   https://app.heygen.com/settings?nav=API before retrying.

   Avatar IDs resolve from $HEYGEN_<NAME>_TALKING_PHOTO_ID and
   $HEYGEN_<NAME>_VOICE_ID in canonical secrets. The avatar_name in the
   doc's frontmatter (e.g. "Seth", "Maya") drives the resolution.
   See docs/output-formats.md § "Avatar registry" for the full pattern.
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
   - Schoonmaker: reads the draft SHOT LIST, assigns durations, flags the peak shot. **For Path A (Veo 3.0 Fast), durations MUST be quantized to {4, 6, 8} seconds.** **For Path B (Veo 3.1 Fast preview with reference images), every shot is 8 seconds.** Schoonmaker's persona file covers the craft reasoning for both paths.
   - Zimmer: reads the draft SHOT LIST, inserts audio cues (ambient sound, dialogue pacing, music direction) into each shot prompt.
   - Both their outputs are applied as edits to `film/screenplay/<slug>.veo3.md` — not written to separate files.

   **Veo 3 production constraints** (see `docs/output-formats.md` § "Veo 3 production constraints" for the full Path A vs Path B discussion):

   **Path A — Veo 3.0 Fast + inline anchoring (default):**
   - `veo_model`: `veo-3.0-fast-generate-001`. Fall back to `veo-3.0-generate-001` (4× cost) if Fast quota is exhausted.
   - Durations quantized to {4, 6, 8}.
   - Do NOT include `personGeneration` or `referenceImages` fields in the API submission.
   - Every shot prompt must include the full character description for every character in frame — inline anchoring is the continuity mechanism.

   **Path B — Veo 3.1 Fast preview + reference images (stronger continuity):**
   - `veo_model`: `veo-3.1-fast-generate-preview`. Requires the upgraded Gemini API tier.
   - All durations fixed at 8 seconds. `aspectRatio: "16:9"` mandatory.
   - Pass up to 3 reference images per shot via `referenceImages` array using the forum-confirmed shape (flat `bytesBase64Encoded` + `mimeType`, `referenceType: "asset"` lowercase). The Google docs page shows an `inlineData` wrapper that the API rejects — don't trust it.
   - Cannot combine `referenceImages` with `image` (init frame) or `lastFrame`.

   **Both paths:** prepend the active style preset paragraph (see `docs/style-presets.md`) verbatim at the start of every shot prompt.

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

6. **Machine-readable footer.** Every artifact produced by `/filmmakers-crew` MUST end with the machine-readable footer specified in `docs/output-formats.md`. This is the stable contract for downstream pipelines.

## Shared notes

- All sub-agents inherit cwd and read `.great-authors/` per their `## Before you work` protocol.
- If the chosen director or writer has no established workflow for the backend (e.g., Lynch for HeyGen educational), the skill proceeds but warns the user that the combination may produce off-voice output.
- The skill writes files. This is distinct from `/filmmakers-edit` / `/filmmakers-critique` / `/filmmakers-debate`, which only output to stdout.
- Files are written to `film/<subdir>/<slug>.<backend>.md` (or `<slug>.md` for non-screenplay artifacts). Resolve `<slug>` from `--scene` arg, else from the source file's basename.

## Error handling

- If a sub-agent returns thin output, redispatch with more context before moving to the next stage. The pipeline is sequential across stages; parallelism is within a stage.
- If a required sub-agent fails completely, abort the pipeline and report which stage failed. Don't produce a partial artifact — it would silently corrupt the downstream pipeline.
