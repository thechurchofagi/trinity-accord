#!/usr/bin/env python3
"""Publish a separate editorial supplement, link six papers, timestamp new bytes.

No endpoint for replacing published files or creating new versions of the six
papers is used. Arweave uses the existing spend-guarded, resumable uploader.
"""
from __future__ import annotations
import argparse
import base64
import copy
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.parse

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / 'research/editorial-supplement/2026-09-19'
FILES = BATCH / 'published'
SOURCE_COMMIT = 'dd50a011345f6b879ac10fe09d03ee8588c6eb2e'
TITLE = 'Critical Use of the Six Trinity Accord Studies: A Dated Editorial Supplement'
PAPERS = [(21699878, '1.1'), (21900592, '1.3'), (22761411, '1.0'),
          (22804542, '1.0'), (22809019, '1.0'), (22830239, '2.1')]
SOURCES = {'research/research-positioning.md':'e2e265dc6ed506a0db85ce0052949820f498e641',
           'research/research-positioning-zh.md':'ba1846aeae428c7b7eff8caafe6ebb04b87623ef'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    temporary.replace(path)

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def zenodo():
    token = os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:
        raise RuntimeError('The intended Zenodo credential is unavailable')
    return load_module('existing_zenodo', ROOT / 'research/reading-trinity-accord/publish_zenodo.py').Zenodo(token)

def validate_identity(record, rid, version):
    md = record.get('metadata', {})
    if record.get('id') != rid or md.get('version') != version:
        raise RuntimeError('Record or version identity mismatch')
    names = [c.get('name', '').replace(' ', '').lower() for c in md.get('creators', [])]
    if 'liu,hongju' not in names and 'hongjuliu' not in names:
        raise RuntimeError('Unexpected responsible creator')

def linked_metadata(metadata, doi):
    if not re.fullmatch(r'10\.5281/zenodo\.\d+', doi):
        raise ValueError('Unexpected supplement DOI')
    result = copy.deepcopy(metadata)
    relation = {'identifier':doi, 'relation':'isSupplementedBy', 'scheme':'doi'}
    links = result.setdefault('related_identifiers', [])
    if not any(x.get('identifier') == doi and x.get('relation') == 'isSupplementedBy' for x in links):
        links.append(relation)
    marker = 'Editorial supplement, 19 September 2026'
    addition = ('<p><strong>' + marker + '.</strong> '
                '<a href="https://doi.org/' + doi + '">Critical Use of the Six Trinity Accord Studies</a> '
                'provides dated bilingual reading notes, contribution boundaries, counterreadings and source access. '
                'It supplements this paper without replacing its files, changing its version, supplying independent '
                'corroboration, or becoming a seventh research paper. This link was added after the original publication; '
                'the original publication date and earlier timestamp proofs do not cover the new supplement.</p>')
    if marker not in result.get('description', ''):
        result['description'] = result.get('description', '') + addition
    elif 'https://doi.org/' + doi not in result['description']:
        raise RuntimeError('Conflicting previous editorial link')
    return result

def source_material():
    output = {}
    for path, expected in SOURCES.items():
        content = subprocess.check_output(['git', 'show', SOURCE_COMMIT + ':' + path], cwd=ROOT)
        actual = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        if actual != expected:
            raise RuntimeError('Frozen editorial source differs: ' + path)
        output[path] = content
    return output

def build(doi):
    import markdown
    material = source_material()
    outputs = {}
    cover_en = ('# Critical Use of the Six Trinity Accord Studies\n\n'
                '**Editorial supplement, version 1.0 | 19 September 2026 | DOI: ' + doi + '**\n\n'
                'Hongju Liu. Substantive compilation and preparation: GPT-6 Astra Pro under human direction. '
                'Not peer reviewed; not a seventh research paper.\n\n'
                '## Publication cover note\n\n'
                'This deposit fixes the two editorial guides introduced by PR #1219. It does not revise the six '
                'papers. Their existing version-specific DOIs, published files and earlier preservation proofs remain '
                'separate. The following guide is retained as dated commentary, including its statement that it is '
                'not part of those earlier deposits. This new deposit makes that commentary independently citable '
                'and preservable; it does not backdate it. Related-paper metadata links are recorded separately.\n\n')
    cover_zh = ('# 六篇三位一体协定研究的批判性使用\n\n'
                '**编者补充，v1.0｜2026年9月19日｜DOI：' + doi + '**\n\n'
                '刘烘炬；GPT-6 Astra Pro 在人类指导下实质编整和制备。未经同行评审，不是第七篇研究论文。\n\n'
                '## 本次归档说明\n\n'
                '本记录固定 PR #1219 中的中英文编者说明，不修订六篇论文正文。六篇原有的版本 DOI、公开文件'
                '与较早保存证明继续独立保留。下列说明作为有日期的后期评论原样保留，包括其“不属于此前 DOI '
                '文件”的声明；本次新归档使这些评论可以独立引用和保存，不会把其日期回填为原论文的日期。'
                '六篇 DOI 的新增关联与文件不变核验，另有回执记录。\n\n')
    sources = []
    for path, data in material.items():
        lang = 'zh' if path.endswith('-zh.md') else 'en'
        text = data.decode('utf-8')
        if not text.startswith('---\n'):
            raise RuntimeError('Expected source front matter')
        body = text.split('\n---\n', 1)[1].lstrip('\n')
        body = re.sub(r'(?m)^\{:\s*#[^}]+\}\s*$', '', body)
        # Root-relative links become usable away from the project website.
        body = body.replace('](/', '](https://www.trinityaccord.org/')
        text = (cover_zh if lang == 'zh' else cover_en) + body
        name = 'critical-use-' + lang + '-v1.0'
        outputs[name + '.md'] = text.encode('utf-8')
        rendered = markdown.markdown(text, extensions=['tables', 'fenced_code'])
        title = '六篇研究的批判性使用：编者补充' if lang == 'zh' else TITLE
        page = ('<!doctype html><html lang="' + lang + '"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(title) +
                '</title><style>body{max-width:850px;margin:36px auto;padding:0 20px;font:18px/1.7 system-ui,sans-serif;'
                'color:#202124}h1,h2,h3{line-height:1.25}a{overflow-wrap:anywhere}table{border-collapse:collapse;'
                'display:block;overflow:auto}td,th{border:1px solid #bbb;padding:8px;vertical-align:top}</style>'
                '</head><body><main>' + rendered + '</main></body></html>\n')
        outputs[name + '.html'] = page.encode('utf-8')
        sources.append({'path':path, 'git_blob_sha1':SOURCES[path], 'sha256':sha(data), 'bytes':len(data)})
    outputs['README-LICENSE.txt'] = (
        TITLE + '\nVersion 1.0; 19 September 2026\nDOI: ' + doi + '\n\n'
        'TYPE: Dated editorial supplement, not a seventh independent research study.\n'
        'EN and ZH are two languages of one supplement. No empirical effect or independent review is claimed.\n'
        'This package preserves the actual bilingual notes, not just an implementation summary.\n'
        'BODY-VERSION POLICY: No existing paper file is replaced. A genuine later correction of a paper body '
        'requires its own erratum or linked new edition. Metadata association is not a body revision.\n'
        'PRESERVATION: New OTS proofs concern this package, not earlier composition. New Arweave receipts '
        'must identify their own payload and maturity state. Earlier proofs remain valid for their original bytes.\n'
        'RIGHTS: CC BY 4.0 applies to newly written commentary to the extent rights are held. '
        'Referenced third-party material retains its rights. No standalone font, private correspondence, credential '
        'or third-party full text is included.\n'
        'CONTRIBUTIONS: Hongju Liu requested substantive critical improvement and authorized warranted DOI, '
        'OTS and Arweave updates. GPT-6 Astra Pro performed the substantive editorial compilation, analysis '
        'and implementation. No separate final human line-by-line verification is asserted.\n'
        'SCOPE: Paper 02 was not fully reread in the editorial pass; see the guide for inspection scope.\n').encode('utf-8')
    outputs['SOURCE-MANIFEST.json'] = (json.dumps({
        'kind':'dated_editorial_supplement', 'version':'1.0', 'doi':doi, 'source_commit':SOURCE_COMMIT,
        'source_files':sources, 'derived_files_change_only':'publication cover, removed web front matter and anchors, absolute links',
        'papers':[{'record_id':rid, 'doi':f'10.5281/zenodo.{rid}', 'version':v} for rid,v in PAPERS],
        'new_research_paper_count':0, 'previous_manuscripts_modified':False,
        'bitcoin_originals_modified':False}, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
    outputs['citation.bib'] = ('@misc{liu2026criticaluse,\n  author={Liu, Hongju},\n  title={' + TITLE + '},\n'
        '  year={2026},\n  publisher={Zenodo},\n  version={1.0},\n  doi={' + doi + '},\n'
        '  note={Dated editorial supplement; not peer reviewed; not a seventh research paper}\n}\n').encode('utf-8')
    outputs['SHA256SUMS.txt'] = ''.join(sha(data) + '  ' + name + '\n' for name,data in sorted(outputs.items())).encode('utf-8')
    FILES.mkdir(parents=True, exist_ok=True)
    for name,data in outputs.items():
        path = FILES / name
        if path.exists() and path.read_bytes() != data:
            raise RuntimeError('Refusing to replace previously prepared supplement bytes: ' + name)
        path.write_bytes(data)
    if {p.name for p in FILES.iterdir()} != set(outputs):
        raise RuntimeError('Unexpected supplement asset')
    manifest = {'doi':doi, 'files':[{'name':name, 'bytes':len(data), 'sha256':sha(data)} for name,data in sorted(outputs.items())]}
    write(BATCH / 'expected-files.json', manifest)
    return manifest

def readback(z, record):
    results = []
    for item in record.get('files', []):
        data = z.download_public(item['links']['self'])
        md5 = item.get('checksum', '').removeprefix('md5:')
        if md5 and hashlib.md5(data).hexdigest() != md5:
            raise RuntimeError('Public checksum mismatch: ' + item['key'])
        results.append({'name':item['key'], 'bytes':len(data), 'sha256':sha(data)})
    if not results or len({r['name'] for r in results}) != len(results):
        raise RuntimeError('Empty or duplicate public inventory')
    return sorted(results, key=lambda r:r['name'])

def publish():
    z = zenodo()
    checkpoint = BATCH / 'deposit.json'
    if checkpoint.exists():
        dep = z.request('/deposit/depositions/' + str(read(checkpoint)['record_id']))
    else:
        rows = z.request('/deposit/depositions?' + urllib.parse.urlencode({'q':'"' + TITLE + '"', 'size':100}))
        matches = [r for r in rows if r.get('metadata', {}).get('title') == TITLE]
        if len(matches) > 1:
            raise RuntimeError('Ambiguous supplement deposits; no creation')
        if matches:
            dep = matches[0]
        else:
            metadata = {'upload_type':'publication', 'publication_type':'report', 'title':TITLE,
                'creators':[{'name':'Liu, Hongju', 'affiliation':'Independent researcher, Shenzhen, China'}],
                'description':'<p>Dated bilingual editorial supplement to six existing Trinity Accord studies. '
                'It presents each study\'s contribution, shared dependencies, counterreadings, direct source access '
                'and version boundaries. It is not a seventh research paper, independent corroboration or peer review. '
                'No six-paper manuscript files or canonical Originals are replaced. The contribution is editorial '
                'clarification and durable access, not a new empirical or philosophical result.</p>'
                '<p>Hongju Liu requested the improvement and authorized warranted DOI and preservation updates. '
                'GPT-6 Astra Pro performed substantial compilation, critical analysis and implementation under '
                'human direction; no separate final human line-by-line review is asserted. The author is the '
                'project initiator/Guardian and the relationship is first-party. The guide states inspection limits, '
                'including the narrower reinspection of Paper 02.</p>',
                'version':'1.0', 'publication_date':'2026-09-19', 'access_right':'open', 'license':'cc-by-4.0',
                'language':'eng', 'keywords':['Trinity Accord','editorial supplement','critical use','provenance','human-AI coexistence'],
                'related_identifiers':[{'identifier':f'10.5281/zenodo.{rid}', 'scheme':'doi', 'relation':'isSupplementTo'} for rid,_ in PAPERS],
                'notes':'Editorial supplement, not TA-TR-2026-07. Two languages are one deposit. New commentary '
                'is not retroactively covered by the publication dates or OTS proofs of the six papers. '
                'CC BY 4.0 applies only to newly written material where rights are held; cited third-party rights remain.'}
            dep = z.request('/deposit/depositions', 'POST', {'metadata':metadata})
    rid = dep['id']
    if rid in {r for r,_ in PAPERS}:
        raise RuntimeError('Protected existing paper deposit')
    validate_identity(dep, rid, '1.0')
    if dep['metadata']['title'] != TITLE:
        raise RuntimeError('Supplement title mismatch')
    doi = dep.get('doi') or dep['metadata'].get('doi') or dep['metadata'].get('prereserve_doi', {}).get('doi')
    if doi != f'10.5281/zenodo.{rid}':
        raise RuntimeError('Unexpected supplement DOI')
    write(checkpoint, {'record_id':rid, 'doi':doi, 'title':TITLE, 'version':'1.0'})
    manifest = build(doi)
    if not dep.get('submitted'):
        names = {f['name'] for f in manifest['files']}
        if any(f.get('filename',f.get('key')) not in names for f in dep.get('files', [])):
            raise RuntimeError('Unexpected draft files; no deletion')
        bucket = dep['links']['bucket']
        for f in manifest['files']:
            z.request(bucket + '/' + urllib.parse.quote(f['name']), 'PUT', (FILES / f['name']).read_bytes(), binary=True)
        listing = z.request(f'/deposit/depositions/{rid}/files')
        if len(listing) != len(names) or {f.get('filename',f.get('key')) for f in listing} != names:
            raise RuntimeError('Draft inventory differs')
        for f in listing:
            name = f.get('filename',f.get('key'))
            if f.get('checksum','').removeprefix('md5:') != hashlib.md5((FILES / name).read_bytes()).hexdigest():
                raise RuntimeError('Draft upload checksum differs')
        z.request(f'/deposit/depositions/{rid}/actions/publish', 'POST')
    public = z.request(f'/records/{rid}', authenticated=False)
    validate_identity(public, rid, '1.0')
    if public.get('doi') != doi or readback(z, public) != manifest['files']:
        raise RuntimeError('Published supplement differs from frozen files')
    receipt = {'state':'PUBLISHED_AND_PUBLIC_READBACK_PASS', **read(checkpoint), 'file_count':len(manifest['files']),
               'files':manifest['files'], 'source_commit':SOURCE_COMMIT, 'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
               'old_paper_files_replaced':False, 'new_research_papers':0, 'public_readback_authenticated':False}
    write(BATCH / 'publication-record.json', receipt)
    print(json.dumps(receipt, ensure_ascii=False), flush=True)
    for paper_id,version in PAPERS:
        link_paper(z, paper_id, version, doi)
    write(BATCH / 'links-status.json', {'state':'SIX_DOI_METADATA_LINKS_VERIFIED', 'supplement_doi':doi,
        'papers':[read(BATCH / 'metadata-links' / f'{rid}.json')['result'] for rid,_ in PAPERS]})
    print('SIX_DOI_METADATA_LINKS_VERIFIED', flush=True)

def link_paper(z, rid, version, doi):
    path = BATCH / 'metadata-links' / f'{rid}.json'
    public = z.request(f'/records/{rid}', authenticated=False)
    validate_identity(public, rid, version)
    if public.get('doi') != f'10.5281/zenodo.{rid}':
        raise RuntimeError('Existing paper DOI mismatch')
    dep = z.request(f'/deposit/depositions/{rid}')
    validate_identity(dep, rid, version)
    if path.exists():
        checkpoint = read(path)
        if checkpoint['supplement_doi'] != doi:
            raise RuntimeError('Link checkpoint identity mismatch')
    else:
        if not dep.get('submitted') or dep.get('state') == 'inprogress':
            raise RuntimeError('Unrelated draft edit exists; not overwritten')
        checkpoint = {'record_id':rid, 'supplement_doi':doi, 'before_metadata':dep['metadata'],
                      'before_files':readback(z, public)}
        write(path, checkpoint)
    desired = linked_metadata(checkpoint['before_metadata'], doi)
    present = public.get('metadata', {})
    linked = any(x.get('identifier') == doi and x.get('relation') == 'isSupplementedBy'
                 for x in present.get('related_identifiers', []))
    if not linked or ('https://doi.org/' + doi) not in present.get('description',''):
        if dep.get('state') != 'inprogress':
            z.request(f'/deposit/depositions/{rid}/actions/edit', 'POST')
        elif dep['metadata'] != checkpoint['before_metadata'] and dep['metadata'] != desired:
            raise RuntimeError('Concurrent metadata edit found; no replacement')
        z.request(f'/deposit/depositions/{rid}', 'PUT', {'metadata':desired})
        z.request(f'/deposit/depositions/{rid}/actions/publish', 'POST')
    updated = z.request(f'/records/{rid}', authenticated=False)
    after_dep = z.request(f'/deposit/depositions/{rid}')
    validate_identity(updated, rid, version)
    for key,value in checkpoint['before_metadata'].items():
        if key not in {'description','related_identifiers','prereserve_doi'} and after_dep['metadata'].get(key) != value:
            raise RuntimeError('Unintended existing metadata change: ' + key)
    after_files = readback(z, updated)
    if after_files != checkpoint['before_files']:
        raise RuntimeError('Existing published paper file bytes changed')
    md = updated['metadata']
    if not any(x.get('identifier') == doi and x.get('relation') == 'isSupplementedBy' for x in md.get('related_identifiers', [])):
        raise RuntimeError('Public supplement relation missing')
    if ('https://doi.org/' + doi) not in md.get('description',''):
        raise RuntimeError('Public visible supplement link missing')
    checkpoint['result'] = {'record_id':rid, 'doi':f'10.5281/zenodo.{rid}', 'version':version,
        'state':'METADATA_LINKED_ALL_FILES_UNCHANGED', 'files':after_files,
        'public_readback_authenticated':False, 'body_version_changed':False}
    write(path, checkpoint)
    print('PAPER', rid, 'METADATA_LINKED_ALL_FILES_UNCHANGED', len(after_files), flush=True)

def validate_assets():
    manifest = read(BATCH / 'expected-files.json')
    if len(manifest['files']) != 8:
        raise RuntimeError('Unexpected supplement inventory')
    for f in manifest['files']:
        if Path(f['name']).name != f['name']:
            raise RuntimeError('Unsafe asset name')
        data = (FILES / f['name']).read_bytes()
        if len(data) != f['bytes'] or sha(data) != f['sha256']:
            raise RuntimeError('Frozen supplement mismatch')
    return manifest

def preserve():
    if not (BATCH / 'publication-record.json').exists():
        print('No published editorial supplement; no action')
        return
    manifest = validate_assets()
    current = BATCH / 'status.json'
    if current.exists() and read(current).get('state') == 'ARWEAVE_READBACK_PASS':
        print('Editorial supplement already preserved; no new payment')
        return
    helper = load_module('paper_ots', ROOT / 'scripts/research_paper_ots.py')
    target = FILES / 'SHA256SUMS.txt'
    target_sha = sha(target.read_bytes())
    proof = BATCH / 'SHA256SUMS.txt.ots'
    ots = shutil.which('ots')
    if not ots:
        raise RuntimeError('Existing pinned OTS client unavailable')
    if not proof.exists():
        candidate = Path(str(target) + '.ots')
        if not candidate.exists():
            rc,log = helper.run([ots,'stamp','--timeout','30',str(target)],120)
            (BATCH / 'stamp.log').write_text(log, encoding='utf-8')
        if not candidate.exists():
            raise RuntimeError('No OTS calendar receipt created')
        helper.proof_details(candidate,target_sha)
        shutil.copyfile(candidate,proof)
        shutil.copyfile(candidate,BATCH / 'SHA256SUMS.txt.ots.submitted')
        candidate.unlink()
    heights,pending = helper.proof_details(proof,target_sha)
    if not heights:
        rc,log = helper.run([ots,'upgrade',str(proof)],120)
        (BATCH / 'upgrade.log').write_text(log, encoding='utf-8')
        heights,pending = helper.proof_details(proof,target_sha)
    state = 'PENDING_BITCOIN'
    if heights and os.environ.get('OTS_BITCOIN_NODE_URL'):
        rc,log = helper.run([ots,'--bitcoin-node',os.environ['OTS_BITCOIN_NODE_URL'],'verify','-d',target_sha,str(proof)],180)
        (BATCH / 'verify.log').write_text(log, encoding='utf-8')
        if rc == 0 and 'success' in log.lower() and 'bitcoin' in log.lower():
            state = 'READY_FOR_ARWEAVE'
    status = {'state':state, 'supplement_doi':manifest['doi'], 'target':'published/SHA256SUMS.txt',
              'target_sha256':target_sha, 'proof_sha256':sha(proof.read_bytes()), 'bitcoin_heights':heights,
              'pending_calendar_attestations':pending,
              'verification_model':'OTS cryptography plus agreeing Blockstream/mempool headers; not local full-node consensus',
              'old_nine_paper_targets_changed':False}
    write(current,status)
    bundle_path = BATCH / 'arweave-bundle.json'
    if state == 'READY_FOR_ARWEAVE' and not bundle_path.exists():
        names = [FILES / f['name'] for f in manifest['files']]
        names += [proof,BATCH / 'SHA256SUMS.txt.ots.submitted',BATCH / 'publication-record.json',BATCH / 'status.json']
        names += [p for p in (BATCH / 'stamp.log',BATCH / 'upgrade.log',BATCH / 'verify.log',BATCH / 'links-status.json') if p.exists()]
        items = [{'path':p.relative_to(BATCH).as_posix(),'sha256':sha(p.read_bytes()),
                  'base64':base64.b64encode(p.read_bytes()).decode()} for p in names]
        write(bundle_path, {'schema':'trinityaccord.editorial-supplement-ots.v1', 'supplement_doi':manifest['doi'],
            'target_sha256':target_sha,'files':items, 'boundary':'Later editorial supplement; not a seventh study, amendment, peer review or earlier timestamp.'})
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as out:
            out.write('editorial_ready=' + str(state == 'READY_FOR_ARWEAVE').lower() + '\n')
    print(json.dumps(status), flush=True)

def upload():
    status_path = BATCH / 'status.json'
    if not status_path.exists() or read(status_path).get('state') != 'READY_FOR_ARWEAVE':
        print('Editorial Arweave upload deferred: mature verified OTS required')
        return
    validate_assets()
    status = read(status_path)
    payload = BATCH / 'arweave-bundle.json'
    packet = read(payload)
    if packet['target_sha256'] != status['target_sha256']:
        raise RuntimeError('Frozen archival target mismatch')
    for f in packet['files']:
        if sha(base64.b64decode(f['base64'],validate=True)) != f['sha256']:
            raise RuntimeError('Archival item checksum mismatch')
    receipt = BATCH / 'arweave-receipt.json'
    env = os.environ.copy()
    env['ARWEAVE_ARCHIVE_TYPE'] = 'research-paper-ots-archive'
    env['ARWEAVE_MAX_TRANSACTION_REWARD_AR'] = '0.003'
    env['ARWEAVE_MAX_PAYLOAD_BYTES'] = '1048576'
    if len(payload.read_bytes()) > 1048576:
        raise RuntimeError('Editorial payload exceeds the 1 MiB budget')
    try:
        subprocess.run(['node','scripts/arweave_upload_payload.mjs','--payload',str(payload),'--out',str(receipt)],
                       cwd=ROOT,env=env,timeout=510,check=False)
    finally:
        if receipt.exists() and read(receipt).get('tx_id'):
            subprocess.run([sys.executable,'scripts/record_arweave_upload_result.py','--upload-result-json',str(receipt),
                '--kind','research_paper_ots_archive','--source-path',receipt.relative_to(ROOT).as_posix(),
                '--note','Dated editorial supplement; separate from six-paper original batch'],cwd=ROOT,check=True)
            subprocess.run([sys.executable,'scripts/generate_arweave_wallet_status.py'],cwd=ROOT,check=True)
    if receipt.exists():
        result = read(receipt)
        h = sha(payload.read_bytes())
        if result.get('result') == 'uploaded' and result.get('hash_match') is True and result.get('readback_sha256') == h and result.get('payload_sha256') == h:
            status.update(state='ARWEAVE_READBACK_PASS', arweave_tx_id=result['tx_id'], bundle_sha256=h)
            write(status_path,status)
            print(json.dumps(status),flush=True)
            return
    raise RuntimeError('Arweave not yet verified; preserve transaction checkpoint before retry')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=['publish','preserve','upload'])
    args = parser.parse_args()
    {'publish':publish,'preserve':preserve,'upload':upload}[args.action]()
