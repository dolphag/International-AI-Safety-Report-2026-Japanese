#!/usr/bin/env python3
"""
Parse the report's own Glossary section (source/11_glossary.txt) into
(English term, English definition) pairs, look up the Japanese
translation for each in glossary_translations.py, and write glossary.md.

Run after extract_chunks.py. Re-run whenever source/11_glossary.txt or
glossary_translations.py changes.
"""
import re
import sys
from pathlib import Path

from glossary_translations import TRANSLATIONS
from glossary_supplementary import SUPPLEMENTARY

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source" / "11_glossary.txt"
OUT = ROOT / "glossary.md"

SKIP_PATTERNS = [
    re.compile(r"^\[\[page \d+\]\]$"),
    re.compile(r"^\d{1,3}$"),
    re.compile(r"^International AI Safety Report 2026$"),
    re.compile(r"^Glossary$"),
]


def parse_entries(text: str):
    lines = text.splitlines()[3:]  # drop the 2-line header + blank
    clean = [ln for ln in lines if not any(p.match(ln.strip()) for p in SKIP_PATTERNS)]
    joined = re.sub(r"\s+", " ", " ".join(l.strip() for l in clean if l.strip()))
    joined = re.sub(r"\s+([.,;:])", r"\1", joined)

    raw_entries = re.split(r"(?<=[.\)])\s+(?=[A-Z(][^:]{2,70}:\s)", joined)
    entries = []
    for e in raw_entries:
        e = e.strip()
        m = re.match(r"^([^:]{2,70}):\s(.*)$", e)
        if m and m.group(1).strip() != "(AI)":
            entries.append([m.group(1).strip(), m.group(2).strip()])
        elif entries:
            entries[-1][1] = entries[-1][1].rstrip() + " " + e

    # Re-attach "(AI) " prefixes that got split off as their own fragment
    # (glyph before "System"/"Model" etc. is a parenthesis, which the
    # split regex's sentence-end lookbehind also matches).
    changed = True
    while changed:
        changed = False
        fixed = []
        i = 0
        while i < len(entries):
            t, d = entries[i]
            if d.rstrip().endswith("(AI)") and i + 1 < len(entries):
                d2 = re.sub(r"\s*\(AI\)\s*$", "", d)
                nt, nd = entries[i + 1]
                fixed.append([t, d2])
                fixed.append([nt if nt.startswith("(AI)") else f"(AI) {nt}", nd])
                i += 2
                changed = True
            else:
                fixed.append([t, d])
                i += 1
        entries = fixed

    # One-off: an internal colon inside the "(AI) Model" definition
    # ("Most AI models today are based on machine learning: ...") gets
    # mis-split into its own pseudo-entry. Fold it back in.
    for i, (t, _) in enumerate(entries):
        if t.startswith("Most AI models"):
            bad_t, bad_d = entries.pop(i)
            entries[i - 1][1] += f" {bad_t}: {bad_d}"
            break

    return entries


def main():
    text = SRC.read_text(encoding="utf-8")
    entries = parse_entries(text)

    missing = [t for t, _ in entries if t not in TRANSLATIONS]
    if missing:
        print("ERROR: missing translations for:", missing, file=sys.stderr)
        return 1

    lines = [
        "# 用語集 (Glossary)\n\n",
        "International AI Safety Report 2026 の翻訳で使用する統一用語集。"
        f"原典 Glossary 章（p.147-155）の全{len(entries)}項目を収録している。\n\n",
        "## 使い方\n\n",
        "- 本文中で専門用語が**初出**する箇所では「日本語訳（English term）」の形で英語を併記する。\n",
        "- 2回目以降の出現では日本語訳のみを用い、訳語を統一する。\n",
        "- 新しい専門用語が本文中に見つかった場合は、この表に追加してから翻訳を進める。\n",
        "- 定義文（日本語）は原典 Glossary の定義を正確に翻訳したものであり、"
        "本文中の用語の意味を確認する際の参照として用いる。\n\n",
        "| English Term | 日本語訳 | 定義（日本語） |\n",
        "|---|---|---|\n",
    ]
    for t, _ in entries:
        ja_term, ja_def = TRANSLATIONS[t]
        row = [t, ja_term, ja_def]
        row = [c.replace("|", "\\|").replace("\n", " ") for c in row]
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} |\n")

    lines.append("\n## 追加用語（原典Glossary未収録）\n\n")
    lines.append(
        "原典 Glossary 章（p.147-155）には収録されていないが、本文中で鍵括弧付き（'…'）の術語として\n"
        "繰り返し使われている表現。翻訳作業の中で `scripts/glossary_supplementary.py` に追記し、本表に反映する。\n\n"
    )
    lines.append("| English Term | 日本語訳 | 定義（日本語） |\n")
    lines.append("|---|---|---|\n")
    for t, ja_term, ja_def in SUPPLEMENTARY:
        row = [c.replace("|", "\\|").replace("\n", " ") for c in (t, ja_term, ja_def)]
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} |\n")

    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} with {len(entries)} entries + {len(SUPPLEMENTARY)} supplementary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
