#!/usr/bin/env python3
"""Bounded read retries; no automatic write retry or assumed empty account list."""
import importlib.util
from pathlib import Path
import time
import urllib.error
from datetime import datetime, timezone

spec=importlib.util.spec_from_file_location('editorial_manager',Path(__file__).with_name('manage.py'))
manager=importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)
original_factory=manager.zenodo

class ReadRetry:
    def __init__(self,client): self.client=client
    def safe_read(self,callback,attempts=2):
        for attempt in range(attempts):
            try: return callback()
            except urllib.error.HTTPError as exc:
                if exc.code not in {429,500,502,503,504} or attempt==attempts-1: raise
                print('Transient Zenodo read failure; retry',attempt+1,'HTTP',exc.code,flush=True)
                time.sleep(2**(attempt+1))
            except (TimeoutError,urllib.error.URLError):
                if attempt==attempts-1: raise
                time.sleep(2**(attempt+1))
    def own_matching_deposits(self):
        matches=[]; seen=set()
        for page in range(1,41):
            rows=self.safe_read(lambda:self.client.request('/deposit/depositions?size=100&page='+str(page)))
            if not isinstance(rows,list): raise RuntimeError('Unexpected account listing shape')
            ids=[r.get('id') for r in rows]
            if len(set(ids))!=len(ids) or seen.intersection(ids):
                raise RuntimeError('Repeated listing page; uniqueness not established')
            seen.update(ids)
            matches.extend(r for r in rows if r.get('metadata',{}).get('title')==manager.TITLE)
            print('Account lookup page',page,'items',len(rows),'editorial matches',len(matches),flush=True)
            if len(rows)<100: return matches
        raise RuntimeError('Incomplete account listing; no new record authorized')
    def request(self,path,method='GET',data=None,**kwargs):
        if method=='GET':
            if path.startswith('/deposit/depositions?') and 'q=' in path: return self.own_matching_deposits()
            return self.safe_read(lambda:self.client.request(path,method,data,**kwargs))
        print('Zenodo write:',method,path,flush=True)
        return self.client.request(path,method,data,**kwargs)
    def download_public(self,url): return self.safe_read(lambda:self.client.download_public(url))

def main():
    done=manager.BATCH/'links-status.json'
    if done.exists() and manager.read(done).get('state')=='SIX_DOI_METADATA_LINKS_VERIFIED':
        print('Publication and links already verified; no retry needed',flush=True)
        return
    attempt=manager.BATCH/'publication-attempt.json'
    state={'attempted_at':datetime.now(timezone.utc).isoformat(),'state':'IN_PROGRESS',
           'workflow_run_id':manager.os.environ.get('GITHUB_RUN_ID'),'source_commit':manager.SOURCE_COMMIT}
    manager.write(attempt,state)
    try:
        probe=ReadRetry(original_factory())
        known=probe.request('/deposit/depositions/22830239')
        manager.validate_identity(known,22830239,'2.1')
        print('Known published record reachable; preflight made no changes',flush=True)
        manager.zenodo=lambda:ReadRetry(original_factory())
        manager.publish()
        state['state']='PUBLICATION_AND_SIX_LINKS_COMPLETE'
    except Exception as exc:
        code=getattr(exc,'code',None)
        state.update(state='BLOCKED_REMOTE_SERVICE' if code in {429,500,502,503,504} else 'INCOMPLETE_REQUIRES_INSPECTION',
                     error_type=type(exc).__name__,http_status=code)
        state['creation_intent_exists']=(manager.BATCH/'create-intent.json').exists()
        state['record_checkpoint_exists']=(manager.BATCH/'deposit.json').exists()
        state['verified_metadata_links']=sum('result' in manager.read(p) for p in (manager.BATCH/'metadata-links').glob('*.json'))
        print('Editorial publication incomplete:',state['state'],'HTTP',code,flush=True)
        raise
    finally:
        state['finished_at']=datetime.now(timezone.utc).isoformat()
        manager.write(attempt,state)

if __name__=='__main__': main()
