#!/usr/bin/env python3
"""Build the English paper with Pandoc and XeLaTeX; preserve the source text."""
from pathlib import Path
import re,subprocess,tempfile
ROOT=Path(__file__).resolve().parent
stem='cross-substrate-phenomenal-comparison-v1.0'
s=(ROOT/'published'/f'{stem}.md').read_text()
# Use Pandoc's title block, then preserve all manuscript sections and appendices.
s=s.split('\n',2)[2].lstrip()
s=re.sub(r'^## (.+)$',r'# \1',s,flags=re.M)
s=re.sub(r'^### (.+)$',r'## \1',s,flags=re.M)
s=s.replace('**Author:** Hongju Liu  \n','').replace('**Date:** 24 September 2026  \n','')
s=s.replace('\n---\n\n*TA-TR-2026-15 · Version 1.0 · English edition · 24 September 2026.*','')
front,body=s.split('\n---\n',1)
s='\\begingroup\\small\n\n'+front+'\n\n\\endgroup\n'+body
s=s.replace('∎',r'$\square$')
s=s.replace('—','--').replace('–','-').replace('‑','-')
header=r'''\usepackage{xurl}
\let\originalmaketitle\maketitle
\renewcommand{\maketitle}{\originalmaketitle\vspace{-18pt}}
\usepackage{fvextra}
\DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\},fontsize=\scriptsize}
\usepackage{etoolbox}
\BeforeBeginEnvironment{longtable}{\begingroup\footnotesize\setlength{\tabcolsep}{3pt}\renewcommand{\arraystretch}{1.15}}
\AfterEndEnvironment{longtable}{\endgroup}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Cross-Substrate Phenomenal Comparison}
\fancyhead[R]{\small TA-TR-2026-15}
\fancyfoot[C]{\thepage}
\setlength{\headheight}{15pt}
\setlength{\emergencystretch}{3em}
\usepackage{needspace}
\pretocmd{\section}{\Needspace{5\baselineskip}}{}{}
\pretocmd{\subsection}{\Needspace{4\baselineskip}}{}{}
'''
with tempfile.TemporaryDirectory() as d:
 d=Path(d);(d/'paper.md').write_text(s);(d/'header.tex').write_text(header)
 args=['pandoc',str(d/'paper.md'),'-f','markdown+tex_math_single_backslash+autolink_bare_uris-yaml_metadata_block-simple_tables-multiline_tables','-s','--top-level-division=section','-V','documentclass=article','-V','fontsize=11pt','-V','geometry:a4paper,margin=24mm','-V','mainfont=Latin Modern Roman','-V','monofont=DejaVu Sans Mono','-V','colorlinks=true','-V','linkcolor=blue','-V','urlcolor=blue','-V','linestretch=1.05','-M','title=Cross-Substrate Phenomenal Comparison','-M','subtitle=A Typed Transformation-Transport Framework under Existential Uncertainty','-M','author=Hongju Liu','-M','date=24 September 2026','-H',str(d/'header.tex'),'-o',str(d/'paper.tex')]
 subprocess.run(args,check=True)
 for _ in range(2):
  p=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','paper.tex'],cwd=d,capture_output=True,text=True)
  if p.returncode: raise RuntimeError(p.stdout[-6000:])
 (ROOT/'published'/f'{stem}.pdf').write_bytes((d/'paper.pdf').read_bytes())
 (ROOT/'pdf-build.log').write_text((d/'paper.log').read_text())
 print('Built',ROOT/'published'/f'{stem}.pdf')
