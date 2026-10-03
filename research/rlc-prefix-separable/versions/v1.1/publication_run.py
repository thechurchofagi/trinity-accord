#!/usr/bin/env python3
"""Run the frozen publisher with verified handling of Zenodo empty DELETE replies.

This operational compatibility layer does not rebuild or change publication bytes.
An empty successful response is accepted only after same-draft file-list readback
confirms the exact requested inherited file ID is absent.
"""
import json,re,sys,os
import publication as p

class ConfirmedDeleteClient:
    def __init__(self,base,rid):
        if type(rid) is not int or rid in p.PROTECTED or rid<=0:raise RuntimeError('Protected transport identity')
        self.base=base;self.rid=rid
    def request(self,path,method='GET',data=None,**kwargs):
        match=None
        if method=='DELETE':
            match=re.fullmatch(r'/deposit/depositions/([0-9]+)/files/([A-Za-z0-9-]+)',path)
            if not match or int(match[1])!=self.rid:raise RuntimeError('Delete is outside the reserved descendant')
        try:return self.base.request(path,method,data,**kwargs)
        except json.JSONDecodeError:
            if method!='DELETE':
                operation=path.split('?')[0] if path.startswith('/deposit/') or path.startswith('/records/') else 'file-bucket operation'
                raise RuntimeError(f'Non-JSON reply for {method} {operation}')
            listing=p.read(self.base,f'/deposit/depositions/{self.rid}/files')
            if not isinstance(listing,list) or any(str(f.get('id'))==match[2] for f in listing):
                raise RuntimeError('Empty DELETE reply was not confirmed by file-list readback')
            print('Same-draft file-list readback confirms inherited file removal.',flush=True)
            return None

def main():
    expected,manifest_hash=p.validate_package();p.require_publication_review(expected,manifest_hash)
    original=p.client
    p.client=lambda:ConfirmedDeleteClient(original(),expected['record_id'])
    try:p.publish()
    except Exception as error:
        p.save('publication-attempt.json',{'state':'INCOMPLETE_REQUIRES_SAME_RECORD_RESUMPTION',
               'record_id':expected['record_id'],'doi':expected['doi'],
               'error_type':type(error).__name__,'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
        print(type(error).__name__+': '+str(error),file=sys.stderr);sys.exit(1)

if __name__=='__main__':main()
