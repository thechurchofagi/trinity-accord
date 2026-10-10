#!/usr/bin/env python3
"""Build the exact reviewed English SCU release from one DOI-bound Markdown file."""
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
if len(sys.argv)!=2:
    raise SystemExit('Usage: build_pdf.py manuscript.md')
source=Path(sys.argv[1]).resolve()
if source.suffix!='.md' or not source.is_file():
    raise SystemExit('A local Markdown manuscript is required')
target=source.with_suffix('.pdf')
subprocess.run(['pandoc',str(source),'--from=markdown+tex_math_dollars',
    '--standalone','--pdf-engine=xelatex','--resource-path='+str(ROOT),
    '-V','documentclass=article','-V','papersize=a4',
    '-V','mainfont=Latin Modern Roman','-V','mathfont=Latin Modern Math',
    '-V','monofont=DejaVu Sans Mono','-V','linestretch=1.04',
    '--include-in-header='+str(ROOT/'pdf_style.tex'),'-o',str(target)],cwd=ROOT,check=True)
print(target)
