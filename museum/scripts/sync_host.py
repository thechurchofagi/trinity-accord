#!/usr/bin/env python3
"""Deploy the latest successful main Museum edition; never execute fetched code."""
import concurrent.futures
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import urllib.parse
import urllib.request

REPO = 'thechurchofagi/trinity-accord'
ROOT = Path('/srv/trinity-museum')
MANIFEST = 'data/release-manifest.json'


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Trinity-Museum-Sync/1'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def candidate():
    url = ('https://api.github.com/repos/' + REPO +
           '/actions/workflows/museum-edition.yml/runs?branch=main&event=push&status=success&per_page=5')
    runs = json.loads(fetch(url))['workflow_runs']
    valid = [r for r in runs if r.get('conclusion') == 'success'
             and r.get('event') == 'push' and r.get('head_branch') == 'main'
             and r.get('head_repository', {}).get('full_name') == REPO
             and re.fullmatch(r'[0-9a-f]{40}', r.get('head_sha', ''))]
    if not valid:
        raise RuntimeError('No successful main Museum edition available')
    return max(valid, key=lambda r: r['run_number'])


def inventory(data):
    manifest = json.loads(data)
    if manifest.get('schema') != 'trinity-museum.release.v1':
        raise ValueError('Unknown manifest schema')
    seen = set()
    for row in manifest['files']:
        path = row['path']
        rel = PurePosixPath(path)
        if (rel.is_absolute() or '..' in rel.parts or chr(92) in path or
                str(rel) != path or path in seen or path == MANIFEST or
                not re.fullmatch(r'[0-9a-f]{64}', row['sha256']) or
                not isinstance(row['bytes'], int) or row['bytes'] < 0):
            raise ValueError('Invalid manifest entry')
        seen.add(path)
    if not {'index.html', 'archive.html', 'boot-loader.js'}.issubset(seen):
        raise ValueError('Incomplete museum export')
    return manifest


def switch(root, target):
    temporary = root / 'current.next'
    if temporary.is_symlink():
        temporary.unlink()
    temporary.symlink_to(target)
    os.replace(str(temporary), str(root / 'current'))


def deploy(root, run, download=fetch, health=None):
    base = 'https://raw.githubusercontent.com/' + REPO + '/' + run['head_sha'] + '/museum/dist/'
    data = download(base + MANIFEST)
    manifest = inventory(data)
    current = root / 'current'
    old = current.resolve() if current.is_symlink() else None
    if (current / 'museum' / MANIFEST).is_file() and (current / 'museum' / MANIFEST).read_bytes() == data:
        print('UNCHANGED ' + manifest['edition'], flush=True)
        return False
    releases = root / 'releases'
    releases.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='pending-', dir=str(releases)))
    destination = stage / 'museum'
    destination.mkdir()
    # tempfile defaults to 0700; nginx must be able to traverse the release.
    stage.chmod(0o755)

    def copy(row):
        target = destination / row['path']
        previous = current / 'museum' / row['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        if previous.is_file():
            cached = previous.read_bytes()
            if len(cached) == row['bytes'] and hashlib.sha256(cached).hexdigest() == row['sha256']:
                shutil.copyfile(str(previous), str(target))
                return
        content = download(base + urllib.parse.quote(row['path'], safe='/'))
        if len(content) != row['bytes'] or hashlib.sha256(content).hexdigest() != row['sha256']:
            raise ValueError('Content verification failed: ' + row['path'])
        target.write_bytes(content)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(copy, manifest['files']))
        (destination / MANIFEST).parent.mkdir(parents=True, exist_ok=True)
        (destination / MANIFEST).write_bytes(data)
        receipt = {'source_sha': run['head_sha'], 'workflow_run_id': run['id'],
                   'edition': manifest['edition'], 'manifest_sha256': hashlib.sha256(data).hexdigest()}
        (stage / 'deployment.json').write_text(json.dumps(receipt, indent=2) + chr(10))
        switch(root, stage)
        try:
            if health:
                health(data)
        except Exception:
            if old:
                switch(root, old)
            else:
                current.unlink()
            raise
        print('DEPLOYED ' + json.dumps(receipt), flush=True)
        # Retain active and immediately previous release for rollback.
        keep = {stage.resolve(), old}
        for path in releases.iterdir():
            if (path.name.startswith('pending-') and path.is_dir()
                    and not path.is_symlink() and path.resolve() not in keep):
                shutil.rmtree(str(path))
        return True
    except Exception:
        if current.resolve() != stage.resolve():
            shutil.rmtree(str(stage))
        raise


def health(expected):
    request = urllib.request.Request('http://127.0.0.1:8081/museum/' + MANIFEST)
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.read() != expected:
            raise RuntimeError('Live manifest does not match release')


if __name__ == '__main__':
    ROOT.mkdir(parents=True, exist_ok=True)
    with (ROOT / 'sync.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        deploy(ROOT, candidate(), health=health)
