#!/usr/bin/env python3
"""Build an integrity manifest and portable R122 export, without rerunning research."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_constant(value):
    raise ValueError(f'Nonstandard JSON constant: {value}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    package = args.package
    records = package.parent
    target = args.out or records/'R122_Research_Package_20261006.zip'
    if target.exists():
        raise FileExistsError(f'Refusing to overwrite existing export: {target}')
    files = sorted(p for p in package.rglob('*') if p.is_file() and p.name != 'SHA256SUMS.txt')
    # A packaging-format check, not a repeated research audit.
    for path in files:
        if path.suffix == '.json':
            json.loads(path.read_text(), parse_constant=reject_constant)
    manifest = package/'SHA256SUMS.txt'
    manifest.write_text(''.join(f'{sha(p)}  {p.relative_to(package).as_posix()}\n' for p in files))
    main_reports = [records/'R122_Real_Rat_B1_B2_and_Open_T2_Certificate_20261006.md',
                    records/'R122_Worklog_and_Handoff_20261006.md']
    export_files = main_reports + files + [manifest]
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in export_files:
            entry = zipfile.ZipInfo(path.relative_to(records).as_posix(), date_time=(2026,10,6,0,0,0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            z.writestr(entry, path.read_bytes())
    receipt = {'round': 'R122', 'archive': target.name, 'bytes': target.stat().st_size,
               'sha256': sha(target), 'files_in_export': len(export_files),
               'uncompressed_bytes': sum(p.stat().st_size for p in export_files),
               'package_manifest': str(manifest.relative_to(records)),
               'package_manifest_sha256': sha(manifest),
               'main_reports': [{'path':p.name,'sha256':sha(p)} for p in main_reports],
               'scope': 'All R122 reports, scripts, derived results, source/review ledgers and provenance; upstream raw MAT and article PDF are not embedded.',
               'archive_layout': 'Main reports and R122_Biology_B1_B2_20261006 directory at archive root; prior-round context remains in the cited research repository.'}
    (records/'R122_Package_Receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
