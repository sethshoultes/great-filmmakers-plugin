#!/usr/bin/env python3
"""Wire rendered book illustrations into Astro chapter MDX files.

Reads a `PROMPTS.md` file (the artifact `/filmmakers-build-keyframes` produces
with `--include-prose-anchors`), extracts per-illustration metadata (filename,
prose anchor, alt-text subject from the ToC), copies rendered PNGs into the
book site's `public/illustrations/` directory, and inserts `<Illustration>`
components into each chapter MDX at the matched prose-anchor paragraph.

Idempotent: re-running on an already-wired MDX detects existing `<Illustration>`
entries by filename and skips inserting them again.

Authentication
--------------
None required — the script only reads/writes local filesystem.

Anchor matching
---------------
Prose anchors are matched against MDX paragraphs in three passes:

1. Substring match — anchor's first 60 chars (lowercase, punctuation stripped)
   appears verbatim somewhere in the paragraph. Fast path.
2. Substring match — anchor's first 30 chars. Fallback for paraphrased anchors.
3. Fuzzy match (v1.8+) — `difflib.SequenceMatcher.ratio()` against each line;
   if any line scores above `--fuzzy-threshold` (default 0.7), the line wins.
   Stdlib-only; no RapidFuzz dependency.

This handles cases where the director's prose anchor was paraphrased slightly
from the source — common when the anchor was hand-written rather than copy-
pasted from the manuscript.

Usage
-----
    python3 scripts/wire_book_illustrations.py
    python3 scripts/wire_book_illustrations.py --chapter 5
    python3 scripts/wire_book_illustrations.py --dry-run
    python3 scripts/wire_book_illustrations.py --fuzzy-threshold 0.6
    python3 scripts/wire_book_illustrations.py \\
        --prompts-file film/render/book-illustrations/PROMPTS.md \\
        --rendered-dir film/render/book-illustrations \\
        --book-root ../my-book-site \\
        --chapter-slugs chapter-slugs.json
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import sys
from pathlib import Path

# Default paths assume the script runs from a project root with the standard
# constellation directory layout. Override via argv for projects that diverge.
DEFAULT_PROMPTS_FILE = "film/render/book-illustrations/PROMPTS.md"
DEFAULT_RENDERED_DIR = "film/render/book-illustrations"
DEFAULT_KEYFRAMES_DIR = "film/render/kling/keyframes"
DEFAULT_BOOK_PUBLIC = "public/illustrations"
DEFAULT_BOOK_CHAPTERS = "src/content/chapters"
DEFAULT_FUZZY_THRESHOLD = 0.7

# Canonical slug regex from docs/output-formats.md (v1.8+).
SLUG_RE = re.compile(r"^### ([a-z][a-z0-9_\-]*)\.png\s*\n", re.MULTILINE)


def parse_toc(text: str) -> dict[str, str]:
    """Map filename (without extension) -> subject from a TOC table.

    The TOC, when present, looks like:

        | Ch 02 | ch02-compound-gate.png | Compound gate at dawn |

    The skill `/filmmakers-build-keyframes` may produce this table. If absent,
    subjects fall back to the slug with hyphens replaced by spaces.
    """
    subjects: dict[str, str] = {}
    pattern = re.compile(
        r"^\|\s*(?:Ch\s*)?\d+\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|\s*$",
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        fname = m.group(1).strip()
        subj = m.group(2).strip()
        if fname in ("—", "-", ""):
            continue
        if fname.endswith(".png"):
            subjects[fname[:-4]] = subj
    return subjects


def parse_blocks(text: str) -> list[dict]:
    """Parse per-illustration blocks from PROMPTS.md.

    Returns a list of dicts with keys: filename, chapter (int or None),
    prose_anchor (str or None), is_reuse (bool), reuse_target (str or None),
    is_optional (bool).

    The slug regex follows docs/output-formats.md v1.8+:
    `### ([a-z][a-z0-9_\\-]*)\\.png`. Chapter prefixes (`ch01-`, `ch02-`, ...)
    are detected; non-chapter slugs (`kf-*`, `cover-*`, custom prefixes) are
    treated as chapter-agnostic.
    """
    blocks: list[dict] = []

    # Standard render block: `### <slug>.png`
    standard_re = re.compile(
        r"^### ([a-z][a-z0-9_\-]*)\.png\s*\n(.*?)(?=^---\s*$|^### |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    # Reuse block: `### chNN — REUSE: <kf-target>.png`
    reuse_re = re.compile(
        r"^### ch(\d{2}) — REUSE: ([a-z][a-z0-9_\-]*)\.png\s*\n(.*?)(?=^---\s*$|^### |\Z)",
        re.DOTALL | re.MULTILINE,
    )
    chapter_prefix_re = re.compile(r"^ch(\d+)-")

    for m in standard_re.finditer(text):
        filename = m.group(1)
        body = m.group(2)
        chapter_match = chapter_prefix_re.match(filename)
        chapter = int(chapter_match.group(1)) if chapter_match else None
        anchor_match = re.search(
            r"\*\*Prose anchor:\*\*\s*[\"\*]?([^\"\*\n]+)[\"\*]?",
            body,
        )
        anchor = anchor_match.group(1).strip() if anchor_match else None
        if anchor is None:
            print(f"WARN: no prose anchor for {filename}", file=sys.stderr)
        blocks.append({
            "filename": filename,
            "chapter": chapter,
            "prose_anchor": anchor,
            "is_reuse": False,
            "reuse_target": None,
            "is_optional": False,
        })

    for m in reuse_re.finditer(text):
        chapter = int(m.group(1))
        target = m.group(2)
        body = m.group(3)
        anchor_match = re.search(
            r"\*\*Prose anchor:\*\*\s*[\"\*]?([^\"\*\n]+)[\"\*]?",
            body,
        )
        anchor = anchor_match.group(1).strip() if anchor_match else None
        if anchor is None:
            print(f"WARN: no prose anchor for ch{chapter:02d} REUSE {target}", file=sys.stderr)
        body_lower = body.lower()
        is_optional = "optional" in body_lower or "discretion" in body_lower
        blocks.append({
            "filename": target,
            "chapter": chapter,
            "prose_anchor": anchor,
            "is_reuse": True,
            "reuse_target": target,
            "is_optional": is_optional,
        })

    return blocks


def normalize_anchor(anchor: str, length: int = 60) -> str:
    """Strip punctuation, lowercase, truncate to length chars."""
    return anchor[:length].strip().rstrip(".,:;!?\"'").lower()


def find_paragraph_index(
    content_lines: list[str], anchor: str, fuzzy_threshold: float = DEFAULT_FUZZY_THRESHOLD,
) -> tuple[int | None, str]:
    """Return (line_index, match_method) for the line that starts the paragraph
    containing the anchor text. Returns (None, 'unmatched') if not found.

    Match passes (in order):
      1. substring-60: first 60 chars of the anchor appears verbatim
      2. substring-30: first 30 chars of the anchor appears verbatim
      3. fuzzy: difflib.SequenceMatcher.ratio() against each line; best match
         wins if it scores above fuzzy_threshold

    Match method is returned alongside the index for debugging.
    """
    needle_60 = normalize_anchor(anchor, 60)
    for i, line in enumerate(content_lines):
        if needle_60 in line.lower():
            return i, "substring-60"

    needle_30 = normalize_anchor(anchor, 30)
    if needle_30:
        for i, line in enumerate(content_lines):
            if needle_30 in line.lower():
                return i, "substring-30"

    # Fuzzy fallback (v1.8+) — handles paraphrased anchors that diverged from
    # the source manuscript text by a few words.
    needle_fuzzy = normalize_anchor(anchor, 80)
    if needle_fuzzy and len(needle_fuzzy) >= 20:
        best_idx: int | None = None
        best_ratio = 0.0
        for i, line in enumerate(content_lines):
            line_normalized = line.strip().lower()
            if not line_normalized or len(line_normalized) < 20:
                continue
            # Compare anchor against the first ~150 chars of each candidate line
            candidate = line_normalized[:150]
            ratio = difflib.SequenceMatcher(None, needle_fuzzy, candidate).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_idx = i
        if best_idx is not None and best_ratio >= fuzzy_threshold:
            return best_idx, f"fuzzy-{best_ratio:.2f}"

    return None, "unmatched"


def build_illustration_tag(filename: str, subject: str, caption: str | None = None) -> str:
    """Render a self-closing Astro <Illustration> tag string."""
    alt = subject.replace('"', "'")
    cap_attr = f' caption="{caption}"' if caption else ""
    return (
        f'<Illustration src="/illustrations/{filename}.png" '
        f'alt="{alt}, illustration."{cap_attr} />'
    )


def ensure_imports(content: str) -> str:
    """Ensure the chapter MDX imports Illustration. Returns updated content."""
    if "import Illustration" in content:
        return content
    fm_end = content.find("---", content.find("---") + 3)
    if fm_end < 0:
        # No frontmatter; add imports at the top.
        return (
            "import Illustration from '../../components/Illustration.astro';\n"
            "\n" + content
        )
    fm_end_eol = content.find("\n", fm_end) + 1
    imports = "import Illustration from '../../components/Illustration.astro';\n\n"
    return content[:fm_end_eol] + imports + content[fm_end_eol:]


def discover_chapter_slugs(chapters_dir: Path) -> dict[int, str]:
    """Derive chapter number -> slug from MDX filenames in the book site.

    Expects filenames like `the-compound.mdx`, `the-rodeo-grounds.mdx`. The
    chapter number isn't embedded in the filename; we use the order of files
    sorted alphabetically as a proxy. For projects where filenames don't
    encode chapter order, pass --chapter-slugs <json> with an explicit map.
    """
    slugs: dict[int, str] = {}
    if not chapters_dir.exists():
        return slugs
    mdx_files = sorted(chapters_dir.glob("*.mdx"))
    for i, p in enumerate(mdx_files, start=1):
        slugs[i] = p.stem
    return slugs


def load_chapter_slugs(json_path: Path | None, fallback_chapters_dir: Path) -> dict[int, str]:
    """Load chapter -> slug mapping from JSON if provided, else discover."""
    if json_path and json_path.exists():
        data = json.loads(json_path.read_text())
        return {int(k): v for k, v in data.items()}
    return discover_chapter_slugs(fallback_chapters_dir)


def wire_chapter(
    chapter: int,
    blocks: list[dict],
    subjects: dict[str, str],
    chapter_slugs: dict[int, str],
    chapters_dir: Path,
    fuzzy_threshold: float,
    dry_run: bool,
) -> dict:
    if chapter not in chapter_slugs:
        return {"chapter": chapter, "status": "unknown-chapter"}
    slug = chapter_slugs[chapter]
    mdx_path = chapters_dir / f"{slug}.mdx"
    if not mdx_path.exists():
        return {"chapter": chapter, "status": "missing-mdx", "path": str(mdx_path)}

    chapter_blocks = [b for b in blocks if b["chapter"] == chapter]
    if not chapter_blocks:
        return {"chapter": chapter, "status": "no-blocks"}

    content = mdx_path.read_text()
    content = ensure_imports(content)
    lines = content.split("\n")

    inserts: list[tuple[int, str, str]] = []
    skipped_existing = 0
    skipped_unmatched = 0
    match_methods: list[str] = []

    for b in chapter_blocks:
        filename = b["filename"]
        if b.get("is_optional"):
            continue
        if f'src="/illustrations/{filename}.png"' in content:
            skipped_existing += 1
            continue
        if not b.get("prose_anchor"):
            print(f"  ch{chapter:02d}: no anchor metadata for {filename}", file=sys.stderr)
            skipped_unmatched += 1
            continue
        subject = subjects.get(filename, filename.replace("-", " "))
        idx, method = find_paragraph_index(lines, b["prose_anchor"], fuzzy_threshold)
        if idx is None:
            print(
                f"  ch{chapter:02d}: anchor not found for {filename}: "
                f"{b['prose_anchor'][:60]}...",
                file=sys.stderr,
            )
            skipped_unmatched += 1
            continue
        match_methods.append(method)
        tag = build_illustration_tag(filename, subject)
        inserts.append((idx, filename, tag))

    inserts.sort(key=lambda x: x[0], reverse=True)
    for idx, _filename, tag in inserts:
        lines.insert(idx + 1, "")
        lines.insert(idx + 2, tag)
        lines.insert(idx + 3, "")

    new_content = "\n".join(lines)

    if not dry_run and inserts:
        mdx_path.write_text(new_content)

    return {
        "chapter": chapter,
        "status": "ok",
        "inserted": len(inserts),
        "skipped_existing": skipped_existing,
        "skipped_unmatched": skipped_unmatched,
        "total_blocks": len(chapter_blocks),
        "match_methods": match_methods,
    }


def copy_assets(
    blocks: list[dict],
    rendered_dir: Path,
    keyframes_dir: Path,
    public_dir: Path,
    dry_run: bool,
) -> dict:
    """Copy rendered PNGs and reused keyframes into the book site's public dir."""
    public_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    missing: list[str] = []
    for b in blocks:
        if b.get("is_optional"):
            continue
        filename = b["filename"]
        src = (keyframes_dir if b["is_reuse"] else rendered_dir) / f"{filename}.png"
        dst = public_dir / f"{filename}.png"
        if not src.exists():
            missing.append(filename)
            continue
        if dst.exists() and dst.stat().st_size == src.stat().st_size:
            continue
        if not dry_run:
            shutil.copy2(src, dst)
        copied += 1
    return {"copied": copied, "missing": missing}


