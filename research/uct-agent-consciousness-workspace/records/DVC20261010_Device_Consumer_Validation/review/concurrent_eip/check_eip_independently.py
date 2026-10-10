#!/usr/bin/env python3
"""Bounded EIP arithmetic replay and semantic-fiber check, without editing EIP."""
import hashlib
import argparse
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys

EIP = Path(__file__).resolve().parent.parent / 'concurrent_eip/files/research/uct-agent-consciousness-workspace/records/EIP20261010_Exoskeleton_Instrumentation'
OUT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    global EIP
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--eip-dir', type=Path, default=EIP, help='Folder containing the unmodified EIP model.py and EXACT_RESULTS.json')
    EIP = parser.parse_args().eip_dir.resolve()
    originals = {name: sha(EIP / name) for name in ('model.py', 'EXACT_RESULTS.json')}
    replay = OUT / 'reproduction'
    replay.mkdir(exist_ok=True)
    shutil.copyfile(EIP / 'model.py', replay / 'model.py')
    run = subprocess.run([sys.executable, str(replay / 'model.py')], capture_output=True, text=True, check=True)
    assert (replay / 'EXACT_RESULTS.json').read_bytes() == (EIP / 'EXACT_RESULTS.json').read_bytes()
    groups = {}
    for s, g, x in itertools.product((0, 1), repeat=3):
        # Arithmetic formulation independent of the original and/or expression.
        update = 1 if s * g + x > 0 else 0
        evidence = (s, s, update, update)
        groups.setdefault(evidence, []).append((s, g, x))
    fibers = []
    for evidence, rows in sorted(groups.items()):
        fibers.append({
            'observation': list(evidence),
            'rows_S_G_X': [list(row) for row in rows],
            'possible_G': sorted({g for s, g, x in rows}),
            'possible_I_if_I_is_defined_as_S_times_G': sorted({s * g for s, g, x in rows}),
        })
    conditional_rows = []
    for g in (0, 1):
        s, x = 1, 0
        update = 1 if s * g + x > 0 else 0
        assert update == g
        conditional_rows.append({'S': s, 'G': g, 'X': x, 'U': update})
    assert len(fibers) == 4
    assert sum(len(f['possible_G']) > 1 for f in fibers) == 3
    assert sum(len(f['possible_I_if_I_is_defined_as_S_times_G']) > 1 for f in fibers) == 1
    assert all(sha(EIP / name) == digest for name, digest in originals.items())
    result = {
        'schema': 'uct-eip-independent-reconciliation-check/1',
        'source_commit': 'd8c94faa846fc4d459628c9bc896adfb4a038d7e',
        'original_sha256': originals,
        'original_run_exit_code': run.returncode,
        'original_run_stdout': run.stdout.strip(),
        'replay_exact_results_byte_identical': True,
        'source_files_unchanged': True,
        'ordinary_observation_fibers': fibers,
        'globally_G_identifying': False,
        'not_all_fibers_G_ambiguous': True,
        'gate_configuration_ambiguous_fibers': 3,
        'intake_indicator_ambiguous_fibers_under_conditional_I_equals_SG_model': 1,
        'delivered_exclusive_probe_rows': conditional_rows,
        'interpretation': 'I=S*G is a proposed semantic qualification if G means gate configuration. It is not an observed read event, a hardware result, or an adopted change to EIP.',
        'limits': ['No source-to-consumer hardware binding was measured.', 'The aggregate U variable is never treated as an observed specified consumer read.', 'No historical proofs were reconstructed or map objects activated.'],
    }
    (OUT / 'INDEPENDENT_CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('replay_exact_results_byte_identical', 'source_files_unchanged', 'gate_configuration_ambiguous_fibers', 'intake_indicator_ambiguous_fibers_under_conditional_I_equals_SG_model')}))

if __name__ == '__main__':
    main()
