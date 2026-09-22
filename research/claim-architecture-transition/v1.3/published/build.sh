#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
python3 audit.py --out rerun
SOURCE_DATE_EPOCH=1790035200 pandoc claim-architecture-transition-v1.3.md --from=markdown+tex_math_dollars --pdf-engine=xelatex -V "mainfont=TeX Gyre Pagella" -V "CJKmainfont=Noto Serif CJK SC" -o rebuilt.pdf
