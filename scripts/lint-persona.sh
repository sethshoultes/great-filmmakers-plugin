#!/usr/bin/env bash
# lint-persona.sh <path-to-persona-file>
#
# Verifies a filmmaker persona file has the required structure defined in
# docs/superpowers/specs/2026-04-24-great-filmmakers-design.md Section 2.
#
# Exit codes: 0 = pass, 1 = fail

set -euo pipefail

file="${1:-}"
if [[ -z "$file" ]]; then
  echo "usage: $0 <persona-file>" >&2
  exit 1
fi

if [[ ! -f "$file" ]]; then
  echo "FAIL: file does not exist: $file" >&2
  exit 1
fi

errors=0

check_contains() {
  local pattern="$1"
  local label="$2"
  if ! grep -qE "$pattern" "$file"; then
    echo "FAIL: missing $label" >&2
    errors=$((errors + 1))
  fi
}

check_frontmatter_field() {
  local field="$1"
  if ! head -30 "$file" | grep -qE "^${field}: "; then
    echo "FAIL: missing frontmatter field: $field" >&2
    errors=$((errors + 1))
  fi
}

# Frontmatter must open on line 1
if ! head -1 "$file" | grep -qE '^---$'; then
  echo "FAIL: file does not start with YAML frontmatter" >&2
  errors=$((errors + 1))
fi

check_frontmatter_field "name"
check_frontmatter_field "description"
check_frontmatter_field "model"
check_frontmatter_field "color"

# Required body sections. "Voice and ..." matches visual/sonic/cutting grammar variants.
check_contains "^## Voice and " "Voice and <grammar> section"

# Role-specific primary utility — require ONE of these headings.
check_contains "^## How to (break down|structure|hook|shot-list|find the cut|score|build the world)" \
  "primary-utility section (one of: break down, structure, hook, shot-list, find the cut, score, build the world)"

check_contains "^## How to draft" "How to draft section"
check_contains "^## Before you work" "Before you work protocol"
check_contains "^## When another filmmaker would serve better" "cross-reference section"
check_contains "^## Things you never do" "Things you never do section"
check_contains "^## Staying in character" "Staying in character footer"

if [[ $errors -gt 0 ]]; then
  echo "FAIL: $errors validation error(s) in $file" >&2
  exit 1
fi

echo "PASS: $file"
