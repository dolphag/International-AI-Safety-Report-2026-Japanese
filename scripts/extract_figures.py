#!/usr/bin/env python3
"""
Extract figure images from the source PDF into docs/images/.

Most figures in this report are vector drawings (charts, diagrams) rather
than embedded raster images, so a naive "extract embedded images" approach
(e.g. PyMuPDF's page.get_images()) misses most of them. This script instead
renders the region of the page occupied by the figure as a PNG:

  1. Find the figure's caption ("Figure X.Y:") on its PDF page to get a
     reference y-position.
  2. Collect the bounding boxes of every vector drawing AND every embedded
     raster image on that page that lies above the caption (figures are
     always drawn above their caption in this report's layout).
  3. Take the union of those boxes, pad it slightly, and render just that
     region at 3x zoom (print quality) with page.get_pixmap(clip=bbox).

This handles both pure-vector charts (e.g. Figure 1.1's neural network
diagram) and figures built from embedded photos (e.g. Figure 2.2's grid of
AI-generated sample images) with the same code path.

Usage:
    python3 scripts/extract_figures.py <page_label>:<fig_number>:<output_name> [...]

    page_label   the PDF's own printed page number (as seen in source/*.txt
                 "[[page N]]" markers), NOT the 0-indexed fitz page index
    fig_number   the figure's number as it appears after "Figure " in its
                 caption, e.g. "3.6" (no need to include "Figure ")
    output_name  output file stem; written to docs/images/<output_name>.png

Example (figures 1.1 on page 19 and 1.2 on page 20):
    python3 scripts/extract_figures.py 19:1.1:fig_1_1 20:1.2:fig_1_2

To find which PDF page a given figure is on, search the relevant
source/*.txt chunk for "Figure X.Y:" -- the chunk header gives the PDF
page range, and grep for the exact caption pins down the page.
"""
import sys
from pathlib import Path

import pymupdf as fitz  # `import fitz` directly is a deprecated alias

ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = ROOT / "international-ai-safety-report-2026_1.pdf"
OUT_DIR = ROOT / "docs" / "images"


def find_caption_rect(page, fig_number):
    """Locate the 'Figure X.Y:' caption text on the page, in DISPLAY
    (rotated) coordinates -- see the note on page.rotation_matrix below.
    A figure number can also appear earlier on the page as an in-text
    citation (e.g. "(Figure 1.5)", with no colon) -- only the
    colon-suffixed caption itself should anchor the crop, and when it
    appears more than once (rare), the last match is the actual caption
    (captions sit below the artwork; any earlier match is an in-body
    reference)."""
    results = page.search_for(f"Figure {fig_number}:")
    if not results:
        return None
    return results[-1] * page.rotation_matrix


def get_visual_bbox(page, caption_rect, pad=6):
    # get_drawings()/get_images()/get_image_bbox()/search_for() all report
    # coordinates in the page's UNROTATED space (mediabox-relative). A
    # landscape page that is internally stored as a rotated portrait page
    # (page.rotation != 0) therefore needs every rect transformed through
    # page.rotation_matrix into DISPLAY space before it's compared against
    # the caption position or unioned into a crop box -- otherwise the
    # "above the caption" test and the final clip (which get_pixmap expects
    # in display space, matching page.rect) silently operate on mismatched
    # coordinate systems and the crop comes out wrong (e.g. truncated on
    # one side) on any rotated page. On an unrotated page rotation_matrix
    # is the identity, so this is a no-op there.
    rot = page.rotation_matrix
    rects = []
    for d in page.get_drawings():
        r = d["rect"] * rot
        if r.width <= 0 or r.height <= 0:
            continue
        if caption_rect is None or r.y1 <= caption_rect.y0 + 20:
            rects.append(r)
    for img in page.get_images(full=True):
        try:
            bbox = page.get_image_bbox(img) * rot
            if caption_rect is None or bbox.y1 <= caption_rect.y0 + 20:
                rects.append(bbox)
        except Exception:
            pass
    if not rects:
        return None
    x0 = max(0, min(r.x0 for r in rects) - pad)
    y0 = max(0, min(r.y0 for r in rects) - pad)
    x1 = min(page.rect.width, max(r.x1 for r in rects) + pad)
    y1 = min(page.rect.height, max(r.y1 for r in rects) + pad)
    return fitz.Rect(x0, y0, x1, y1)


def extract(doc, page_label, fig_number, out_name, zoom=3):
    page = doc[page_label - 1]  # fitz page index = printed page label - 1
    caption_rect = find_caption_rect(page, fig_number)
    bbox = get_visual_bbox(page, caption_rect)
    if bbox is None:
        print(f"WARNING: no drawings/images found for Figure {fig_number} "
              f"on page {page_label}; falling back to the full page. "
              f"Check the crop and re-run with a manual bbox if needed.")
        bbox = page.rect
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=bbox)
    out_path = OUT_DIR / f"{out_name}.png"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pix.save(out_path)
    try:
        shown_path = out_path.relative_to(ROOT)
    except ValueError:
        shown_path = out_path
    print(f"Saved {shown_path}  (page {page_label}, "
          f"{pix.width}x{pix.height}, bbox {[round(v, 1) for v in bbox]})")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    doc = fitz.open(PDF_PATH)
    for spec in sys.argv[1:]:
        page_label_s, fig_number, out_name = spec.split(":")
        extract(doc, int(page_label_s), fig_number, out_name)


if __name__ == "__main__":
    main()
