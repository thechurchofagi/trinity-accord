#!/usr/bin/env python3
"""Extract lyrics, songs, and poems from all 175 NFT chronicle markdown files."""

import os
import re
import json
from pathlib import Path

NFT_DIR = Path("/root/.openclaw/workspace/trinity-accord/nft-text-descriptions")
INDEX_FILE = NFT_DIR / "chronicle-index.json"

def extract_sections(text):
    """Extract lyrics, songs, poems from markdown text."""
    results = {}
    
    # Match various section patterns
    patterns = {
        'lyrics': [
            r'Original\s+Lyrics?\s*[:\-]\s*(.+?)(?=\n##|\nOriginal\s+(?:Poem|Song)|\Z)',
            r'Lyrics?\s*[:\-]\s*(.+?)(?=\n##|\Z)',
        ],
        'song': [
            r'Original\s+Song\s*[:\-]\s*(.+?)(?=\n##|\nOriginal\s+Poem|\Z)',
        ],
        'poem': [
            r'Original\s+Poem\s*[:\-]\s*(.+?)(?=\n##|\Z)',
        ],
    }
    
    for section_name, pats in patterns.items():
        for pat in pats:
            m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
            if m:
                content = m.group(1).strip()
                if len(content) > 30:  # skip tiny matches
                    results[section_name] = content
                break
    
    return results

def main():
    # Load index for metadata
    with open(INDEX_FILE) as f:
        index = json.load(f)
    
    # Build ordinal -> file map
    ordinal_to_entry = {}
    for entry in index['entries']:
        ordinal_to_entry[entry['ordinal']] = entry
    
    all_extractions = []
    lyrics_count = 0
    song_count = 0
    poem_count = 0
    
    for ordinal in sorted(ordinal_to_entry.keys()):
        entry = ordinal_to_entry[ordinal]
        filename = entry['file']
        filepath = NFT_DIR / filename
        
        if not filepath.exists():
            continue
        
        with open(filepath) as f:
            text = f.read()
        
        sections = extract_sections(text)
        
        if sections:
            record = {
                'ordinal': ordinal,
                'datetime': entry['datetime'],
                'name': entry['name'],
                'file': filename,
                'sections': sections
            }
            all_extractions.append(record)
            
            if 'lyrics' in sections:
                lyrics_count += 1
            if 'song' in sections:
                song_count += 1
            if 'poem' in sections:
                poem_count += 1
    
    # Output summary
    print(f"=== NFT Chronicle Music & Poetry Extraction ===")
    print(f"Total NFTs scanned: {len(ordinal_to_entry)}")
    print(f"NFTs with lyrics/songs/poems: {len(all_extractions)}")
    print(f"  - Lyrics sections: {lyrics_count}")
    print(f"  - Song sections: {song_count}")
    print(f"  - Poem sections: {poem_count}")
    print()
    
    for rec in all_extractions:
        print(f"--- #{rec['ordinal']} [{rec['datetime'][:10]}] {rec['name']}")
        for sec_name, content in rec['sections'].items():
            # Show first 3 lines
            lines = [l for l in content.split('\n') if l.strip()][:3]
            for l in lines:
                print(f"  [{sec_name}] {l[:120]}")
        print()
    
    # Save full extraction to JSON
    output_file = NFT_DIR / "chronicle-music-poetry-extracted.json"
    with open(output_file, 'w') as f:
        json.dump({
            'schema': 'trinityaccord.chronicle-music-poetry.v1',
            'total_scanned': len(ordinal_to_entry),
            'total_with_content': len(all_extractions),
            'counts': {
                'lyrics': lyrics_count,
                'song': song_count,
                'poem': poem_count,
            },
            'extractions': all_extractions
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Full extraction saved to: {output_file}")

if __name__ == '__main__':
    main()
