#!/usr/bin/env python3
"""Reproducible single-column PDF build, leaving the source manuscript unchanged."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
source = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'source-main.md'
target = source.with_suffix('.pdf')
work = ROOT / 'tmp' / 'pdfs' / source.stem
work.mkdir(parents=True, exist_ok=True)
text = source.read_text()
# Normalize Unicode dash codepoints only in the typesetting copy.
for c in ('\u2010', '\u2011', '\u2012', '\u2013', '\u2014', '\u2212'):
    text = text.replace(c, '-')
# Typeset the manuscript's existing frontmatter once, as an academic title block.
def latex_escape(s):
    replacements={'&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_'}
    return ''.join(replacements.get(c,c) for c in s)
lines=text.splitlines()
if len(lines)>2 and lines[0].startswith('# ') and lines[1].startswith('## '):
    abstract=text.find('## Abstract')
    if abstract>=0:
        front=text[:abstract].splitlines()
        title=latex_escape(front[0][2:])
        subtitle=latex_escape(front[1][3:])
        metadata=[]
        for line in front[2:]:
            if line.strip():
                line=latex_escape(line.strip())
                line=re.sub(r'\*\*(.*?)\*\*',r'\\textbf{\1}',line)
                metadata.append(line)
        titleblock='\\begin{center}\n{\\LARGE\\bfseries '+title+'\\par}\n\\vspace{0.55em}\n{\\large\\bfseries '+subtitle+'\\par}\n\\vspace{0.85em}\n{\\small '+r'\\[0.2em]'.join(metadata)+'\\par}\n\\end{center}\n\n'
        text=titleblock+text[abstract:]
render_source = work / 'typesetting.md'
render_source.write_text(text)
header = work / 'header.tex'
header.write_text(r'''
\usepackage{microtype}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{etoolbox}
\usepackage{xurl}
\usepackage{needspace}
\usepackage{enumitem}
\setlength{\emergencystretch}{3em}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.55em}
\setlist{itemsep=0.15em,topsep=0.25em,parsep=0pt}
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.1}
\AtBeginEnvironment{longtable}{\footnotesize}
\AtBeginEnvironment{tabular}{\footnotesize}
\AtBeginEnvironment{quote}{\small}
\titleformat{\section}{\normalfont\Large\bfseries}{\thesection}{0.5em}{}
\titleformat{\subsection}{\normalfont\large\bfseries}{\thesubsection}{0.5em}{}
\titleformat{\subsubsection}{\normalfont\normalsize\bfseries}{\thesubsubsection}{0.5em}{}
\titlespacing*{\section}{0pt}{1.6em}{0.65em}
\titlespacing*{\subsection}{0pt}{1.2em}{0.5em}
\titlespacing*{\subsubsection}{0pt}{1.0em}{0.4em}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\itshape Unified Consciousness Theory III}
\fancyhead[R]{\small Theoretical preprint}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.25pt}
\setlength{\headheight}{14pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\small\thepage}\renewcommand{\headrulewidth}{0pt}}
\AtBeginDocument{\thispagestyle{plain}}
\widowpenalty=10000
\clubpenalty=10000
\displaywidowpenalty=10000
''')
tex = work / 'manuscript.tex'
cmd = ['pandoc',str(render_source),'-f','markdown+tex_math_single_backslash+autolink_bare_uris','-t','latex','-s',
       '--pdf-engine=xelatex','--include-in-header',str(header),
       '-V','documentclass:article','-V','fontsize:11pt','-V','papersize:a4',
       '-V','geometry:top=25mm,bottom=24mm,left=23mm,right=23mm',
       '-V','mainfont:Latin Modern Roman','-V','sansfont:Latin Modern Sans',
       '-V','monofont:DejaVu Sans Mono','-V','mathfont:Latin Modern Math',
       '-V','linestretch:1.08','-V','colorlinks:true','-V','linkcolor:MidnightBlue',
       '-V','urlcolor:MidnightBlue','-o',str(tex)]
subprocess.run(cmd, check=True, capture_output=True, text=True)
latex = tex.read_text()
# Prevent a running header on title page; keep all equations authored in math.
latex = latex.replace(r'\begin{longtable}', r'\Needspace{10\baselineskip}'+'\n'+r'\begin{longtable}')
tex.write_text(latex)
logs=[]
for i in range(2):
    p = subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',str(tex.name)],
                       cwd=work, capture_output=True, text=True)
    logs.append(p.stdout + '\n' + p.stderr)
    (work / f'build-pass-{i+1}.log').write_text(logs[-1])
    if p.returncode:
        print(logs[-1][-12000:])
        raise SystemExit(p.returncode)
target.write_bytes((work / 'manuscript.pdf').read_bytes())
warnings=[line for line in logs[-1].splitlines() if any(x in line for x in ['Overfull','Underfull','Missing character','Warning'])]
print('\n'.join(warnings) if warnings else 'No typesetting warnings.')
print(target)
