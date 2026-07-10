#!/usr/bin/env python3
"""
Extract text from the source PDF and split it into per-chapter/section
chunk files under source/, based on the PDF's own bookmark structure.

Known source-PDF extraction artifacts and how this script handles them:
  - Isolated U+FFFD characters are a font-encoding artifact that reliably
    stands in for a period ("."). Long runs of U+FFFD (table-of-contents
    dot leaders) are left alone since TOC pages are not translated.
  - Page 8 (Forewords, contribution from the Government of India) has an
    "AI" -> "Al" ligature bug local to that one page's embedded font.
    NOT auto-fixed here (a global "Al"->"AI" replace would corrupt
    legitimate "Al-" name prefixes in the References, e.g. "Al-Dahle").
    Fix manually if/when that page is translated.
  - A small number of pages (~25 of 220) have a spurious space inserted
    mid-word (e.g. "national" -> "nationa l"). Left as-is; harmless for a
    human/LLM translator reading for meaning, but noted here in case a
    future automated process matches on exact tokens.

Each output chunk file starts with a comment header giving the PDF page
range it was extracted from, for traceability back to the original.
"""
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / "international-ai-safety-report-2026_1.pdf"
OUT_DIR = ROOT / "source"

# (output filename, title, start_page_idx, end_page_idx_inclusive) - 0-indexed
SECTIONS = [
    ("00_contributors.txt", "Contributors", 1, 2),
    ("01_acknowledgements.txt", "Acknowledgements", 3, 4),
    ("02_forewords.txt", "Forewords", 5, 7),
    ("03_about_this_report.txt", "About this Report", 8, 8),
    ("04_key_developments.txt", "Key developments since the 2025 Report", 9, 9),
    ("05_executive_summary.txt", "Executive summary", 10, 12),
    ("06_introduction.txt", "Introduction", 13, 14),
    ("07_background.txt", "Background on general-purpose AI", 15, 42),
    ("07a_what_is_general_purpose_ai.txt", "What is general-purpose AI?", 16, 24),
    ("07b_current_capabilities.txt", "Current capabilities", 25, 30),
    ("07c_capabilities_by_2030.txt", "Capabilities by 2030", 31, 42),
    ("08_risks.txt", "Risks", 43, 94),
    ("08a_malicious_use.txt", "Risks from malicious use", 44, 69),
    ("08a1_ai_generated_content_crime.txt", "2.1.1 AI-generated content and criminal activity", 44, 48),
    ("08a2_influence_manipulation.txt", "2.1.2 Influence and manipulation", 49, 55),
    ("08a3_cyberattacks.txt", "2.1.3 Cyberattacks", 56, 62),
    ("08a4_bio_chem_risks.txt", "2.1.4 Biological and chemical risks", 63, 69),
    ("08b_malfunctions.txt", "Risks from malfunctions", 70, 82),
    ("08b1_reliability_challenges.txt", "2.2.1 Reliability challenges", 70, 74),
    ("08b2_loss_of_control.txt", "2.2.2 Loss of control", 75, 82),
    ("08c_systemic_risks.txt", "Systemic risks", 83, 94),
    ("08c1_labour_market.txt", "2.3.1 Labour market impacts", 83, 87),
    ("08c2_human_autonomy.txt", "2.3.2 Risks to human autonomy", 88, 94),
    ("09_risk_management.txt", "Risk management", 95, 144),
    ("09a_technical_institutional_challenges.txt", "Technical and institutional challenges", 96, 103),
    ("09b_risk_management_practices.txt", "Risk management practices", 104, 118),
    ("09c_technical_safeguards_monitoring.txt", "Technical safeguards and monitoring", 119, 130),
    ("09d_open_weight_models.txt", "Open-weight models", 131, 136),
    ("09e_building_societal_resilience.txt", "Building societal resilience", 137, 144),
    ("10_conclusion.txt", "Conclusion", 145, 145),
    ("11_glossary.txt", "Glossary", 146, 154),
    ("12_how_to_cite.txt", "How to cite this report", 155, 155),
    ("13_references.txt", "References", 156, 218),
    ("14_colophon.txt", "Colophon", 219, 219),
]

# Top-level chapters only (used to build the chunking manifest / TOC).
# Subsections above are extracted too, for finer-grained work, but the
# top-level file is the unit of translation per CLAUDE.md.
TOP_LEVEL = {
    "00_contributors.txt", "01_acknowledgements.txt", "02_forewords.txt",
    "03_about_this_report.txt", "04_key_developments.txt",
    "05_executive_summary.txt", "06_introduction.txt", "07_background.txt",
    "08_risks.txt", "09_risk_management.txt", "10_conclusion.txt",
    "11_glossary.txt", "12_how_to_cite.txt", "13_references.txt",
    "14_colophon.txt",
}


def clean_page_text(text: str) -> str:
    # Isolated U+FFFD -> period. Do not touch runs of 2+ (TOC dot leaders).
    text = re.sub(r"(?<!�)�(?!�)", ".", text)
    return text


def main():
    reader = PdfReader(str(PDF_PATH))
    OUT_DIR.mkdir(exist_ok=True)

    manifest_lines = ["# Chunk manifest\n", "\n",
                       "| # | File | Title | PDF pages | Top-level? |\n",
                       "|---|------|-------|-----------|------------|\n"]

    for n, (fname, title, start, end) in enumerate(SECTIONS, 1):
        parts = []
        for idx in range(start, end + 1):
            raw = reader.pages[idx].extract_text() or ""
            parts.append(f"[[page {idx + 1}]]\n" + clean_page_text(raw))
        body = "\n\n".join(parts)

        header = f"# {title}\n# Source PDF pages: {start + 1}-{end + 1}\n\n"
        (OUT_DIR / fname).write_text(header + body, encoding="utf-8")

        top = "yes" if fname in TOP_LEVEL else ""
        manifest_lines.append(
            f"| {n} | {fname} | {title} | {start + 1}-{end + 1} | {top} |\n"
        )

    (OUT_DIR / "_manifest.md").write_text("".join(manifest_lines), encoding="utf-8")
    print(f"Wrote {len(SECTIONS)} chunk files to {OUT_DIR}")


if __name__ == "__main__":
    sys.exit(main())
