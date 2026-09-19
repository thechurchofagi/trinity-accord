#!/usr/bin/env python3
"""Use direct record reads and complete own-record pagination; retry reads only.

A failed/partial lookup never becomes an empty lookup authorizing creation.
No write is automatically retried and no credentials or unrelated records logged.
"""
import importlib.util
from pathlib import Path
import time
import urllib.error

spec = importlib.util.spec_from_file_location('editorial_manager', Path(__file__).with_name('manage.py'))
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)
original_factory = manager.zenodo

class ReadRetry:
    def __init__(self, client): self.client = client
    def safe_read(self, callback, attempts=3):
        for attempt in range(attempts):
            try: return callback()
            except urllib.error.HTTPError as exc:
                if exc.code not in {429,500,502,503,504} or attempt == attempts - 1: raise
                print('Transient Zenodo read failure; retry',attempt+1,'HTTP',exc.code,flush=True)
                time.sleep(2 ** (attempt + 1))
            except (TimeoutError, urllib.error.URLError):
                if attempt == attempts - 1: raise
                time.sleep(2 ** (attempt + 1))
    def own_matching_deposits(self):
        # The former quoted full-text query repeatedly returned server errors.
        # Enumerate the account's actual records without that query, to completion.
        matches = []
        seen = set()
        for page in range(1,41):
            rows = self.safe_read(lambda:self.client.request('/deposit/depositions?size=100&page='+str(page)),attempts=2)
            if not isinstance(rows,list): raise RuntimeError('Unexpected own-record listing shape')
            ids = [r.get('id') for r in rows]
            if len(set(ids)) != len(ids) or seen.intersection(ids):
                raise RuntimeError('Repeated listing page; cannot establish uniqueness')
            seen.update(ids)
            matches.extend(r for r in rows if r.get('metadata',{}).get('title') == manager.TITLE)
            print('Own-record lookup page',page,'items',len(rows),'matching editorial records',len(matches),flush=True)
            if len(rows) < 100: return matches
        raise RuntimeError('Own-record listing exceeded bound; no creation')
    def request(self, path, method='GET', data=None, **kwargs):
        if method == 'GET':
            if path.startswith('/deposit/depositions?') and 'q=' in path:
                return self.own_matching_deposits()
            return self.safe_read(lambda:self.client.request(path,method,data,**kwargs))
        print('Zenodo write:',method,path,flush=True)
        try:
            return self.client.request(path,method,data,**kwargs)
        except urllib.error.HTTPError as exc:
            if exc.code in {400,409,422}:
                print('Validation response:',exc.code,exc.read(1600).decode('utf-8','replace'),flush=True)
            raise
    def download_public(self, url):
        return self.safe_read(lambda:self.client.download_public(url))

if __name__ == '__main__':
    probe = ReadRetry(original_factory())
    known = probe.safe_read(lambda:probe.client.request('/deposit/depositions/22830239'),attempts=2)
    manager.validate_identity(known,22830239,'2.1')
    print('Existing published record is reachable; no changes made by preflight',flush=True)
    manager.zenodo = lambda:ReadRetry(original_factory())
    manager.publish()
