#!/usr/bin/env python3
"""Retry transient read errors only; never automatically repeat a write request."""
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
    def safe_read(self, callback):
        for attempt in range(4):
            try: return callback()
            except urllib.error.HTTPError as exc:
                if exc.code not in {429,500,502,503,504} or attempt == 3: raise
                print('Transient Zenodo read failure; retry',attempt+1,'HTTP',exc.code,flush=True)
                time.sleep(2 ** (attempt + 1))
            except (TimeoutError, urllib.error.URLError):
                if attempt == 3: raise
                time.sleep(2 ** (attempt + 1))
    def request(self, path, method='GET', data=None, **kwargs):
        if method == 'GET':
            return self.safe_read(lambda:self.client.request(path,method,data,**kwargs))
        return self.client.request(path,method,data,**kwargs)
    def download_public(self, url):
        return self.safe_read(lambda:self.client.download_public(url))

if __name__ == '__main__':
    manager.zenodo = lambda:ReadRetry(original_factory())
    manager.publish()
