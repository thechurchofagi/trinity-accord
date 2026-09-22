#!/usr/bin/env python3
"""Recover only the already-created TA14 child; no new-record action exists here.
Zenodo's preserved parent may not expose latest_draft on subsequent GETs.
Inspect authorized draft listings, select exactly one matching concept, and
checkpoint its confirmed identity before returning to the guarded pipeline.
"""
import json
import os
import pipeline as p

def main():
    if (p.ROOT/'state.json').exists() or not (p.ROOT/'creation-intent.json').exists():
        return
    intent=p.load('creation-intent.json')
    if intent.get('parent_record_id')!=p.OLD or intent.get('action')!='newversion':
        raise RuntimeError('Unexpected recovery intent')
    z=p.client()
    old,inventory=p.old_identity(z)
    concept=str(old['conceptrecid'])
    if str(intent.get('conceptrecid'))!=concept:
        raise RuntimeError('Intent concept mismatch')
    matches={}
    for page in range(1,11):
        rows=p.get(z,f'/deposit/depositions?status=draft&size=100&page={page}')
        if not isinstance(rows,list): raise RuntimeError('Unexpected authorized draft response')
        for row in rows:
            if str(row.get('conceptrecid'))==concept and row.get('id')!=p.OLD and not row.get('submitted'):
                rid=p.check_child(row,concept)
                matches[rid]=row
        if len(rows)<100: break
    else:
        raise RuntimeError('Draft pagination incomplete; do not guess a record')
    if len(matches)!=1:
        raise RuntimeError('Expected exactly one same-concept child, found '+str(len(matches)))
    rid=next(iter(matches))
    dep=p.get(z,f'/deposit/depositions/{rid}')
    p.check_child(dep,concept,rid)
    if dep.get('submitted'): raise RuntimeError('Will not edit a published child')
    dep=z.request(f'/deposit/depositions/{rid}','PUT',{'metadata':p.metadata()})
    p.check_child(dep,concept,rid,True)
    doi=dep.get('metadata',{}).get('prereserve_doi',{}).get('doi')
    if doi!=f'10.5281/zenodo.{rid}': raise RuntimeError('Child DOI not confirmed')
    p.save('state.json',{'state':'RESERVED_NOT_PUBLISHED','record_id':rid,'doi':doi,'version':p.VERSION,
                       'title':p.TITLE,'old_record_id':p.OLD,'old_doi':p.OLD_DOI,'conceptrecid':concept,
                       'old_inventory':inventory,'old_pdf_sha256':p.OLD_SHA,'same_concept':True,
                       'old_files_modified':False,'date':p.DATE})
    p.save('draft-recovery.json',{'record_id':rid,'conceptrecid':concept,'same_concept':True,
                                'method':'unique_authorized_unpublished_child','created_new_record':False,
                                'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
    p.persist()
    print(json.dumps({'state':'EXISTING_CHILD_RECOVERED','record_id':rid,'doi':doi}))

if __name__=='__main__': main()
