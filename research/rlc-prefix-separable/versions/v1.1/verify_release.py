#!/usr/bin/env python3
"""Reproduce frozen mathematical receipts without modifying reviewed sources."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parent
CHECKS=[('verify_readk_and_interleaving.py','verification.json'),
        ('verify_comparison_support_entropy.py','comparison_support_entropy_verification.json'),
        ('verify_bottom_extension_concentration.py','bottom_extension_concentration_verification.json'),
        ('verify_sparse_support_amplification.py','sparse_support_amplification_verification.json'),
        ('verify_conditional_mean_obstruction.py','conditional_mean_obstruction_verification.json')]
IGNORED={'seconds','elapsed_seconds','audit_sha256'}
def stable(v):
    if isinstance(v,dict):return {k:stable(x) for k,x in v.items() if k not in IGNORED}
    if isinstance(v,list):return [stable(x) for x in v]
    return v
def main():
    rows=[]
    with tempfile.TemporaryDirectory(prefix='rlc-v11-audit-') as td:
        dest=Path(td)
        shutil.copytree(ROOT/'dependencies',dest/'dependencies')
        for script,receipt in CHECKS:
            shutil.copy2(ROOT/script,dest/script)
            done=subprocess.run([sys.executable,str(dest/script)],cwd=dest,capture_output=True,text=True,check=True)
            expected=json.loads((ROOT/receipt).read_text())
            actual=json.loads((dest/receipt).read_text())
            if stable(actual)!=stable(expected):raise RuntimeError('Mathematical receipt changed: '+receipt)
            rows.append({'script':script,'script_sha256':hashlib.sha256((ROOT/script).read_bytes()).hexdigest(),
                         'receipt':receipt,'receipt_sha256':hashlib.sha256((ROOT/receipt).read_bytes()).hexdigest(),
                         'stable_mathematical_fields_match':True})
    print(json.dumps({'state':'V11_FROZEN_MATHEMATICAL_RECEIPTS_REPRODUCED','checks':rows,'violations':0},indent=2))
if __name__=='__main__':main()
