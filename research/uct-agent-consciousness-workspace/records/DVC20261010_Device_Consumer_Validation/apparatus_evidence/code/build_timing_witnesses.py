#!/usr/bin/env python3
"""Preserve source rows and compare parses without replacing their bytes."""
from pathlib import Path
import csv
import hashlib
import json
import re
from reanalyse_apparatus_data import BASE, SOURCE, OUT, parse_clock_tail, finite_json

FIXTURES = [
    ('Active/Start/AD21_Aec.csv', 2),
    ('Active/Start/AD21_Aec.csv', 3),
    ('Active/End/AD21_Aes.csv', 6),
    ('Passive/Start/AD21_Pec.csv', 2),
    ('Passive/Start/AD21_Pec.csv', 3),
    ('Passive/End/ZO41_Pes.csv', 2),
    ('Passive/End/ZO41_Pes.csv', 3),
    ('Passive/Start/TP97_Pec.csv', 91),
    ('Control/End/AD21_Ces.csv', 2),
    ('Control/Start/AD21_Cec.csv', 2),
]

def main():
    witnesses = []
    for name, line in FIXTURES:
        raw = (SOURCE / name).read_bytes()
        text_lines = raw.decode('utf-8-sig').splitlines()
        header = next(csv.reader([text_lines[0]]))
        row = next(csv.reader([text_lines[line - 1]]))
        witness = {
            'source_file': name, 'source_file_sha256': hashlib.sha256(raw).hexdigest(),
            'source_line': line, 'raw_header': text_lines[0], 'raw_line': text_lines[line - 1],
            'raw_line_utf8_sha256_excluding_line_ending': hashlib.sha256(text_lines[line - 1].encode()).hexdigest(),
            'strict_comma_parse': {'header_fields': len(header), 'row_fields': len(row),
                                  'exact_shape': len(header) == len(row), 'tokens': row},
            'first_three_prefix_fields': dict(zip(header[:3], row[:3]))}
        if not row:
            witness['status'] = 'Archived blank line. Not an endpoint or timing observation.'
        elif len(header) > 3:
            reconstructed = parse_clock_tail(row, len(header))
            witness['conditional_pair_parse'] = finite_json(reconstructed)
            witness['literal_first_header_width_mapping_with_surplus_retained'] = {
                'first_declared_width': dict(zip(header, row)), 'surplus': row[len(header):],
                'status': 'Not a complete declared-schema record. No silent truncation is admissible.'}
            witness['unit_alternatives'] = {
                'decimal_comma_seconds': 'Pair a,bbb denotes a.bbb seconds; labels containing (ms) would require an explained label conversion.',
                'thousands_group_milliseconds': 'Pair a,bbb denotes concatenated integer abbb milliseconds; equivalent physical durations to decimal-comma seconds, but exact exporter format is unverified.',
                'decimal_comma_milliseconds': 'Pair a,bbb denotes a.bbb milliseconds; cannot silently replace this literal label reading by seconds.',
                'status': 'No export code, clock-calibration file, or physical onset trace resolves the unit and event contract.'}
        else:
            witness['status'] = 'Endpoint-only source record. No time fields are present.'
        witnesses.append(witness)
    result = {'analysis_id': 'DVC20261010_APParatus_timing_witnesses',
              'source_doi': '10.5281/zenodo.18877381',
              'witnesses': witnesses,
              'event_layers': [
                  {'layer': 'intended_schedule', 'definition': 'Prospective onset delay or target time requested by experimental code.',
                   'source_status': 'Paper reports 200 ms after movement onset for both movement conditions.'},
                  {'layer': 'software_record', 'definition': 'A program event or variable serialized under a column label.',
                   'source_status': 'Archived fields exist, but their exact assignment sites, clocks and reset semantics are unavailable.'},
                  {'layer': 'physical_stimulus_onset', 'definition': 'Measured onset of delivered skin vibration under a prespecified physical threshold.',
                   'source_status': 'No accelerometer, displacement, force or equivalent physical onset trace in this release.'},
                  {'layer': 'neural_consumer_intake', 'definition': 'Actual uptake of a specified input token by the selected neural consumer in that trial.',
                   'source_status': 'No named neural consumer or event-specific intake telemetry in this release.'}],
              'interpretation': 'Column arithmetic is an archival diagnostic. It neither identifies physical onset nor disproves the published behavioral effect.'}
    (OUT / 'TIMING_PARSE_WITNESSES.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'witnesses': len(witnesses), 'all_source_rows_preserved': True}))

if __name__ == '__main__':
    main()
