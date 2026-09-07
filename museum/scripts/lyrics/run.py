"""python scripts/lyrics/run.py --cache /path/to/cache [--ids eth-103,eth-151]"""
import argparse,os,pathlib,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--cache',required=True);p.add_argument('--ids',default='');p.add_argument('--stage',choices=['all','asr','vocals','emissions','transcript','align'],default='all');a=p.parse_args()
os.environ['MUSEUM_LYRICS_CACHE']=str(pathlib.Path(a.cache).resolve());os.environ['MUSEUM_LYRICS_IDS']=a.ids
here=pathlib.Path(__file__).resolve().parent
stages=['asr','vocals','emissions','transcript','align'] if a.stage=='all' else [a.stage]
for stage in stages:subprocess.run([sys.executable,str(here/(stage+'.py'))],check=True)
