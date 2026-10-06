#!/usr/bin/env python3
"""Export checkpoint metadata from saved results; no model fitting or data edits."""
import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

import matplotlib
import numpy
import pandas
import scipy
import sklearn
from threadpoolctl import threadpool_info


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    p = args.package
    b1 = json.loads((p/'b1_results/B1_results.json').read_text())
    b2 = json.loads((p/'b2_results/B2_aggregate.json').read_text())
    sources = []
    for path in sorted((p/'schema_scan').glob('*.json')):
        s = json.loads(path.read_text())
        sources.append({'file': Path(s['source_file']).name, 'bytes': s['source_bytes'],
                        'sha256': s['source_sha256'], 'source_trials': s['n_source_trials'],
                        'b1_eligible_trials': s['n_eligible_trials'],
                        'source_units': s['neural_unit_count'],
                        'recorded_availability': s['recorded_availability'],
                        'nonfinite_spike_count': s['nonfinite_spike_count']})
    save(p/'R122_Input_Manifest.json', {
        'dataset_doi': '10.6084/m9.figshare.30369064.v1',
        'version_metadata': 'https://api.figshare.com/v2/articles/30369064/versions/1',
        'stable_download': 'https://ndownloader.figshare.com/files/58773835',
        'archive_bytes': 1929137550, 'archive_md5': '3b0ab5c964fb492ec36ee0f55a5d53de',
        'archive_sha256': 'e23a5c281b828c5d9545576ebc9197f37dbc20bd16c616aa2eda55d220fe9494',
        'n_sessions': len(sources), 'sessions': sources,
        'source_hash_origin': 'Executed common-loader schema audits; no inferred or synthetic raw files',
        'author_repository': 'Brody-Lab/fof_ads_interactions',
        'author_commit': '39d056fb12f688034b543d9ac8b7406a58ad0f77',
        'final_author_pdf_url': 'https://dikshagup.github.io/publication/multiregion-accumulation/multiregion-accumulation.pdf',
        'final_author_pdf_bytes': 11663991,
        'final_author_pdf_sha256': '8daabdb02884a87b51c0c618f64c7f14a53e92b20eda7eaf70132ff640f24789'})
    rows = [
        ('C0', 'grounding consistency', 'PASS', 'Restricted external signed-count task coordinate',
         'All eligible raw click identities, signs, times and source rows checked; R117 uses signed evidence history.',
         'Does not pass input-distribution matching, internal-state identity, temporal transport or phenomenal labeling.',
         'R122_Input_Manifest.json; independent_b1_checks.json; independent_analysis_checks.json'),
        ('C1', 'baseline correspondence', 'UNCERTAIN', 'Biology to AI output-law comparison',
         'R122 real rat choice predictions and historical R117 artificial behavior are available.',
         'Declare matched inputs/nuisances, common output law and epsilon_base. R117 accuracy and pulse use different readout laws.',
         'b1_results/B1_results.json; R122_Continuity_Read_Ledger.json'),
        ('C2', 'transition commutation', 'UNCERTAIN', 'Selected causally used state transition',
         'Modest/heterogeneous held-out external cumulative-evidence decoding.',
         'Identify biological causal state, update law, state map and epsilon_update; decoding does not establish these.',
         'b2_results/B2_aggregate.json; R122_Primary_Methods_and_T2_Audit.md'),
        ('C3', 'intervention transport', 'UNCERTAIN', 'Actual part/port-specific causal operations',
         'Historical R117 interventions; independently read published biology; all twelve recording laser flags are zero.',
         'Obtain independently assessable biological perturbation outcomes; establish phi_I and epsilon_int. Registry is not trial behavior.',
         'independent_raw_audit.json; R122_Methods_Source_Ledger.json'),
        ('C4', 'temporal correspondence', 'UNCERTAIN', 'Matched state/update/intervention timing',
         'Biological clocks, actual stimulus durations, 50 ms bins and 100 ms observation lag audited.',
         'Declare phi_tau; normalized fractions, abstract AI bins, sustained inhibition and instantaneous reset are not already matched.',
         'B2_PROTOCOL_FROZEN.md; independent_analysis_checks.json'),
        ('C5', 'nuisance stability', 'UNCERTAIN', 'Declared cross-substrate nuisance domain',
         'All five rats/twelve sessions, blocked trial validation, population-count matching and controls retained.',
         'Establish correspondence error bounds across difficulty, laterality, intervention conditions and model realizations; current heterogeneity remains.',
         'b1_results/B1_results.json; b2_results/B2_session_metrics.csv'),
        ('C6', 'anti-triviality / mapping discipline', 'UNCERTAIN', 'Analysis discipline passed; mechanism map incomplete',
         'External target, locally frozen low-complexity estimators, training-only preprocessing and fixed controls.',
         'Justify an actual part/port-grounded state map and test correlate-only or wrong-port alternatives; successful decoding alone is insufficient.',
         'R122_B1_Frozen_Protocol.md; B2_PROTOCOL_FROZEN.md; independent_review.md')]
    fields = ['component', 'requirement', 'status', 'scope', 'evidence', 'remaining_gap', 'artifact_refs']
    with (p/'R122_T2_Certificate.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(dict(zip(fields, row)) for row in rows)
    save(p/'R122_T2_Certificate.json', {
        'schema_version': '1.0', 'round': 'R122', 'date': '2026-10-06',
        'framework': 'R119 T2 intervention-preserving support correspondence',
        'foundational_UCT_C1_is_distinct_from_certificate_C1': True,
        'candidate_domain': 'Audited rat left/right click histories and historical R117 signed evidence-count task coordinate',
        'maps': {'phi_X': 'restricted signed-count semantics only; common input domain still required',
                 'phi_Y': 'candidate left/right-choice coordinate; output laws uncalibrated',
                 'phi_Z': None, 'phi_I': None, 'phi_tau': None},
        'accepted_error_bounds': {'epsilon_base': None, 'epsilon_update': None, 'epsilon_int': None},
        'components': [dict(zip(fields, row)) for row in rows],
        'overall': 'T2_NOT_CLOSED', 'T3': 'NOT_ESTABLISHED', 'G4': 'NOT_ESTABLISHED',
        'cross_substrate_G2_geometry_comparison': 'NOT_ESTABLISHED_BY_DECODER_SCORE',
        'B3': 'NOT_INDEPENDENTLY_REPLICATED', 'AI_experience_E': 'LATENT_NOT_LABELED',
        'valence_V': 'NOT_MEASURED', 'subject_boundary': 'NOT_ESTABLISHED',
        'status_semantics': 'PASS applies only to stated scope; UNCERTAIN is missing/insufficient evidence, not an invented failed quantitative bound.'})
    code_hashes = {name: hashlib.sha256((p/name).read_bytes()).hexdigest()
                   for name in ['rat_cells.py', 'b1_kernel.py', 'b2_decode.py']}
    save(p/'R122_Research_Status.json', {
        'schema_version': '1.0', 'round': 'R122', 'date': '2026-10-06',
        'repository': 'thechurchofagi/trinity-accord', 'branch': 'uct-agent-consciousness-workspace',
        'research_directory': 'research/uct-agent-consciousness-workspace',
        'continuation_parent_at_start': 'ab02cb6ea51442aa434bdfbe3ef69d52d2877996',
        'archive_status': 'COMPLETE_DOWNLOAD_SIZE_MD5_SHA256_VERIFIED',
        'B1': {'status': b1['status'], 'n_sessions': b1['n_sessions_completed'],
               'n_rats': len(b1['aggregate']['per_rat']),
               'n_trials': sum(s['n_eligible_trials'] for s in b1['sessions']),
               'primary_contrast': 'full10 versus lastbin held-out log-loss improvement',
               'primary_conclusion': 'INCONCLUSIVE_ACROSS_FIVE_RATS',
               'model_metrics_equal_rat': b1['aggregate']['models'],
               'prespecified_loss_contrasts': b1['aggregate']['paired_loss_gain'],
               'accuracy_target': 'observed rat choice, not objective task correctness'},
        'B2': {'status': 'COMPLETED_INDEPENDENT_CONSERVATIVE_REANALYSIS',
               'n_sessions': b2['n_sessions_computed'], 'n_failed_sessions': b2['n_sessions_failed'],
               'n_rats': b2['n_rats'], 'n_trials': 3319, 'n_held_out_bins': 32656,
               'equal_rat_means': b2['equal_rat_means'], 'paired_rat_contrasts': b2['paired_rat_contrasts'],
               'conclusion': 'MODEST_HETEROGENEOUS_STIMULUS_DECODABILITY',
               'exact_reproduction_of_Figure_2C': False,
               'negative_session_region_R2': 8, 'session_region_pairs': 24},
        'independent_computational_review': 'PASS_WITH_DECLARED_SCIENTIFIC_LIMITS',
        'code_sha256': code_hashes, 'externally_preregistered': False,
        'new_AI_runs': 0, 'new_theorems': 0, 'B3_trial_replication': False,
        'T2': 'NOT_CLOSED', 'T3': 'NOT_ESTABLISHED', 'G4': 'NOT_ESTABLISHED',
        'E': 'LATENT', 'V': 'NOT_MEASURED',
        'R117_readout_caveat': 'Accuracy uses Gaussian decision noise sigma3; pulse probability uses sigmoid temperature3; state R2 is cum versus cum+Gaussian noise, not a trained held-out decoder.',
        'next_narrow_step': 'Declare biological state/port/time maps and common output law with error tolerances; pursue auditable biological perturbation outcomes. If needed, a predeclared one-factor sensitivity on the same sessions, without altering R122.',
        'source_and_read_scope': ['R122_Continuity_Read_Ledger.json', 'R122_Methods_Source_Ledger.json', 'R122_B1_Source_Schema_Ledger.json']})
    versions = {'python': platform.python_version(), 'numpy': numpy.__version__, 'scipy': scipy.__version__,
                'pandas': pandas.__version__, 'scikit-learn': sklearn.__version__, 'matplotlib': matplotlib.__version__}
    save(p/'R122_Environment.json', {'versions': versions, 'platform': platform.platform(),
                                  'machine': platform.machine(), 'numeric_libraries': threadpool_info(),
                                  'scope': 'Same primary runtime used for B1/B2; collected while assembling the unchanged checkpoint.'})
    (p/'requirements.txt').write_text('# Executed with Python ' + versions['python'] + '\n' +
        '\n'.join(f'{k}=={v}' for k,v in versions.items() if k != 'python') + '\n')
    save(p/'R122_Integration_Review.json', {
        'reviewer': 'independent_review subtask; separate raw-data audit and final text review',
        'disposition': 'ACCEPT_WITH_ONE_WORDING_CORRECTION_RESOLVED',
        'scientific_checks': 'See independent_review.md and executed independent_*_checks.json',
        'final_text_correction': 'Replaced ambiguous capability-difference refines E-type wording with difference implies difference under fixed complete conditions; no refinement/richness ordering implied.',
        'coordinator_additions': ['R117 distinct Gaussian/sigmoid readout laws disclosed', 'Figure script path corrected to figures/plot_r122_summary.py'],
        'additional_fits_or_tests_for_integration': 0})
    print(json.dumps({'metadata_export': 'completed', 'sessions': len(sources), 'versions': versions}))


if __name__ == '__main__':
    main()