def main() -> int:
    parser = argparse.ArgumentParser(description="Wire rendered illustrations into Astro chapter MDX files.")
    parser.add_argument(
        "--prompts-file",
        default=DEFAULT_PROMPTS_FILE,
        help=f"Path to PROMPTS.md (default: {DEFAULT_PROMPTS_FILE})",
    )
    parser.add_argument(
        "--rendered-dir",
        default=DEFAULT_RENDERED_DIR,
        help=f"Directory of rendered PNGs (default: {DEFAULT_RENDERED_DIR})",
    )
    parser.add_argument(
        "--keyframes-dir",
        default=DEFAULT_KEYFRAMES_DIR,
        help=f"Directory of keyframe PNGs for REUSE blocks (default: {DEFAULT_KEYFRAMES_DIR})",
    )
    parser.add_argument(
        "--book-root",
        required=True,
        help="Path to the Astro book site root (e.g., ../my-book-site)",
    )
    parser.add_argument(
        "--chapter-slugs",
        help="Optional JSON file mapping chapter number -> slug. If omitted, slugs are derived from <book-root>/src/content/chapters/*.mdx by sorted order.",
    )
    parser.add_argument(
        "--chapter",
        type=int,
        help="Process only this chapter number",
    )
    parser.add_argument(
        "--fuzzy-threshold",
        type=float,
        default=DEFAULT_FUZZY_THRESHOLD,
        help=f"Fuzzy match threshold for anchor lookup (default: {DEFAULT_FUZZY_THRESHOLD})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change, don't write",
    )
    args = parser.parse_args()

    prompts_path = Path(args.prompts_file).resolve()
    if not prompts_path.exists():
        print(f"error: PROMPTS.md not found at {prompts_path}", file=sys.stderr)
        return 1

    rendered_dir = Path(args.rendered_dir).resolve()
    keyframes_dir = Path(args.keyframes_dir).resolve()
    book_root = Path(args.book_root).resolve()
    if not book_root.exists():
        sys.stderr.write(
            f"error: --book-root {book_root} does not exist. "
            f"Create the Astro book site first, then re-run.\n"
        )
        return 1
    public_illustrations = book_root / DEFAULT_BOOK_PUBLIC
    chapters_dir = book_root / DEFAULT_BOOK_CHAPTERS
    if not chapters_dir.exists():
        sys.stderr.write(
            f"error: chapters directory not found at {chapters_dir}. "
            f"Expected the Astro book-site convention "
            f"<book-root>/src/content/chapters/. Override paths if your "
            f"site uses a different layout.\n"
        )
        return 1

    chapter_slugs_json = Path(args.chapter_slugs).resolve() if args.chapter_slugs else None
    chapter_slugs = load_chapter_slugs(chapter_slugs_json, chapters_dir)

    text = prompts_path.read_text()
    subjects = parse_toc(text)
    blocks = parse_blocks(text)
    chapters_present = sorted({b["chapter"] for b in blocks if b["chapter"] is not None})
    print(f"parsed {len(blocks)} illustration blocks across {len(chapters_present)} chapters")

    asset_report = copy_assets(blocks, rendered_dir, keyframes_dir, public_illustrations, dry_run=args.dry_run)
    print(f"assets: {asset_report['copied']} copied; {len(asset_report['missing'])} missing")
    if asset_report["missing"]:
        print(f"  missing source PNGs: {asset_report['missing']}")

    targets = [args.chapter] if args.chapter else chapters_present
    total_inserted = 0
    total_unmatched = 0
    for ch in targets:
        report = wire_chapter(
            ch,
            blocks,
            subjects,
            chapter_slugs,
            chapters_dir,
            args.fuzzy_threshold,
            dry_run=args.dry_run,
        )
        slug = chapter_slugs.get(ch, "?")
        print(f"  ch{ch:02d} {slug:25}  {report}")
        if report.get("status") == "ok":
            total_inserted += report.get("inserted", 0)
            total_unmatched += report.get("skipped_unmatched", 0)

    print()
    print(f"done. inserted={total_inserted} unmatched={total_unmatched}")
    if args.dry_run:
        print("(dry-run — no files were written)")
    return 0 if total_unmatched == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
