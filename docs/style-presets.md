# Great Filmmakers — Style Presets

Style presets are short paragraphs prepended verbatim to every Veo 3 shot prompt produced by `/filmmakers-crew --backend veo3`. They lock the visual register across an entire short and create the consistency that lets match-cuts and character continuity actually work.

Without a style preset, Veo defaults to a generic photorealistic register that varies subtly between shots — and on the Gemini API tier, it also content-gates photorealistic humans. With a strong stylized preset, humans render fine and the look is consistent.

## How presets are used

1. The writer (Kaufman or Rhimes) selects or accepts a preset before composing the production doc.
2. The preset's `prompt_anchor` paragraph is prepended verbatim to every shot prompt in the SHOT LIST — not paraphrased, not abbreviated.
3. The preset's slug is recorded in the machine-readable footer as `style_preset: <slug>` so downstream renderers know what they're getting.

## v1.1 preset library

### `pen-and-ink-editorial` (default)

Black-and-white pen-and-ink animation in the style of an animated New Yorker editorial illustration. Adult, draftsmanlike, never whimsical. Verified to bypass Veo's photorealistic-human content gate without `personGeneration`.

```
prompt_anchor: |
  Black-and-white pen-and-ink animation in the style of an animated New Yorker
  illustration. Crosshatch shading. High-contrast linework. Spare composition.
  Editorial, adult, draftsmanlike. Never whimsical. Limited grayscale palette.
  Subtle paper-grain texture. Static frame except where motion is named.
```

**Use when:** the source is essayistic, reflective, or otherwise wants an editorial register. Native ambient audio renders alongside (room tone, soft footsteps, no music) — design VO mixes accordingly.

### `noir` (placeholder — not yet verified)

High-contrast black-and-white live-action register. Hard shadows, smoke, venetian blinds.

```
prompt_anchor: |
  Black-and-white live-action cinematography in the style of 1940s American film
  noir. Hard chiaroscuro lighting. Long shadows. Wet pavement. Cigarette smoke
  visible in the key light. Limited dynamic range. Static frame except where
  camera movement is explicitly named.
```

**Status:** not yet verified against Veo's content gates with human subjects. Probe before relying on it for production.

### `photoreal-cinematic` (placeholder — content-gate risk)

Anamorphic photoreal cinematography. The default Veo register, expressed as a preset for explicitness.

```
prompt_anchor: |
  Photorealistic cinematography. Anamorphic lens. Natural lighting. Cinematic
  color grade. Shallow depth of field where motivated. Live-action register.
```

**Status:** humans get content-gated by Veo on this tier. Do not select for any short with human characters until Vertex AI access is available; safe for landscape, object, or animal-only shots.

### `studio-ghibli` (placeholder — not yet verified)

Hand-painted animation register in the Ghibli/Studio Ponoc tradition.

```
prompt_anchor: |
  Hand-painted 2D animation in the style of Studio Ghibli. Soft watercolor
  textures. Warm natural lighting. Frame-by-frame character animation. Gentle
  camera moves. Saturated but never garish. Tender atmosphere.
```

**Status:** not verified for the editorial use case the trilogy targets. Listed for future expansion.

## Adding a preset

1. Add a new section to this file with `prompt_anchor` (block scalar) and a short note on use case + content-gate status.
2. Render at least 3 shots with the preset and inspect the output before marking it "verified."
3. The slug must be lowercase-hyphen and stable; it ends up in the production doc footer.

## Why this matters

The pen-and-ink preset wasn't an aesthetic choice in isolation — it was the path that bypassed Veo's photorealistic-human content gate after `personGeneration: allow_all` was rejected. The lesson generalized: if you want human characters on the Gemini API tier, the style preset must commit to a stylized/animated register, not "photoreal but tasteful." The preset library encodes that decision so future shorts don't have to discover it from scratch.
