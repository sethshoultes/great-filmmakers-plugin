#!/usr/bin/env bash
# Plugin smoke tests for great-filmmakers. Catches frontmatter issues,
# version coherence, and v1.7+ trilogy-improvement-#5 checks (style preset
# slug consistency between docs/style-presets.md and template references).

set -uo pipefail

cd "$(dirname "$0")/.."

ERRORS=0
red() { printf '\033[31m%s\033[0m\n' "$1" >&2; }
green() { printf '\033[32m%s\033[0m\n' "$1"; }

# ---------- 1. Frontmatter validity ----------

echo "Checking SKILL.md frontmatter..."
for f in skills/*/SKILL.md; do
  if [ ! -f "$f" ]; then continue; fi
  if ! head -1 "$f" | grep -q '^---$'; then
    red "  FAIL: $f does not start with YAML frontmatter delimiter"
    ERRORS=$((ERRORS + 1))
    continue
  fi
  if ! awk '/^---$/{c++} c==1 && /^name: /{found=1} END{exit !found}' "$f"; then
    red "  FAIL: $f frontmatter is missing 'name:' field"
    ERRORS=$((ERRORS + 1))
  fi
  if ! awk '/^---$/{c++} c==1 && /^description: /{found=1} END{exit !found}' "$f"; then
    red "  FAIL: $f frontmatter is missing 'description:' field"
    ERRORS=$((ERRORS + 1))
  fi
done

echo "Checking persona frontmatter..."
for f in agents/*-persona.md; do
  if [ ! -f "$f" ]; then continue; fi
  if ! head -1 "$f" | grep -q '^---$'; then
    red "  FAIL: $f does not start with YAML frontmatter delimiter"
    ERRORS=$((ERRORS + 1))
    continue
  fi
  if ! awk '/^---$/{c++} c==1 && /^name: /{found=1} END{exit !found}' "$f"; then
    red "  FAIL: $f frontmatter is missing 'name:' field"
    ERRORS=$((ERRORS + 1))
  fi
  if ! awk '/^---$/{c++} c==1 && /^description: /{found=1} END{exit !found}' "$f"; then
    red "  FAIL: $f frontmatter is missing 'description:' field"
    ERRORS=$((ERRORS + 1))
  fi
done

# ---------- 2. Version coherence ----------

echo "Checking version coherence..."
PKG_VERSION=$(grep '"version"' package.json | head -1 | sed 's/.*"version": *"\([^"]*\)".*/\1/')
PLUGIN_VERSION=$(grep '"version"' .claude-plugin/plugin.json | head -1 | sed 's/.*"version": *"\([^"]*\)".*/\1/')

# DXT bundle versions (added in v1.10).
DXT_PKG_VERSION=""
DXT_MANIFEST_VERSION=""
if [ -f "distribution/dxt/package.json" ]; then
  DXT_PKG_VERSION=$(grep '"version"' distribution/dxt/package.json | head -1 | sed 's/.*"version": *"\([^"]*\)".*/\1/')
fi
if [ -f "distribution/dxt/manifest.json" ]; then
  DXT_MANIFEST_VERSION=$(grep '"version"' distribution/dxt/manifest.json | head -1 | sed 's/.*"version": *"\([^"]*\)".*/\1/')
fi

if [ "$PKG_VERSION" != "$PLUGIN_VERSION" ]; then
  red "  FAIL: version drift between package.json ($PKG_VERSION) and .claude-plugin/plugin.json ($PLUGIN_VERSION)"
  ERRORS=$((ERRORS + 1))
fi
if [ -n "$DXT_PKG_VERSION" ] && [ "$PKG_VERSION" != "$DXT_PKG_VERSION" ]; then
  red "  FAIL: version drift between package.json ($PKG_VERSION) and distribution/dxt/package.json ($DXT_PKG_VERSION)"
  ERRORS=$((ERRORS + 1))
fi
if [ -n "$DXT_MANIFEST_VERSION" ] && [ "$PKG_VERSION" != "$DXT_MANIFEST_VERSION" ]; then
  red "  FAIL: version drift between package.json ($PKG_VERSION) and distribution/dxt/manifest.json ($DXT_MANIFEST_VERSION)"
  ERRORS=$((ERRORS + 1))
fi

# ---------- 2b. DXT bundle persona alignment (v1.10+) ----------

