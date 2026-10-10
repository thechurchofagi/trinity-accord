#!/usr/bin/env python3
"""Stage exactly the applied CTD overlay and prepare a compact Git API payload.

Root runs this only after the guarded overlay apply. This tool performs local
git add --sparse/write-tree, but never fetches, commits, pushes or calls an API.
Known-remote reuse is limited to the two explicitly supplied fetched commits.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

DEFAULT_RELEASE_COMMIT = '20079ae38a190600a7d8dbef5d1340838ed5042a'
REPOSITORY = 'thechurchofagi/trinity-accord'
CHUNK_CHARS = 32000
INLINE_BYTES = 50000
ENV = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_NO_REPLACE_OBJECTS='1', GIT_LITERAL_PATHSPECS='1')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def call(repo, *args, text=False):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=ENV,
                                   text=text, stderr=subprocess.PIPE)


def git_text(repo, *args):
    return call(repo, *args, text=True).strip()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def path_names(data):
    return [x.decode('utf-8') for x in data.split(b'\0') if x]


def safe_path(name):
    require(isinstance(name, str) and '\0' not in name and '\\' not in name,
            'Invalid manifest path')
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == name and name not in ('', '.'),
            'Unsafe or non-canonical manifest path')
    return name


def commit_available(repo, commit):
    try:
        return git_text(repo, 'rev-parse', '--verify', commit + '^{commit}') == commit
    except subprocess.CalledProcessError:
        return False


def pinned_blob_inventory(repo, commit, role):
    require(re.fullmatch(r'[0-9a-f]{40}', commit), 'An exact full SHA-1 commit is required')
    require(commit_available(repo, commit), 'Pinned source commit is not locally fetched')
    require(git_text(repo, 'rev-parse', '--show-object-format') == 'sha1', 'Unexpected Git object format')
    tree = git_text(repo, 'rev-parse', commit + '^{tree}')
    raw = call(repo, 'ls-tree', '-r', '-z', '--full-tree', commit)
    blobs = set()
    entries = 0
    for line in raw.split(b'\0'):
        if not line:
            continue
        meta, _ = line.split(b'\t', 1)
        mode, obj_type, oid = meta.decode('ascii').split()
        entries += 1
        if obj_type == 'blob':
            require(re.fullmatch(r'[0-9a-f]{40}', oid), 'Invalid pinned blob ID')
            blobs.add(oid)
    require(blobs, 'Empty pinned source blob inventory')
    proof = {'role': role, 'repository_full_name': REPOSITORY, 'local_object_repository': str(repo),
             'commit': commit, 'tree': tree, 'tree_entries': entries, 'unique_blob_count': len(blobs),
             'git_ls_tree_bytes': len(raw), 'git_ls_tree_sha256': sha256(raw),
             'remote_identity_basis': 'Exact commit supplied by root after actual remote fetch/readback; no new remote request by this helper.'}
    return blobs, proof


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--manifest', type=Path, required=True, help='The reviewed OVERLAY_MANIFEST.json')
    ap.add_argument('--expected-head', required=True)
    ap.add_argument('--release-repo', type=Path, required=True, help='Fallback local object store for the pinned release commit')
    ap.add_argument('--release-commit', default=DEFAULT_RELEASE_COMMIT)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    repo, release_repo, out = a.repo.resolve(), a.release_repo.resolve(), a.out.resolve()
    require(out != repo and repo not in out.parents and out != release_repo and release_repo not in out.parents,
            'Transport output must be outside both repositories')
    require(not out.exists(), 'Use a new output directory; preserve prior transport evidence')
    require(git_text(repo, 'rev-parse', 'HEAD') == a.expected_head,
            'Research HEAD changed; reconcile and regenerate the overlay before staging')
    require(not call(repo, 'diff', '--cached', '--name-only', '-z'),
            'Pre-existing staged files: refuse a mixed commit')
    manifest_bytes = a.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    require(manifest.get('schema') == 'ctd-research-sync-overlay/1' and
            manifest.get('expected_research_head') == a.expected_head,
            'Manifest is not bound to this research HEAD')
    entries = manifest['files']
    paths = [safe_path(f['path']) for f in entries]
    require(paths and len(paths) == len(set(paths)), 'Duplicate or empty allowed manifest paths')
    expected = {f['path']: f['after'] for f in entries}
    base_blobs, base_proof = pinned_blob_inventory(repo, a.expected_head, 'current_research_remote_head')
    release_store = repo if commit_available(repo, a.release_commit) else release_repo
    release_blobs, release_proof = pinned_blob_inventory(release_store, a.release_commit,
                                                       'verified_CTD_release_remote_commit')
    known = base_blobs | release_blobs
    base_tree = base_proof['tree']
    rows, original_bytes, omitted_bytes = [], 0, 0
    for name in sorted(paths):
        p = repo / name
        require(p.is_file() and not p.is_symlink() and repo in p.resolve().parents,
                'Allowed file is missing, symlinked or escaped: ' + name)
        data = p.read_bytes()
        digest = sha256(data)
        require({'bytes': len(data), 'sha256': digest} == expected[name],
                'Applied file differs from reviewed manifest after-hash: ' + name)
        oid = blob_sha(data)
        row = {'path': name, 'bytes': len(data), 'sha256': digest, 'git_sha': oid}
        original_bytes += len(data)
        if oid in known:
            row['reuse'] = True
            row['reuse_source'] = 'research_head' if oid in base_blobs else 'release_commit'
            # Intentionally no content, inline or encoding property on reused blobs.
            omitted_bytes += len(data)
        else:
            try:
                content = data.decode('utf-8')
                inline = len(data) <= INLINE_BYTES
            except UnicodeDecodeError:
                content, inline = None, False
            row.update({'reuse': False, 'inline': inline,
                        'content': content if inline else base64.b64encode(data).decode('ascii'),
                        'encoding': 'utf-8' if inline else 'base64'})
        rows.append(row)
    # Intentional unstaged overlay changes are allowed. Nothing outside the exact
    # manifest path list is added. Recheck the two index/HEAD guards immediately.
    require(git_text(repo, 'rev-parse', 'HEAD') == a.expected_head, 'HEAD changed before staging')
    require(not call(repo, 'diff', '--cached', '--name-only', '-z'), 'Index changed before staging')
    subprocess.run(['git', '-C', str(repo), 'add', '--sparse', '--', *paths], env=ENV, check=True)
    staged = path_names(call(repo, 'diff', '--cached', '--name-only', '-z'))
    require(len(staged) == len(paths) and set(staged) == set(paths),
            'Staged path set differs from the exact allowed manifest; reconcile the index')
    index = {}
    for line in call(repo, 'ls-files', '--stage', '-z', '--', *paths).split(b'\0'):
        if not line:
            continue
        meta, raw_name = line.split(b'\t', 1)
        mode, oid, stage = meta.decode('ascii').split()
        name = raw_name.decode('utf-8')
        require(stage == '0' and name not in index, 'Unmerged or duplicate index entry')
        require(mode in ('100644', '100755'), 'Only regular-file index modes are supported')
        index[name] = (mode, oid)
    require(set(index) == set(paths), 'Index did not return exactly the allowed paths')
    for row in rows:
        mode, oid = index[row['path']]
        require(oid == row['git_sha'],
                'Git filters/autocrlf changed staged bytes; do not transport raw working bytes: ' + row['path'])
        row['mode'] = mode  # Target index mode, never a source-file mode.
        require(sha256((repo / row['path']).read_bytes()) == row['sha256'],
                'Working file changed during staging')
    expected_tree = git_text(repo, 'write-tree')
    require(re.fullmatch(r'[0-9a-f]{40}', expected_tree), 'Invalid staged tree SHA')
    written = {}
    for line in call(repo, 'ls-tree', '-r', '-z', '--full-tree', expected_tree, '--', *paths).split(b'\0'):
        if not line:
            continue
        meta, raw_name = line.split(b'\t', 1)
        mode, obj_type, oid = meta.decode('ascii').split()
        name = raw_name.decode('utf-8')
        require(obj_type == 'blob' and name not in written, 'Unexpected object in immutable written tree')
        written[name] = (mode, oid)
    require(set(written) == set(paths), 'Written tree is missing an exact allowed file')
    require(all(written[r['path']] == (r['mode'], r['git_sha']) for r in rows),
            'Written immutable tree differs from transport rows; concurrent index change requires reconciliation')
    tree_paths = path_names(call(repo, 'diff-tree', '-r', '--no-commit-id', '--name-only', '-z',
                                base_tree, expected_tree))
    require(set(tree_paths) == set(paths), 'Written tree changes paths outside the allowed manifest')
    require(git_text(repo, 'rev-parse', 'HEAD') == a.expected_head, 'HEAD changed while staging')
    require(set(path_names(call(repo, 'diff', '--cached', '--name-only', '-z'))) == set(paths),
            'Index changed while preparing payload')
    payload = {'repository_full_name': REPOSITORY, 'head': a.expected_head, 'base_tree': base_tree,
               'expected_tree': expected_tree, 'files': rows}
    serial = json.dumps(payload, ensure_ascii=True, separators=(',', ':'))
    encoded = serial.encode('ascii')
    out.mkdir(parents=True)
    (out / 'payload.json').write_bytes(encoded)
    chunks = []
    for i, start in enumerate(range(0, len(serial), CHUNK_CHARS)):
        part = serial[start:start + CHUNK_CHARS]
        f = out / ('chunk-%04d.txt' % i)
        data = part.encode('ascii')
        f.write_bytes(data)
        chunks.append({'path': str(f), 'chars': len(part), 'sha256': sha256(data)})
    require(b''.join(Path(c['path']).read_bytes() for c in chunks) == encoded,
            'Chunk reassembly differs from the exact ASCII payload')
    reuse_count = sum(r['reuse'] for r in rows)
    meta = {'head': a.expected_head, 'base_tree': base_tree, 'expected_tree': expected_tree,
            'file_count': len(rows), 'payload_chars': len(serial), 'payload_sha256': sha256(encoded),
            'chunk_count': len(chunks), 'chunks': chunks,
            'files': [{k: v for k, v in r.items() if k != 'content'} for r in rows],
            'reuse_count': reuse_count, 'transmitted_file_count': len(rows) - reuse_count,
            'original_file_bytes': original_bytes, 'reused_file_bytes_omitted': omitted_bytes,
            'new_file_bytes_serialized': original_bytes - omitted_bytes,
            'mode_counts': {m: sum(r['mode'] == m for r in rows) for m in sorted({r['mode'] for r in rows})},
            'source_overlay_manifest': str(a.manifest.resolve()), 'source_overlay_manifest_sha256': sha256(manifest_bytes),
            'known_remote_blob_provenance': [base_proof, release_proof],
            'source_tree_lookup_includes_sparse_unchecked_out_paths': True,
            'git_mutations_performed': ['add --sparse exact manifest paths', 'write-tree'],
            'network_requests_performed': False, 'commit_or_push_performed': False,
            'consumer_contract': 'Check reuse first and reference git_sha directly; otherwise retain inline/encoding/content semantics. Use each target mode. Concatenate all ASCII chunks before JSON.parse.'}
    (out / 'manifest.json').write_text(json.dumps(meta, ensure_ascii=True, indent=2) + '\n', encoding='ascii')
    print(json.dumps({k: v for k, v in meta.items() if k not in ['chunks', 'files', 'known_remote_blob_provenance']},
                     ensure_ascii=True))


if __name__ == '__main__':
    main()
