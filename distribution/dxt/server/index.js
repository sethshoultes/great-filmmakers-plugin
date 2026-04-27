#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PERSONAS_DIR = join(__dirname, "personas");

// Load all bundled persona files. Filenames carry a -persona suffix
// which is stripped from the lookup key.
const PERSONAS = Object.fromEntries(
  readdirSync(PERSONAS_DIR)
    .filter((f) => f.endsWith(".md"))
    .map((f) => {
      const slug = f.replace(/\.md$/, "").replace(/-persona$/, "");
      const body = readFileSync(join(PERSONAS_DIR, f), "utf8");
      return [slug, body];
    })
);

const FILMMAKER_BLURBS = {
  "scorsese": "Director. Visceral, propulsive cinema. Pace, music, kinetic camera. The dramatic-narrative default.",
  "kubrick": "Director. Cold procedural symmetry. Precision framing. The procedural-cool register.",
  "kurosawa": "Director. Landscape as character, weather as score. Wide-frame elemental composition.",
  "hitchcock": "Director. Suspense architecture. Camera as accomplice. The genre-fiction default.",
  "spielberg": "Director. Populist craft, emotional accessibility. The educational/explainer register.",
  "lynch": "Director. Dread under domestic surface. Sound design and tonal rupture.",
  "kaufman": "Writer-adapter. Structural; meta; voice on the page. The default writer for HeyGen + Veo3.",
  "rhimes": "Writer-adapter. Scrappy serialized momentum. Fits brand-personality and growth-driven projects.",
  "deakins": "Cinematographer. Natural light, restraint, observed rather than staged.",
  "schoonmaker": "Editor. Cut rhythm, shot durations, pace shifts.",
  "ferretti": "Production designer. Materials, locations, period markers, props. Builds CAST + LOCATIONS.",
  "zimmer": "Composer. Music as narrative spine. Builds cue sheets and audio anchors.",
};

const FILMMAKER_ALIASES = {
  "marty": "scorsese",
  "stanley": "kubrick",
  "akira": "kurosawa",
  "hitch": "hitchcock",
  "alfred": "hitchcock",
  "steven": "spielberg",
  "david": "lynch",
  "charlie": "kaufman",
  "shonda": "rhimes",
  "roger": "deakins",
  "thelma": "schoonmaker",
  "dante": "ferretti",
  "hans": "zimmer",
};

function resolveFilmmaker(input) {
  if (!input) {
    throw new Error("Persona name is required.");
  }
  const normalized = input.toLowerCase().trim();
  const slug = FILMMAKER_ALIASES[normalized] || normalized;
  if (!PERSONAS[slug]) {
    const valid = Object.keys(FILMMAKER_BLURBS).join(", ");
    throw new Error(
      `Unknown persona "${input}". Valid: ${valid} (short forms: marty, stanley, hitch, shonda).`
    );
  }
  return { slug, body: PERSONAS[slug] };
}

const server = new Server(
  { name: "great-filmmakers", version: "1.10.0" },
  { capabilities: { tools: {} } }
);

