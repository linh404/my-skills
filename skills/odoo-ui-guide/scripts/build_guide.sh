#!/usr/bin/env bash
# Build a user guide: Markdown (+ screenshots) -> DOCX (pandoc, styled, with TOC) -> refreshed TOC + PDF (LibreOffice).
# Usage: build_guide.sh guide.md [output_basename]
#   Images are resolved relative to the Markdown file. Outputs <output_basename>.docx and .pdf
#   (default: next to the Markdown file, same name).
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MD="$(realpath "$1")"
OUT="${2:-${MD%.md}}"
OUT="$(realpath -m "$OUT")"
MD_DIR="$(dirname "$MD")"
TOC_TITLE="${TOC_TITLE:-Mục lục}"

mkdir -p "$(dirname "$OUT")"
pandoc "$MD" \
    --from markdown+pipe_tables+grid_tables+yaml_metadata_block \
    --to docx \
    --reference-doc "$SKILL_DIR/assets/reference.docx" \
    --resource-path "$MD_DIR" \
    --toc --toc-depth 2 \
    --metadata toc-title="$TOC_TITLE" \
    -o "$OUT.docx"

/usr/bin/python3 "$SKILL_DIR/scripts/update_docx.py" "$OUT.docx" "$OUT.pdf"
pdfinfo "$OUT.pdf" | grep -E '^(Title|Pages):' || true
