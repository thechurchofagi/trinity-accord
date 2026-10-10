#!/usr/bin/env python3
"""Rebuild the working manuscript PDF with Pandoc and XeLaTeX."""
from pathlib import Path
import subprocess
import sys

base = Path(__file__).resolve().parent
stem = 'Matched_Behavior_and_Source_Use_v1.0.0'
subprocess.run([sys.executable,str(base/'make_figure.py')],check=True)
cmd = ['pandoc',str(base/(stem+'.md')),'--from=markdown+tex_math_dollars',
       '--standalone','--pdf-engine=xelatex','--resource-path='+str(base),
       '-V','documentclass=article','-V','papersize=a4',
       '-V','mainfont=Latin Modern Roman','-V','mathfont=Latin Modern Math',
       '-V','monofont=DejaVu Sans Mono','-V','linestretch=1.04',
       '--include-in-header='+str(base/'pdf_style.tex'),
       '-o',str(base/(stem+'.pdf'))]
subprocess.run(cmd,cwd=base,check=True)
print(base/(stem+'.pdf'))
