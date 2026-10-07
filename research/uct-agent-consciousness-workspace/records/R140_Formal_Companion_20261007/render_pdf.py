"""Render the English review PDF with Pandoc/XeLaTeX; no external fetch is needed."""
from pathlib import Path
import os,re,subprocess,tempfile
REC=Path(__file__).resolve().parent
ROOT=REC.parent.parent
SOURCE=REC/'Organization_Capability_Experience_v0_2.md'
OUT=REC/'output/pdf/UCT_Formal_Companion_v0_2.pdf'
BASE='https://github.com/thechurchofagi/trinity-accord/blob/692a091ede41b0111c0423855a213566460793bc/research/uct-agent-consciousness-workspace/'
OUT.parent.mkdir(parents=True,exist_ok=True)
text=SOURCE.read_text()
def online(m):
 label,target=m.group(1),m.group(2)
 if '://' in target or target.startswith('#'): return m.group(0)
 path=(REC/target).resolve().relative_to(ROOT.resolve()).as_posix()
 return '['+label+']('+BASE+path+')'
text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',online,text)
text=text.replace('## Appendix A.', r'\clearpage'+'\n\n## Appendix A.',1)
header=r"""
\usepackage{fancyhdr}
\usepackage{microtype}
\usepackage{needspace}
\usepackage{xurl}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small UCT | Formal companion}
\fancyhead[R]{\small Review version 0.2}
\fancyfoot[C]{\small \thepage}
\fancypagestyle{plain}{
\fancyhf{}
\fancyhead[L]{\small UCT | Formal companion}
\fancyhead[R]{\small Review version 0.2}
\fancyfoot[C]{\small \thepage}
}
\setlength{\headheight}{15pt}
\setlength{\emergencystretch}{3em}
\setlength{\parskip}{5pt}
\setlength{\parindent}{0pt}
\widowpenalty=10000
\clubpenalty=10000
\let\oldsection\section
\renewcommand{\section}{\Needspace{5\baselineskip}\oldsection}
\let\oldsubsubsection\subsubsection
\renewcommand{\subsubsection}{\Needspace{8\baselineskip}\oldsubsubsection}
\let\oldsubsection\subsection
\renewcommand{\subsection}{\Needspace{8\baselineskip}\oldsubsection}
"""
with tempfile.TemporaryDirectory(prefix='uct_r140_') as d:
 tmp=Path(d);(tmp/'input.md').write_text(text);(tmp/'header.tex').write_text(header)
 subprocess.run(['pandoc',str(tmp/'input.md'),'-f','markdown+tex_math_single_backslash+autolink_bare_uris','--standalone',
 '--pdf-engine=xelatex','-V','mainfont=DejaVu Serif','-V','sansfont=DejaVu Sans',
 '-V','monofont=DejaVu Sans Mono','-V','fontsize=10.5pt','-V','geometry:margin=23mm',
 '-V','colorlinks=true','-V','urlcolor=blue','-V','linkcolor=black',
 '--include-in-header',str(tmp/'header.tex'),'-o',str(OUT)],check=True)
print(OUT)
