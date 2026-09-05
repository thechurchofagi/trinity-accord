#!/usr/bin/env python3
"""Check derived lyric excerpts against their own unchanged NFT source files."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / 'nft-text-descriptions' / 'lyrics'

def main():
    index = json.loads((COLLECTION / 'index.json').read_text())
    entries = index['entries']
    assert len(entries) == index['counts']['written_reading_entries']
    assert len({e['id'] for e in entries}) == len(entries)
    records = set()
    checked = 0
    for entry in entries:
        assert (COLLECTION / entry['path']).is_file(), entry['path']
        for text, sources in [(entry['text'], [entry['source']])] + [
            (v['text'], v['sources']) for v in entry['variants']
        ]:
            for source in sources:
                raw = (ROOT / source['file']).read_bytes()
                assert hashlib.sha256(raw).hexdigest() == source['file_sha256'], source['file']
                assert raw.decode('utf-8')[source['start_char']:source['end_char']] == text, source
                assert f"/blob/{index['source_commit']}/" in source['url']
                records.add(source['nft_ordinal'])
                checked += 1
    assert len(records) == index['counts']['nft_records_with_extracted_text_or_fragments']
    assert len(index['audio_transcription_paths']) == index['counts']['audio_transcription_drafts']
    for path in index['audio_transcription_paths']:
        text = (COLLECTION / path).read_text()
        assert 'ASR DRAFT' in text and '不是NFT书面原词' in text, path
    print(f'PASS: {len(entries)} entries; {len(records)} NFT records; {checked} exact source excerpts; 2 labeled ASR drafts.')

if __name__ == '__main__':
    main()
