#!/usr/bin/env python3
"""Reproduce deterministic results in temporary directories, preserving archives."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

BASE = Path(__file__).resolve().parent
jobs = [
    ('SCU', BASE/'check_source_consumers.py', BASE/'EXACT_RESULTS.json'),
    ('R204', BASE/'reproduction/baseline_R204/check_alignment_and_use.py',
     BASE/'reproduction/baseline_R204/EXACT_RESULTS.json'),
    ('R205', BASE/'reproduction/baseline_R205/exact_probe.py',
     BASE/'reproduction/baseline_R205/EXACT_RESULTS.json'),
    ('R201 coherent witnesses', BASE/'corrections/check_r201_coherent_witnesses.py',
     BASE/'corrections/R201_COHERENT_WITNESSES.json'),
    ('R202 residual witness', BASE/'corrections/check_r202_residual_correction.py',
     BASE/'corrections/R202_RESIDUAL_CORRECTION.json'),
    ('R194/R201/R202 effective corrections', BASE/'corrections/verify_effective_corrections.py',
     BASE/'corrections/EFFECTIVE_CORRECTION_EXACT_RESULTS.json'),
]

def main():
    receipts=[]
    with tempfile.TemporaryDirectory(prefix='uct-scu-reproduction-') as td:
        for k,(name,code,expected) in enumerate(jobs):
            work=Path(td)/str(k);work.mkdir()
            copied=work/code.name;shutil.copy2(code,copied)
            subprocess.run([sys.executable,str(copied)],cwd=work,
                           capture_output=True,text=True,check=True)
            actual=work/expected.name
            if actual.read_bytes()!=expected.read_bytes():
                raise AssertionError(f'{name}: exact output differs from frozen result')
            receipts.append({'name':name,'byte_equal':True,
                             'code_sha256':hashlib.sha256(code.read_bytes()).hexdigest(),
                             'result_sha256':hashlib.sha256(actual.read_bytes()).hexdigest()})
    print(json.dumps({'status':'PASS','runs':receipts,
                     'scope':'Deterministic model/rational-witness reproduction only; no actual or phenomenal inference.'},indent=2))

if __name__=='__main__':main()
