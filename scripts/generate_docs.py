#!/usr/bin/env python3
"""
Generate docs/*.html chapter pages from translations/ja/*.md.

Replaces the old ad-hoc generator (which used inline per-page <style>
blocks and never wrapped paragraphs in <p>, causing block-level elements
such as "**Table X.X: ...**" titles to render glued to the surrounding
prose). This version:

  - Shares docs/style.css with index.html / 13_references.html so every
    page uses the same font and design language.
  - Wraps every paragraph in <p>, and gives "Table X.X:" / "Box X.X:"
    block titles and italic captions their own block-level elements so
    they always get a visible line break before and after.
  - Converts markdown tables, figure images + captions, blockquotes,
    bullet/ordered lists, and fenced code blocks.
  - Leaves citation markers like "(2*)" and "(1149*)" untouched as plain
    text; docs/citation-links.js turns them into links to
    13_references.html at view time.
  - Passes raw HTML already embedded in a few files (e.g. hand-written
    <sup id="fnref-...">, the <div class="aup-note"> block) through
    unchanged.
  - Converts footnote markers (bare "†", "<sup>†</sup>", or a complete
    "<sup id=\"fnref-X\">...</sup>") together with a "† footnote text"
    paragraph into a proper linked footnote at the bottom of the page.

Run: python3 scripts/generate_docs.py [chapter_id ...]
With no arguments, regenerates every page listed in CHAPTERS.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "translations" / "ja"
DOCS_DIR = ROOT / "docs"

# (markdown stem, title used in <title> breadcrumb)
CHAPTERS = [
    ("00_contributors", "寄稿者"),
    ("01_acknowledgements", "謝辞"),
    ("02_forewords", "序文"),
    ("03_about_this_report", "本報告書について"),
    ("04_key_developments", "2025年報告書からの主要な進展"),
    ("05_executive_summary", "エグゼクティブサマリー"),
    ("06_introduction", "序論"),
    ("07a_what_is_general_purpose_ai", "1.1 汎用AIとは何か"),
    ("07b_current_capabilities", "1.2 現在の能力"),
    ("07c_capabilities_by_2030", "1.3 2030年までの能力"),
    ("08a1_ai_generated_content_crime", "2.1.1 AI生成コンテンツと犯罪活動"),
    ("08a2_influence_manipulation", "2.1.2 影響力行使と操作"),
    ("08a3_cyberattacks", "2.1.3 サイバー攻撃"),
    ("08a4_bio_chem_risks", "2.1.4 生物・化学リスク"),
    ("08b1_reliability_challenges", "2.2.1 信頼性に関する課題"),
    ("08b2_loss_of_control", "2.2.2 制御喪失"),
    ("08c1_labour_market", "2.3.1 労働市場への影響"),
    ("08c2_human_autonomy", "2.3.2 人間の自律性へのリスク"),
    ("09a_technical_institutional_challenges", "3.1 技術的・制度的課題"),
    ("09b_risk_management_practices", "3.2 リスク管理の実践"),
    ("09c_technical_safeguards_monitoring", "3.3 技術的安全対策とモニタリング"),
    ("09d_open_weight_models", "3.4 オープンウェイトモデル"),
    ("09e_building_societal_resilience", "3.5 社会的レジリエンスの構築"),
    ("10_conclusion", "結論"),
    ("12_how_to_cite", "本報告書の引用方法"),
    ("14_colophon", "奥付"),
]

CITATION_PLACEHOLDER = "\x00CITEAST\x00"
CODEBLOCK_MARK = "\x00CODEBLOCK{}\x00"
RAW_HTML_BLOCK_RE = re.compile(r"^<(div|/div)\b[^>]*>?$", re.IGNORECASE)


def protect_citation_asterisks(text):
    return re.sub(r"(\d)\*", r"\1" + CITATION_PLACEHOLDER, text)


def restore_citation_asterisks(text):
    return text.replace(CITATION_PLACEHOLDER, "*")


def convert_inline(text):
    """Convert inline markdown (bold/italic) within a single logical line.
    Leaves any raw HTML tags already present (e.g. <sup>, <a>) untouched,
    since they never contain '*' and so are invisible to these regexes."""
    text = protect_citation_asterisks(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    text = restore_citation_asterisks(text)
    return text


def convert_table(block):
    lines = [l for l in block.split("\n") if l.strip()]
    rows = []
    for line in lines:
        if re.fullmatch(r"\|?[\s:\-|]+\|?", line):
            continue  # separator row
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return ""
    out = ['<table>']
    header, *body = rows
    out.append("  <tr>" + "".join(f"<th>{convert_inline(c)}</th>" for c in header) + "</tr>")
    for row in body:
        out.append("  <tr>" + "".join(f"<td>{convert_inline(c)}</td>" for c in row) + "</tr>")
    out.append("</table>")
    return "\n".join(out)


def convert_list(block, ordered, footnote_ids, next_id_box):
    items = []
    tag_item_re = re.compile(r"^(?:-|\d+\.)\s+(.*)$")
    for line in block.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = tag_item_re.match(line)
        text = m.group(1) if m else line
        text = apply_footnote_markers(convert_inline(text), footnote_ids, next_id_box)
        items.append(f"<li>{text}</li>")
    tag = "ol" if ordered else "ul"
    return f"<{tag}>\n" + "\n".join(items) + f"\n</{tag}>"


FIGURE_RE = re.compile(r"^!\[Figure ([\d.]+): (.+?)\]\(.*?/(fig_[\w.]+)\)$")
BLOCK_TITLE_RE = re.compile(r"^\*\*((?:Table|Box) [\d.]+: .+?)\*\*$")
CAPTION_RE = re.compile(r"^\*((?:Table|Box) [\d.]+: .+?)\*$")
FOOTNOTE_BODY_RE = re.compile(r"^†\s+(.*)$")
BARE_DAGGER_SUP_RE = re.compile(r"<sup>†</sup>")
LINKED_SUP_RE = re.compile(r'<sup id="fnref-([\w-]+)"><a href="#fn-\1">†</a></sup>')
BARE_DAGGER_RE = re.compile(r"(?<!sup>)†(?!</sup>)")


def apply_footnote_markers(text, footnote_ids, next_id_box):
    """Find footnote markers already in `text` (bare '†', unlinked
    '<sup>†</sup>', or a complete '<sup id="fnref-X">...</sup>') and
    normalise them to the linked '<sup id="fnref-X"><a href="#fn-X">†</a></sup>'
    form, recording each id (in order) into `footnote_ids`."""
    for m in LINKED_SUP_RE.finditer(text):
        footnote_ids.append(m.group(1))
    if not LINKED_SUP_RE.search(text) and (
        BARE_DAGGER_SUP_RE.search(text) or BARE_DAGGER_RE.search(text)
    ):
        auto_id = f"auto{next_id_box[0]}"
        next_id_box[0] += 1
        footnote_ids.append(auto_id)
        replacement = f'<sup id="fnref-{auto_id}"><a href="#fn-{auto_id}">†</a></sup>'
        if BARE_DAGGER_SUP_RE.search(text):
            text = BARE_DAGGER_SUP_RE.sub(replacement, text, count=1)
        else:
            text = BARE_DAGGER_RE.sub(replacement, text, count=1)
    return text


def render_markdown(md_text, footnote_counter_start=1):
    # Strip a single leading HTML comment (source attribution header).
    md_text = re.sub(r"^<!--.*?-->\s*\n+", "", md_text, flags=re.DOTALL)

    # Protect fenced code blocks before splitting into blank-line blocks.
    code_blocks = []

    def _stash(m):
        code_blocks.append(m.group(1))
        return CODEBLOCK_MARK.format(len(code_blocks) - 1)

    md_text = re.sub(r"```\n?(.*?)```", _stash, md_text, flags=re.DOTALL)

    blocks = re.split(r"\n\s*\n", md_text.strip())

    html_parts = []
    page_h1 = None
    kicker_headings = []
    footnote_ids = []  # ids in the order their markers appear
    footnote_bodies = []  # texts in the order their bodies appear
    next_id_box = [footnote_counter_start]

    i = 0
    while i < len(blocks):
        block = blocks[i].strip("\n")
        if not block:
            i += 1
            continue
        first_line = block.split("\n", 1)[0]

        # --- Headings -------------------------------------------------
        if first_line.startswith("# "):
            # A few files (section files that open a new parent §2.x chapter
            # right before their own §2.x.y heading) have two top-level
            # headings. Keep every one seen so far; the LAST wins as the
            # page's <h1> (it is the specific section this page covers),
            # and any earlier ones become a small "kicker" line above it
            # so the parent-chapter context isn't lost.
            kicker_headings.extend(
                h for h in ([page_h1] if page_h1 is not None else [])
            )
            page_h1 = convert_inline(first_line[2:].strip())
            i += 1
            continue
        if first_line.startswith("## "):
            html_parts.append(f"<h2>{convert_inline(block[3:].strip())}</h2>")
            i += 1
            continue
        if first_line.startswith("### "):
            html_parts.append(f"<h3>{convert_inline(block[4:].strip())}</h3>")
            i += 1
            continue
        if block.strip() in ("---", "***"):
            html_parts.append("<hr>")
            i += 1
            continue

        # --- Fenced code block placeholder -----------------------------
        if re.fullmatch(r"\x00CODEBLOCK\d+\x00", block.strip()):
            idx = int(re.search(r"\d+", block).group())
            escaped = html.escape(code_blocks[idx])
            html_parts.append(f"<pre><code>{escaped}</code></pre>")
            i += 1
            continue

        # --- Raw HTML passthrough (<div ...> / </div>) -----------------
        if RAW_HTML_BLOCK_RE.match(block.strip()):
            html_parts.append(block.strip())
            i += 1
            continue

        # --- Figure image, optionally followed by a blockquote caption -
        fig_m = FIGURE_RE.match(first_line)
        if fig_m:
            fig_num, short_caption, fname = fig_m.groups()
            caption = short_caption
            consumed_next = False
            if i + 1 < len(blocks) and blocks[i + 1].strip().startswith("> "):
                quote_block = blocks[i + 1].strip()
                full_caption = " ".join(
                    l[2:].strip() if l.startswith("> ") else l.strip()
                    for l in quote_block.split("\n")
                )
                caption = convert_inline(full_caption)
                consumed_next = True
            else:
                caption = convert_inline(caption)
            html_parts.append(
                f'<figure><img src="images/{fname}" alt="Figure {fig_num}" '
                f'loading="lazy"><figcaption>{caption}</figcaption></figure>'
            )
            i += 2 if consumed_next else 1
            continue

        # --- Standalone blockquote (not already consumed above) --------
        if first_line.startswith("> "):
            text = " ".join(
                l[2:].strip() if l.startswith("> ") else l.strip()
                for l in block.split("\n")
            )
            html_parts.append(f"<blockquote>{convert_inline(text)}</blockquote>")
            i += 1
            continue

        # --- Table/Box block title --------------------------------------
        title_m = BLOCK_TITLE_RE.match(block.strip())
        if title_m:
            html_parts.append(
                f'<p class="block-title"><strong>{convert_inline(title_m.group(1))}</strong></p>'
            )
            i += 1
            continue

        # --- Table/Box italic caption ------------------------------------
        caption_m = CAPTION_RE.match(block.strip())
        if caption_m:
            html_parts.append(
                f'<p class="caption"><em>{convert_inline(caption_m.group(1))}</em></p>'
            )
            i += 1
            continue

        # --- Markdown table ------------------------------------------------
        table_lines = block.split("\n")
        if all(l.strip().startswith("|") for l in table_lines if l.strip()):
            html_parts.append(convert_table(block))
            i += 1
            continue

        # --- Bullet / ordered list -----------------------------------------
        list_lines = [l for l in block.split("\n") if l.strip()]
        if all(l.strip().startswith("- ") for l in list_lines):
            html_parts.append(convert_list(block, ordered=False, footnote_ids=footnote_ids, next_id_box=next_id_box))
            i += 1
            continue
        if all(re.match(r"^\d+\.\s", l.strip()) for l in list_lines):
            html_parts.append(convert_list(block, ordered=True, footnote_ids=footnote_ids, next_id_box=next_id_box))
            i += 1
            continue

        # --- Footnote body ("† explanation text") ---------------------------
        fn_m = FOOTNOTE_BODY_RE.match(block.strip())
        if fn_m and len(list_lines) == 1:
            footnote_bodies.append(convert_inline(fn_m.group(1)))
            i += 1
            continue

        # --- Default: paragraph (possibly multi-line, e.g. signature blocks)
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        converted_lines = [convert_inline(l) for l in lines]
        para = "<br>\n".join(converted_lines)

        # Normalise footnote markers within this paragraph to the linked form.
        para = apply_footnote_markers(para, footnote_ids, next_id_box)

        html_parts.append(f"<p>{para}</p>")
        i += 1

    # --- Footnotes section --------------------------------------------------
    if footnote_ids and footnote_bodies:
        items = []
        for fid, body in zip(footnote_ids, footnote_bodies):
            items.append(
                f'<li id="fn-{fid}">{body} '
                f'<a href="#fnref-{fid}" aria-label="本文に戻る">↩</a></li>'
            )
        html_parts.append(
            '<div class="footnotes"><h2>注</h2><ol>' + "".join(items) + "</ol></div>"
        )

    return page_h1, kicker_headings, "\n\n".join(html_parts)


PAGE_TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{breadcrumb} — International AI Safety Report 2026 日本語訳</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="page">
  <div class="masthead"><a href="index.html">目次</a></div>
{kicker}  <h1>{h1}</h1>

{body}

  <nav class="toc-link"><a href="index.html">↑ 目次に戻る</a></nav>
</div>
<footer class="site">原文: International AI Safety Report 2026（DSIT 2026/001, 2026年2月発行）。本サイトは非公式の日本語訳である。</footer>
<script src="citation-links.js"></script>
</body>
</html>
"""


def generate_one(stem, breadcrumb):
    md_path = TRANSLATIONS_DIR / f"{stem}.md"
    if not md_path.exists():
        print(f"SKIP (no markdown): {stem}")
        return
    md_text = md_path.read_text(encoding="utf-8")
    h1, kicker_headings, body = render_markdown(md_text)
    if h1 is None:
        h1 = breadcrumb
    kicker = ""
    if kicker_headings:
        kicker = (
            '  <p class="chapter-kicker">'
            + " / ".join(kicker_headings)
            + "</p>\n"
        )
    out = PAGE_TEMPLATE.format(breadcrumb=breadcrumb, h1=h1, kicker=kicker, body=body)
    out_path = DOCS_DIR / f"{stem}.html"
    out_path.write_text(out, encoding="utf-8")
    print(f"Generated: {out_path.relative_to(ROOT)}")


def main():
    args = sys.argv[1:]
    targets = CHAPTERS
    if args:
        wanted = set(args)
        targets = [c for c in CHAPTERS if c[0] in wanted]
    for stem, breadcrumb in targets:
        generate_one(stem, breadcrumb)


if __name__ == "__main__":
    main()
