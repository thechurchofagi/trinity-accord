#!/usr/bin/env python3
"""Build the exact DOI-bound CTD release with the reviewed Pandoc/XeLaTeX layout.

The publisher supplies one temporary Markdown file under this paper directory.
Figures and the frozen header stay relative to the paper directory; the generated
LaTeX/PDF and auxiliary files stay next to that temporary Markdown file.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
if len(sys.argv) != 2:
    raise SystemExit("Usage: build_pdf.py manuscript.md")
source = Path(sys.argv[1]).resolve()
if source.suffix != ".md" or not source.is_file() or ROOT not in source.parents:
    raise SystemExit("A local Markdown manuscript within the paper directory is required")

tex = source.with_suffix(".tex")
subprocess.run([
    "pandoc", str(source), "--standalone", "--from=markdown", "--to=latex",
    "--resource-path=" + str(ROOT),
    "--include-in-header=" + str(ROOT / "pdf_style.tex"),
    "-V", "mainfont=Latin Modern Roman",
    "-V", "sansfont=Latin Modern Sans",
    "-V", "monofont=DejaVu Sans Mono",
    "-V", "monofontoptions=Scale=0.82",
    "-V", "documentclass=article",
    "-o", str(tex),
], cwd=ROOT, check=True)
for _ in range(2):
    subprocess.run([
        "xelatex", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error",
        "-output-directory=" + str(source.parent), str(tex),
    ], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
print(source.with_suffix(".pdf"))