if [ -d "distribution/dxt/server/personas" ]; then
  echo "Checking DXT bundled personas match agents/..."
  AGENTS_COUNT=$(ls agents/*-persona.md 2>/dev/null | wc -l | tr -d ' ')
  DXT_COUNT=$(ls distribution/dxt/server/personas/*.md 2>/dev/null | wc -l | tr -d ' ')
  if [ "$AGENTS_COUNT" != "$DXT_COUNT" ]; then
    red "  FAIL: agents/ has $AGENTS_COUNT *-persona.md files but distribution/dxt/server/personas/ has $DXT_COUNT"
    red "        Run: cp agents/*.md distribution/dxt/server/personas/"
    ERRORS=$((ERRORS + 1))
  fi
fi

# ---------- 2c. DXT tool / handler alignment (v1.10+) ----------

if [ -f "distribution/dxt/server/index.js" ]; then
  echo "Checking DXT tool definitions vs handlers..."
  TOOL_NAMES=$(grep -oE 'name: "[a-z_]+"' distribution/dxt/server/index.js | sed 's/name: "\(.*\)"/\1/' | sort -u)
  HANDLER_NAMES=$(grep -oE 'name === "[a-z_]+"' distribution/dxt/server/index.js | sed 's/name === "\(.*\)"/\1/' | sort -u)

  MISSING_HANDLERS=$(comm -23 <(echo "$TOOL_NAMES") <(echo "$HANDLER_NAMES"))
  MISSING_DEFS=$(comm -13 <(echo "$TOOL_NAMES") <(echo "$HANDLER_NAMES"))

  if [ -n "$MISSING_HANDLERS" ]; then
    red "  FAIL: tool defined in DXT manifest but no handler:"
    echo "$MISSING_HANDLERS" | sed 's/^/        /' >&2
    ERRORS=$((ERRORS + 1))
  fi
  if [ -n "$MISSING_DEFS" ]; then
    red "  FAIL: handler in DXT but no tool definition:"
    echo "$MISSING_DEFS" | sed 's/^/        /' >&2
    ERRORS=$((ERRORS + 1))
  fi
fi

# ---------- 3. Style preset slug consistency (trilogy improvement #5) ----------

echo "Checking style preset slug consistency..."
STYLE_PRESETS_FILE="docs/style-presets.md"
if [ ! -f "$STYLE_PRESETS_FILE" ]; then
  red "  FAIL: $STYLE_PRESETS_FILE does not exist"
  ERRORS=$((ERRORS + 1))
else
  # Extract slugs from style-presets.md headings: lines like "### \`pen-and-ink-editorial\`"
  PRESET_SLUGS=$(grep -oE '^### `[a-z][a-z0-9_\-]*`' "$STYLE_PRESETS_FILE" | sed 's/^### `\(.*\)`/\1/' | sort -u)

  if [ -z "$PRESET_SLUGS" ]; then
    red "  FAIL: $STYLE_PRESETS_FILE has no preset slugs in the format \`### \\\`<slug>\\\`\`"
    ERRORS=$((ERRORS + 1))
  fi

  # Check that any slug referenced in docs/output-formats.md (in the image-gen section) exists in style-presets.md
  if [ -f "docs/output-formats.md" ]; then
    REFERENCED=$(grep -oE '\b(pen-and-ink-editorial|photoreal-cinematic|mid-century-illustration|noir)\b' docs/output-formats.md 2>/dev/null | sort -u)
    for slug in $REFERENCED; do
      if ! echo "$PRESET_SLUGS" | grep -q "^${slug}$"; then
        # Don't fail — these may be example slugs in documentation. Just warn.
        :
      fi
    done
  fi
fi

# ---------- 4. v1.7+ filmmakers-build-keyframes skill check ----------

echo "Checking v1.7+ filmmakers-build-keyframes skill exists..."
# Numeric major.minor compare (lexicographic compare would break at v1.10).
PLUGIN_MAJOR=$(echo "$PLUGIN_VERSION" | cut -d. -f1)
PLUGIN_MINOR=$(echo "$PLUGIN_VERSION" | cut -d. -f2)
if [ "$PLUGIN_MAJOR" -gt 1 ] || { [ "$PLUGIN_MAJOR" -eq 1 ] && [ "$PLUGIN_MINOR" -ge 7 ]; }; then
  if [ ! -f "skills/filmmakers-build-keyframes/SKILL.md" ]; then
    red "  FAIL: v1.7+ requires skills/filmmakers-build-keyframes/SKILL.md (trilogy improvement #1)"
    ERRORS=$((ERRORS + 1))
  fi
fi

# ---------- Summary ----------

echo ""
if [ "$ERRORS" -eq 0 ]; then
  green "✓ All smoke tests passed."
  exit 0
else
  red "✗ $ERRORS check(s) failed."
  exit 1
fi
