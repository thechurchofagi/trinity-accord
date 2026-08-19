#!/usr/bin/env python3
"""Strict local integrity contract for the Chronicle sidechain DOI package."""
from __future__ import annotations
import hashlib, json, pathlib
from typing import Any

PACKAGE_SCHEMA='trinityaccord.chronicle-sidechain-doi-package.v1'
RIGHTS_SCHEMA='trinityaccord.chronicle-sidechain-doi-rights.v1'
PACKAGE_TITLE='Trinity Accord Chronicle Polygon/Base NFT Evidence Preservation'
ZENODO_LICENSE_ID='other-closed'
CORE_NAMES=(
    'chronicle-sidechain-evidence.tar.gz',
    'chronicle-sidechain-evidence.tar.gz.sha256',
    'chronicle-sidechain-settlement.tar.gz',
    'chronicle-sidechain-settlement.tar.gz.sha256',
    'COLD-RECOVERY-REPORT.json',
    'README.txt',
    'zenodo-metadata.json',
    'checksums.sha256',
    'sidechain-doi-manifest.json',
)

def sha256(path:pathlib.Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def md5(path:pathlib.Path)->str:
    h=hashlib.md5(usedforsecurity=False)
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def read_json(path:pathlib.Path)->dict[str,Any]:
    def pairs(items):
        out={}
        for k,v in items:
            if k in out: raise SystemExit(f'duplicate JSON key {k!r}: {path}')
            out[k]=v
        return out
    try: obj=json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    except Exception as e: raise SystemExit(f'invalid strict JSON {path}: {e}') from e
    if not isinstance(obj,dict): raise SystemExit(f'expected object: {path}')
    return obj

def parse_checksums(path:pathlib.Path)->dict[str,str]:
    out={}
    for line in path.read_text().splitlines():
        if not line.strip(): continue
        try,dummy=(None,None)
        except Exception: pass
        parts=line.split('  ',1)
        if len(parts)!=2 or len(parts[0])!=64: raise SystemExit(f'invalid checksum line: {line!r}')
        digest,name=parts
        if name in out: raise SystemExit(f'duplicate checksum target: {name}')
        out[name]=digest
    return out

def inventory(package_dir:pathlib.Path)->dict[str,dict[str,Any]]:
    return {p.name:{'bytes':p.stat().st_size,'sha256':sha256(p),'md5':md5(p)} for p in sorted(package_dir.iterdir()) if p.is_file()}

def package_identity(inv:dict[str,dict[str,Any]])->str:
    raw=json.dumps({k:{'bytes':v['bytes'],'sha256':v['sha256']} for k,v in sorted(inv.items())},sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(raw).hexdigest()

def verify_package(package_dir:pathlib.Path)->dict[str,Any]:
    if not package_dir.is_dir(): raise SystemExit(f'missing package dir: {package_dir}')
    observed={p.name for p in package_dir.iterdir() if p.is_file()}
    missing=set(CORE_NAMES)-observed
    if missing: raise SystemExit(f'DOI package missing core files: {sorted(missing)}')
    manifest=read_json(package_dir/'sidechain-doi-manifest.json')
    if manifest.get('schema')!=PACKAGE_SCHEMA: raise SystemExit('unsupported sidechain DOI manifest schema')
    published=manifest.get('published_file_names')
    if not isinstance(published,list) or set(published)!=observed: raise SystemExit('published file set does not equal package directory')
    rights=manifest.get('rights_boundary')
    if not isinstance(rights,dict) or rights.get('schema')!=RIGHTS_SCHEMA or rights.get('third_party_rights_are_not_transferred') is not True or rights.get('deposit_grants_no_new_reuse_rights') is not True or rights.get('license_identifier')!=ZENODO_LICENSE_ID:
        raise SystemExit('sidechain DOI rights boundary invalid')
    checks=parse_checksums(package_dir/'checksums.sha256')
    checksum_targets=observed-{'checksums.sha256','sidechain-doi-manifest.json'}
    if set(checks)!=checksum_targets: raise SystemExit('checksums.sha256 target set mismatch')
    for name,digest in checks.items():
        if sha256(package_dir/name)!=digest: raise SystemExit(f'checksum mismatch: {name}')
    entries=manifest.get('files')
    if not isinstance(entries,list): raise SystemExit('manifest files missing')
    by={x.get('name'):x for x in entries if isinstance(x,dict)}
    manifest_targets=observed-{'sidechain-doi-manifest.json'}
    if set(by)!=manifest_targets: raise SystemExit('manifest file inventory mismatch')
    for name,row in by.items():
        p=package_dir/name
        if row.get('bytes')!=p.stat().st_size or row.get('sha256')!=sha256(p): raise SystemExit(f'manifest identity mismatch: {name}')
    meta=read_json(package_dir/'zenodo-metadata.json')
    if meta.get('title')!=PACKAGE_TITLE or meta.get('version')!=manifest.get('archive_id') or meta.get('upload_type')!='dataset' or meta.get('access_right')!='open' or meta.get('license')!=ZENODO_LICENSE_ID or not meta.get('creators'):
        raise SystemExit('Zenodo metadata incomplete/mismatched')
    recovery=read_json(package_dir/'COLD-RECOVERY-REPORT.json')
    if recovery.get('pass') is not True or recovery.get('evidence_offline_pass') is not True or recovery.get('settlement_offline_pass') is not True:
        raise SystemExit('cold recovery report is not PASS')
    inv=inventory(package_dir)
    return {'archive_id':manifest['archive_id'],'manifest':manifest,'metadata':meta,'inventory':inv,'package_identity_sha256':package_identity(inv),'published_file_names':published}
