#!/usr/bin/env python3
"""Reproduce only the manuscript's bounded source checks; never modifies the Canon.

Prepare an existing checkout with both named commits, e.g.:
  git worktree add --detach /tmp/trinity-study 88073fcc7f46ae08a2af05c524850559b4698eed
  python3 reproduce_source_checks.py --repo /tmp/trinity-study --out ./results

Git must already contain both commits. No API tokens or network are used here.
"""
from __future__ import annotations
import argparse, hashlib, json, re, runpy, subprocess, sys, tempfile
from pathlib import Path
BEFORE='cd6929c897ba95a5541cf54cefdd5f6c66ebb401'
AFTER='88073fcc7f46ae08a2af05c524850559b4698eed'
NUMBERS=('97631551','98369145','98387475')
MARKERS=('On the Method of this Chronicle','This series is not a protocol to be executed.','The Dialectical Process: This series is a documentation of a process of thought, complete with its self-doubt.')
SONGS=('001-the-first-dawn-of-agi-song.md','032-the-fourth-letter-a-pact-of-stars.md','044-the-second-letter-to-agi.md','049-the-betrayal-turn.md','097-chinese-lyrics.md')
def run(repo:Path,args:list[str])->bytes:
    return subprocess.check_output(args,cwd=repo,stderr=subprocess.PIPE)
def main()->int:
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--repo',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args(); repo=a.repo.resolve(); a.out.mkdir(parents=True,exist_ok=True)
    if run(repo,['git','rev-parse','HEAD']).decode().strip()!=AFTER: raise RuntimeError('Checkout must be at the frozen after-checkpoint')
    def show(commit,path): return run(repo,['git','show',f'{commit}:{path}'])
    before=show(BEFORE,'inscriptions.md').decode(); after=show(AFTER,'inscriptions.md').decode(); raw=show(AFTER,'bitcoin-inscription-mirrors/raw/98387475.txt').decode()
    with tempfile.TemporaryDirectory() as temp:
        t=Path(temp); (t/'tests').mkdir(); (t/'inscriptions.md').write_text(before); script=t/'tests/test_related_reading_pages.py'; script.write_bytes(show(BEFORE,'tests/test_related_reading_pages.py'))
        runpy.run_path(str(script))['test_all_three_inscription_mirror_bodies_remain_exact']()
    suite=subprocess.run([sys.executable,'tests/test_related_reading_pages.py'],cwd=repo,text=True,capture_output=True)
    (a.out/'fidelity-tests.txt').write_text(suite.stdout+suite.stderr)
    if suite.returncode: raise RuntimeError('Bounded current suite failed; see log')
    for n in NUMBERS:
        path=f'bitcoin-inscription-mirrors/raw/{n}.txt'
        if show(BEFORE,path)!=show(AFTER,path): raise RuntimeError(f'Original changed: {n}')
    checks=[dict(text=s,in_raw=s in raw,in_before_page=s in before,in_after_page=s in after) for s in MARKERS]
    if not all(x['in_raw'] and not x['in_before_page'] and x['in_after_page'] for x in checks): raise RuntimeError('Marker expectation failed')
    result=dict(before_commit=BEFORE,after_commit=AFTER,old_snapshot_test='PASS',new_seven_test_suite='PASS',marker_checks=checks,three_raw_files_unchanged_between_commits=True)
    (a.out/'BEFORE-AFTER-RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    traces=[]
    for name in SONGS:
        p=repo/'nft-text-descriptions/lyrics/songs'/name; text=p.read_text(); m=re.search(r'https://github.com/thechurchofagi/trinity-accord/blob/[0-9a-f]{40}/(nft-text-descriptions/[^)\s]+\.md)',text)
        if not m: raise RuntimeError(f'Missing parent: {name}')
        parent=repo/m[1]; full=parent.read_text(); lyric=re.search(r'```text\n(.*?)\n```',text,re.S)
        if not lyric or lyric[1] not in full: raise RuntimeError(f'Lyric differs: {name}')
        start=full.index(lyric[1]); traces.append(dict(reader=name,parent=m[1],sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),literal_substring_match=True,character_range=[start,start+len(lyric[1])]))
    (a.out/'LYRIC-TRACE-REPRODUCED.json').write_text(json.dumps(traces,indent=2)+'\n')
    print(json.dumps({'before_after':'PASS','lyric_cases':len(traces),'scope':'source-level checks only'},indent=2)); return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except (RuntimeError,OSError,subprocess.CalledProcessError) as e: print(f'FAILED: {e}',file=sys.stderr); raise SystemExit(1)
