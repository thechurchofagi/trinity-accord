#!/usr/bin/env python3
"""Build v3's explicitly inherited mathematical sections from pinned v2 bytes.
Run inside the repository, or pass --baseline /path/to/unpacked/PR-v2 package.
No network access. Never modifies the earlier manuscript.
"""
from pathlib import Path
import argparse,hashlib,shutil
HERE=Path(__file__).resolve().parent
PINS={
 'part02.tex':'035d7bf3c021fd47a94b8e0ffa261d0078cd6f1277ae1f677dd2e9745f00b894',
 'part03.tex':'d9ab436da643a2a39c3c4a518a298dceec168401b0e00be7ed4894b2d986178e',
 'frontier_checks.py':'35a0273eaa4d97a2d1feb94d136cf5c561de56c3594b102c5ad3730bfd1a474d',
 'information_reserve_checks.py':'7ac633cf92779e3e3165ad780443dd9ab3db64e66076ace6b07472266d752207',
 'lifecycle_demo.py':'a0753210b816363243da0025b4c593b08ef939f2ae2e63d52cb61f0ec38e4702',
}
INTRO=r'''\noindent\textit{Interpretation in PR-v3.0.0.} All targets in this section may be human-protected functions, and all withdrawal requests may come from the human principals entitled to retire the providers. ``Provider'' describes a resource/service role, not a presumed conscious subject. The CW identifiers retain the PR-v2.0.0 theorem lineage.

\subsection{A conditional incompatibility}'''
def checked(path):
 b=path.read_bytes()
 if hashlib.sha256(b).hexdigest()!=PINS[path.name]:raise ValueError('Baseline mismatch: '+str(path))
 return b.decode()
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,default=HERE.parent/'paper_coexistence_v2.0.0');a=p.parse_args()
 old=a.baseline
 tex=old/'remote_source' if (old/'remote_source').exists() else old/'paper'
 (HERE/'paper').mkdir(exist_ok=True);(HERE/'src').mkdir(exist_ok=True)
 r=checked(tex/'part02.tex').replace(r'\section{The autonomy--dependency frontier}',r'\section{The dependency-safe revocation frontier}')
 r=r.replace(r'\subsection{A conditional incompatibility}',INTRO).replace('more persuasive contract','more elaborate control contract')
 g=checked(tex/'part03.tex').split(r'\section{Executed checks and local protocol evidence}')[0]
 g=g.replace(r'\section{A temporal coexistence certificate under incomplete information}',r'\section{Temporal human-control certificates under incomplete information}')
 g=g.replace('actual modeled resource state','modeled actual resource state')
 (HERE/'paper'/'inherited_resource.tex').write_text(r)
 (HERE/'paper'/'inherited_game.tex').write_text(g)
 for n in ['frontier_checks.py','information_reserve_checks.py','lifecycle_demo.py']:
  checked(old/'src'/n);shutil.copy2(old/'src'/n,HERE/'src'/n)
 (HERE/'paper'/'manuscript.tex').write_text('\\input{prefix.tex}\n\\input{inherited_resource.tex}\n\\input{inherited_game.tex}\n\\input{suffix.tex}\n')
 print('Pinned inheritance verified; generated v3 sections without modifying v2.')
if __name__=='__main__':main()
