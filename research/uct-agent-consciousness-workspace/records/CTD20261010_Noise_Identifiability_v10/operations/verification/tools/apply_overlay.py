#!/usr/bin/env python3
"""Validate a prepared CTD overlay; write locally only with explicit --apply.

No fetch, checkout, commit, push, remote call, Library or publication operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def require(ok, message):
    if not ok:
        raise ValueError(message)


def md(path):
    b = path.read_bytes()
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--prepared', type=Path, required=True)
    p.add_argument('--apply', action='store_true', help='Perform the guarded local file writes after validation')
    args = p.parse_args()
    repo, prepared = args.repo.resolve(), args.prepared.resolve()
    manifest = json.loads((prepared / 'OVERLAY_MANIFEST.json').read_text())
    require(manifest['schema'] == 'ctd-research-sync-overlay/1', 'Wrong overlay schema')
    require(git(repo, 'rev-parse', 'HEAD') == manifest['expected_research_head'],
            'Research HEAD changed; fetch/reconcile normally, then reprepare the overlay')
    require(not git(repo, 'status', '--porcelain'), 'Working tree is not clean; do not mix updates')
    ws = Path('research/uct-agent-consciousness-workspace')
    require(manifest['workspace'] == str(ws), 'Unexpected workspace root')
    record = ws / 'records/CTD20261010_Noise_Identifiability_v10'
    pub = ws / 'publication' / manifest['coverage_version']
    require(not (repo / record).exists(), 'Record appeared after preparation; reconcile')
    require(not (repo / pub).exists(), 'Coverage version is now occupied; reprepare using next free version')
    require(not git(repo, 'ls-tree', '-r', '--name-only', 'HEAD', '--', str(record)),
            'Record already exists in the sparse Git tree; reconcile')
    require(not git(repo, 'ls-tree', '-r', '--name-only', 'HEAD', '--', str(pub)),
            'Coverage version exists in the sparse Git tree; reprepare')
    allowed_old = {str(ws / n) for n in [
        'PUBLICATION_COVERAGE.json', 'CURRENT_STATE.json', 'RESEARCH_REGISTRY.json',
        'RESEARCH_SESSION_LOG_INDEX.json', 'UCT_FORMAL_GRAPH_MODULES.json',
        'AGENTS.md', 'MEMORY.md', 'HANDOFF.md', 'MASTER_INDEX.md', 'CHANGELOG.md',
        'RESEARCH_MASTER_GUIDE.md']}
    paths = [f['path'] for f in manifest['files']]
    require(len(paths) == len(set(paths)), 'Duplicate planned file')
    writes = []
    for item in manifest['files']:
        rel = Path(item['path'])
        require(not rel.is_absolute() and '..' not in rel.parts, 'Unsafe manifest path')
        dst, src = repo / rel, prepared / 'overlay' / rel
        require(repo in dst.resolve().parents and (prepared / 'overlay') in src.resolve().parents,
                'Manifest path escaped through a symlink')
        require(src.is_file() and md(src) == item['after'], 'Overlay file hash mismatch: ' + str(rel))
        if item['before'] is None:
            require(record in rel.parents or pub in rel.parents, 'Unapproved new path: ' + str(rel))
            require(not dst.exists(), 'New file already exists: ' + str(rel))
        else:
            require(str(rel) in allowed_old, 'Existing non-navigation file would be overwritten')
            require(dst.is_file() and md(dst) == item['before'], 'Old file changed: ' + str(rel))
        writes.append((src, dst, item))
    require(git(repo, 'rev-parse', 'HEAD') == manifest['expected_research_head'] and
            not git(repo, 'status', '--porcelain'), 'Repository changed during validation')
    if not args.apply:
        print(json.dumps({'state': 'DRY_RUN_VALIDATED_NO_WRITES', 'files': len(writes),
                          'expected_head': manifest['expected_research_head'],
                          'coverage_version': manifest['coverage_version'],
                          'doi': manifest['publication_doi']}))
        return
    completed = []
    try:
        for src, dst, item in writes:
            # Recheck each destination immediately before its atomic replacement.
            require((not dst.exists()) if item['before'] is None else md(dst) == item['before'],
                    'Destination changed during apply: ' + str(dst))
            dst.parent.mkdir(parents=True, exist_ok=True)
            temporary = dst.with_name(dst.name + '.ctd-sync.tmp')
            require(not temporary.exists(), 'Unexpected previous transient apply file')
            temporary.write_bytes(src.read_bytes())
            temporary.replace(dst)
            require(md(dst) == item['after'], 'Local write failed hash verification')
            completed.append(item['path'])
    except Exception as exc:
        # Do not reset or roll back files that another process may have changed.
        print(json.dumps({'state': 'PARTIAL_LOCAL_APPLY_REQUIRES_RECONCILIATION',
                          'completed_paths': completed, 'error_type': type(exc).__name__}))
        raise
    receipt = {'state': 'LOCAL_OVERLAY_APPLIED_HASH_VERIFIED_NOT_COMMITTED',
               'expected_head': manifest['expected_research_head'], 'files_written': len(completed),
               'coverage_version': manifest['coverage_version'], 'doi': manifest['publication_doi'],
               'git_mutations_performed': False, 'external_mutations_performed': False,
               'note': 'Root must inspect the diff, commit normally, and verify the actual remote readback.'}
    (prepared / 'LOCAL_APPLY_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