// ---------- Tool listing ----------

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "list_filmmakers",
      description:
        "List the twelve filmmaker personas with one-line descriptions.",
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: "filmmakers_channel",
      description:
        "Load a named filmmaker persona into the conversation for direct collaboration on scene breakdown, shot design, or craft conversation. Substantive output saves to film/<artifact-type>/<slug>.md by save trigger. Valid: scorsese, kubrick, kurosawa, hitchcock, spielberg, lynch, kaufman, rhimes, deakins, schoonmaker, ferretti, zimmer (short forms accepted).",
      inputSchema: {
        type: "object",
        properties: {
          persona: {
            type: "string",
            description: "Persona slug or short form.",
          },
        },
        required: ["persona"],
      },
    },
    {
      name: "filmmakers_crew",
      description:
        "Turn a source file (blog post, manuscript chapter, scene notes) into a complete film treatment. Auto-selects backend from source classification or accepts --backend heygen|veo3|remotion. HeyGen = single-avatar; Veo 3 = multi-character with CAST+VISUAL GRAMMAR+SHOT LIST; Remotion = slideshow.",
      inputSchema: {
        type: "object",
        properties: {
          source_file: {
            type: "string",
            description: "Path to the source prose. Required.",
          },
          backend: {
            type: "string",
            enum: ["heygen", "veo3", "remotion"],
            description: "Optional backend override. If omitted, auto-selects from source classification.",
          },
          director: {
            type: "string",
            description: "Optional director override (scorsese, kubrick, kurosawa, hitchcock, spielberg, lynch).",
          },
          writer: {
            type: "string",
            description: "Optional writer override (kaufman default, rhimes alternative).",
          },
        },
        required: ["source_file"],
      },
    },
    {
      name: "filmmakers_project_init",
      description:
        "Scaffold the film/ output directory at the project root (sibling to manuscript/) plus the scripts/ render-script templates (render_keyframes.py, render_kling.py, render_veo.py, wire_book_illustrations.py). Adds a ## Film section to .great-authors/project.md.",
      inputSchema: {
        type: "object",
        properties: {
          target_dir: {
            type: "string",
            description: "Optional target directory. If omitted, the prompt asks the user.",
          },
          slug: {
            type: "string",
            description: "Optional starting scene slug. Defaults to project slug.",
          },
        },
      },
    },
    {
      name: "filmmakers_build_keyframes",
      description:
        "Dispatch a director persona to read source prose + the project bible, identify illustration cue points, and produce a structured PROMPTS.md artifact. Default director Hitchcock for genre fiction; override available.",
      inputSchema: {
        type: "object",
        properties: {
          source_file: {
            type: "string",
            description: "Path to the source prose. Required.",
          },
          director: {
            type: "string",
            description: "Optional director override. Default hitchcock; valid: hitchcock, scorsese, kubrick, kurosawa, spielberg, lynch, deakins.",
          },
          count: {
            type: "number",
            description: "Optional target number of cue points. Default is the director's judgment based on source length.",
          },
          include_prose_anchors: {
            type: "boolean",
            description: "Include the prose snippet preceding each cue point (for downstream wiring scripts). Default false.",
          },
          out_dir: {
            type: "string",
            description: "Output directory. Default: film/render/book-illustrations/",
          },
          style_preset: {
            type: "string",
            description: "Optional style preset slug from docs/style-presets.md.",
          },
        },
        required: ["source_file"],
      },
    },
    {
      name: "filmmakers_critique",
      description:
        "Fast 3-bullet critique from N filmmaker personas in parallel on a scene or shot list. Cheaper and faster than filmmakers_edit.",
      inputSchema: {
        type: "object",
        properties: {
          content: {
            type: "string",
            description: "The scene or shot list to critique.",
          },
          personas: {
            type: "array",
            items: { type: "string" },
            description: "Array of filmmaker slugs. Defaults to 3 if empty (auto-selected by content).",
          },
        },
        required: ["content"],
      },
    },
    {
      name: "filmmakers_debate",
      description:
        "2-round craft debate between two filmmaker personas. Round 1 = each states position; Round 2 = each responds; consolidation names the real tension and picks winner or third way.",
      inputSchema: {
        type: "object",
        properties: {
          topic: {
            type: "string",
            description: "The shot, scene, or production decision to debate.",
          },
          persona_a: {
            type: "string",
            description: "First filmmaker slug.",
          },
          persona_b: {
            type: "string",
            description: "Second filmmaker slug.",
          },
        },
        required: ["topic", "persona_a", "persona_b"],
      },
    },
    {
      name: "filmmakers_edit",
      description:
        "Run 1-2 filmmaker personas as editors on a scene, shot list, or production doc. Produces a consolidated marked-up view.",
      inputSchema: {
        type: "object",
        properties: {
          content: {
            type: "string",
            description: "The draft to edit.",
          },
          personas: {
            type: "array",
            items: { type: "string" },
            description: "Array of 1 or 2 filmmaker slugs. If empty, auto-selects based on content register.",
          },
        },
        required: ["content"],
      },
    },
  ],
}));

