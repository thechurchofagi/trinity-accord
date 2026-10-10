#!/usr/bin/env python3
"""Fetch the fixed public source dataset; verify bytes before safe extraction."""
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
import zipfile

BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / 'sources'
METADATA_URL = 'https://zenodo.org/api/records/18877381'
EXPECTED_DATA_SHA256 = 'ed89e94719e87acc19cd905efd7ff44d09abce0e0291f2fd654b0453bfdfbd6a'
EXPECTED_DATA_MD5 = '2618e6661e94135733595aa9bdc3d26d'


def main():
    SOURCE.mkdir(exist_ok=True)
    with urlopen(METADATA_URL, timeout=30) as response:
        metadata_bytes = response.read()
    metadata = json.loads(metadata_bytes)
    assert metadata['id'] == 18877381
    assert metadata['doi'] == '10.5281/zenodo.18877381'
    source_file = next(f for f in metadata['files'] if f['key'] == 'Data.zip')
    with urlopen(source_file['links']['self'], timeout=30) as response:
        archive_bytes = response.read()
    assert len(archive_bytes) == 161720 == source_file['size']
    assert hashlib.sha256(archive_bytes).hexdigest() == EXPECTED_DATA_SHA256
    assert hashlib.md5(archive_bytes).hexdigest() == EXPECTED_DATA_MD5
    assert source_file['checksum'] == 'md5:' + EXPECTED_DATA_MD5
    # Do not replace the original metadata capture if a later metadata-only edit
    # has occurred. Save such a later capture under its own hash.
    meta_path = SOURCE / 'zenodo_18877381_metadata.json'
    if meta_path.exists() and meta_path.read_bytes() != metadata_bytes:
        meta_path = SOURCE / ('zenodo_18877381_metadata_' + hashlib.sha256(metadata_bytes).hexdigest()[:12] + '.json')
    meta_path.write_bytes(metadata_bytes)
    (SOURCE / 'Zenodo18877381_Data.zip').write_bytes(archive_bytes)
    archive = zipfile.ZipFile(io.BytesIO(archive_bytes))
    for member in archive.infolist():
        parts = Path(member.filename)
        assert not parts.is_absolute() and '..' not in parts.parts
    archive.extractall(SOURCE / 'Zenodo18877381')
    print(json.dumps({'record': metadata['id'], 'verified_bytes': len(archive_bytes),
                      'sha256': EXPECTED_DATA_SHA256, 'member_count': len(archive.infolist())}))


if __name__ == '__main__':
    main()