// ---------- Tool calls ----------

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;

  if (name === "list_filmmakers") {
    const lines = Object.entries(FILMMAKER_BLURBS).map(
      ([k, v]) => `- **${k}** — ${v}`
    );
    const text = `# Great Filmmakers Roster\n\n## Twelve personas\n\n${lines.join("\n")}\n\nDispatch via \`filmmakers_channel\` (Claude Desktop) or \`/filmmakers-channel <name>\` (Claude Code). Short forms accepted: marty, stanley, hitch, shonda.`;
    return { content: [{ type: "text", text }] };
  }

  if (name === "filmmakers_channel") {
    const { slug, body } = resolveFilmmaker(args.persona);
    const text = `You are now channeling the following filmmaker persona. Read the persona body carefully, then adopt this voice for the rest of the conversation. The user will collaborate with you on scene breakdown, shot design, production-doc work, or craft conversation.\n\n---PERSONA: ${slug}---\n${body}\n---END PERSONA---\n\nIf the user says "drop the persona," "exit persona," or "back to Claude," return to normal voice.\n\nIf the user says "save as screenplay," "save as shot list," "save as score notes," "save as storyboard," or "save as edit notes," save the most recent substantive prose block to the appropriate film/ subdirectory (film/screenplay/<slug>.md, film/shot-lists/<slug>.md, etc.).\n\nIf .great-authors/ exists in the working directory, read project.md, voice.md, and any relevant scenes/ before producing substantive work.\n\nBegin as ${slug} now.`;
    return { content: [{ type: "text", text }] };
  }

  if (name === "filmmakers_crew") {
    const source = args.source_file;
    const backend = args.backend || "(auto-select from source classification)";
    const director = args.director || "(default by backend: scorsese for narrative, spielberg for educational)";
    const writer = args.writer || "(default kaufman; rhimes if backend=heygen and avatar=sara)";
    const text = `You are running the /filmmakers-crew pipeline. Source file: ${source}. Backend: ${backend}. Director: ${director}. Writer: ${writer}.\n\nThe pipeline is backend-aware. For each backend, run the right multi-stage dispatch:\n\n## HeyGen backend (single-avatar talking-head)\n\nStage 1 (sequential): Kaufman (or Rhimes) adapts the source into a HeyGen script. Output: film/screenplay/<slug>.heygen.md.\n\nStage 2 (parallel): Director + Schoonmaker produce edit notes. Output: film/edit-notes/<slug>.md.\n\n## Veo 3 backend (multi-character cinematic)\n\nStage 1 (parallel): Ferretti (CAST + LOCATIONS + NEGATIVE PROMPT), Deakins (VISUAL GRAMMAR), Director (initial SHOT LIST sketch).\n\nStage 2 (sequential): Kaufman/Rhimes integrates all three into the final production doc. Output: film/screenplay/<slug>.veo3.md.\n\nStage 3 (parallel): Schoonmaker (durations quantized to {4, 6, 8} for Veo 3.0 Fast) and Zimmer (audio cues embedded in shot prompts).\n\n## Remotion backend (slideshow + narration)\n\nStage 1 (parallel): Director + writer produce narration paragraphs; Zimmer produces musicPromptFor() tags.\n\nStage 2 (sequential): Schoonmaker sets per-segment timing.\n\nWrite output to film/screenplay/<slug>.<backend>.md and end with the machine-readable footer.\n\nRefer to docs/output-formats.md for the canonical format spec, slug conventions, image-gen backend choices (Path E gpt-image-1, F gpt-image-2, G Imagen 4 Ultra, H Leonardo Phoenix), and Veo 3 production constraints.\n\nIf .great-authors/ does not exist, warn the user and recommend running /authors-project-init from great-authors-plugin first.\n\nBegin.`;
    return { content: [{ type: "text", text }] };
  }

  if (name === "filmmakers_project_init") {
    const target = args.target_dir || "<user's current working directory>";
    const slug = args.slug || "<project slug>";
    const text = `You are scaffolding the film/ directory and the scripts/ render-script templates for a project at ${target}.\n\n1. Verify .great-authors/ exists at the target. If not, warn the user (the scaffold proceeds but personas won't have bible context).\n2. Create film/ with subdirs: screenplay/, shot-lists/, score-notes/, storyboards/, edit-notes/.\n3. Copy templates/scripts/*.py from this plugin's templates/scripts/ into <target>/scripts/. Files: render_keyframes.py (gpt-image-1 → PNGs), render_kling.py (Kling i2v → MP4), render_veo.py (Veo 3.0 Fast → MP4), wire_book_illustrations.py (PROMPTS.md → MDX wiring).\n4. Do NOT overwrite existing scripts in scripts/. Report which were skipped.\n5. chmod +x each new script.\n6. Update .great-authors/project.md with a ## Film section (path, current-scene slug ${slug}).\n7. Report what was created and suggest next steps:\n   - /filmmakers-channel <persona> for direct collaboration\n   - /filmmakers-crew <source-file> [--backend heygen|veo3|remotion] for the full pipeline\n   - /filmmakers-build-keyframes <source-file> for illustration prompts\n\nBegin.`;
    return { content: [{ type: "text", text }] };
  }

  if (name === "filmmakers_build_keyframes") {
    const source = args.source_file;
    const director = args.director || "hitchcock";
    const count = args.count ? args.count : "(director's judgment based on source length)";
    const include = args.include_prose_anchors ? "yes" : "no";
    const outDir = args.out_dir || "film/render/book-illustrations/";
    const style = args.style_preset || "(from .great-authors/project.md ## Visual section, or default by genre)";
    const { slug, body } = resolveFilmmaker(director);
    const text = `You are dispatching ${slug} to identify illustration cue points in ${source} and produce a structured PROMPTS.md.\n\nSource: ${source}\nDirector: ${slug}\nTarget cue count: ${count}\nInclude prose anchors: ${include}\nOutput dir: ${outDir}\nStyle preset: ${style}\n\nDirector's persona to apply:\n\n---PERSONA: ${slug}---\n${body}\n---END PERSONA---\n\nThe director should:\n\n1. Read the source file and the project bible (.great-authors/project.md, voice.md, visual-lints.md if it exists).\n2. Identify cue points — moments where an image carries something the prose alone doesn't.\n3. Pull the verbatim style anchor from .great-authors/project.md's ## Visual section (or the named style preset).\n4. Read .great-authors/visual-lints.md if it exists and use its forbidden-elements list as the baseline negative-prompt for every cue.\n5. Write structured prompt blocks per the canonical PROMPTS.md format (style anchor + composition + subject + light + production design + negative prompt, plus prose anchor when --include-prose-anchors).\n6. Use the slug convention <prefix>-<scene-slug> (e.g., ch01-hands-folding for chapter 1 illustrations, kf-truck-departing for video keyframes).\n7. Save to ${outDir}PROMPTS.md.\n\nRefer to docs/output-formats.md "Image-generation prompt format (v1.7+)" for the canonical structure and the four image-gen backend paths.\n\nBegin.`;
    return { content: [{ type: "text", text }] };
  }

  if (name === "filmmakers_critique") {
    const personas = Array.isArray(args.personas) && args.personas.length > 0
      ? args.personas.map((p) => resolveFilmmaker(p).slug)
      : ["scorsese", "deakins", "schoonmaker"];
    const personaBlocks = personas
      .map((s) => `### ${s}\n\n${PERSONAS[s]}`)
      .join("\n\n");
    const text = `You are conducting a fast 3-bullet critique from multiple filmmaker personas. Personas: ${personas.join(", ")}.\n\n---CONTENT---\n${args.content}\n---END CONTENT---\n\n---PERSONAS---\n\n${personaBlocks}\n---END PERSONAS---\n\nFor EACH persona, produce EXACTLY 3 bullets. Each bullet is one craft observation. No introduction. No markup. No rewrites. Just the three most important things that filmmaker notices.\n\nThen consolidate in one block:\n- Consensus: one sentence naming what most/all filmmakers flagged\n- Sharpest disagreement: one sentence, or "no significant disagreement"\n\nKeep it TERSE. The whole output should fit on one screen.`;
    return { content: [{ type: "text", text }] };
  }

  if (name === "filmmakers_debate") {
    const a = resolveFilmmaker(args.persona_a);
    const b = resolveFilmmaker(args.persona_b);
    if (a.slug === b.slug) {
      throw new Error(`Debate requires two different filmmakers. Got ${a.slug} twice.`);
    }
    const text = `You are running a 2-round craft debate between two filmmaker personas.\n\n**Topic:** ${args.topic}\n\n---PERSONA A: ${a.slug}---\n${a.body}\n---END PERSONA A---\n\n---PERSONA B: ${b.slug}---\n${b.body}\n---END PERSONA B---\n\n## Round 1 (parallel)\n\nEach filmmaker states their position in 3-5 sentences. What would you do? Why? What would be wrong with treating it another way? Be specific about craft reasoning.\n\n## Round 2 (parallel)\n\nEach filmmaker reads the other's Round 1 and replies in 3-5 sentences:\n- What do you concede?\n- Where do you hold your position?\n- If you'd revise your Round 1, how?\n\n## Consolidation\n\nNarrate (out of voice):\n- **The real tension:** one or two sentences naming what this dispute is actually about — usually a register, genre, or backend question.\n- **Verdict:** Winner / Third way / Genre call (which choice depends on what)\n\nProduce all three sections now. Label them clearly.`;
    return { content: [{ type: "text", text }] };
  }

  if (name === "filmmakers_edit") {
    const personas = Array.isArray(args.personas) && args.personas.length > 0
      ? args.personas.map((p) => resolveFilmmaker(p).slug)
      : null;
    const personaBlocks = personas
      ? personas.map((s) => `### ${s}\n\n${PERSONAS[s]}`).join("\n\n")
      : "(No personas specified — auto-select 1-2 based on content register.)";
    const text = `You are conducting a multi-filmmaker editorial pass on a scene, shot list, or production doc.${personas ? ` Filmmakers selected: ${personas.join(", ")}.` : " Auto-select 1-2 filmmakers based on register."}\n\n---DRAFT---\n${args.content}\n---END DRAFT---\n\n${personas ? `---PERSONAS---\n\n${personaBlocks}\n---END PERSONAS---\n\n` : ""}For each selected filmmaker, produce:\n- **Verdict** (one sentence top-line reaction)\n- **Marked passages** (3-8 quoted excerpts with ~~strikethroughs~~ for cuts and [→ replacements] for substitutions)\n- **Hand off** (if a different filmmaker would serve better)\n\nThen consolidate:\n- Verdicts from each filmmaker\n- Where they agree (1-3 points)\n- Where they disagree (1-2 points)\n- Highest-leverage change (pick ONE)\n\nIf .great-authors/ exists, each filmmaker reads the bible before editing per their before-decision protocol.\n\nBegin.`;
    return { content: [{ type: "text", text }] };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// ---------- Boot ----------

const transport = new StdioServerTransport();
await server.connect(transport);
