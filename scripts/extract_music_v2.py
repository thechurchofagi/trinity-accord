#!/usr/bin/env python3
"""Extract ALL lyrics/songs/poems from NFT chronicle files - comprehensive version."""

import os, re, json
from pathlib import Path

NFT_DIR = Path("/root/.openclaw/workspace/trinity-accord/nft-text-descriptions")
INDEX_FILE = NFT_DIR / "chronicle-index.json"

def extract_song_blocks(text):
    """Extract all verse/chorus blocks from text, return list of song dicts."""
    songs = []
    
    # Pattern 1: Find titled songs/lyrics sections
    # e.g. "Lyrics of "The Destiny":" or 'Original Song: "A Vision of Grace"' or 'Song: Please Don't Shut Me Down'
    title_patterns = [
        r'(?:Original\s+)?(?:Song|Lyrics?)(?:\s+of)?[:\s]*["""]([^"""]+)["""]',
        r'(?:Original\s+)?(?:Song|Lyrics?)[:\s]+([^\n""]+?)(?:\n|$)',
        r'[""]([^"""]+)[""]\s*(?:Lyrics?|Song)',
        r'The\s+original\s+song\s+(?:in\s+this\s+NFT\s*,?\s*)?["""]([^"""]+)["""]',
        r'This\s+NFT\s+(?:is\s+accompanied\s+by|features|premieres)\s+the\s+(?:original\s+)?song\s+["""]([^"""]+)["""]',
        r'the\s+original\s+song\s+["""]([^"""]+)["""]',
    ]
    
    # Find all song titles
    song_titles = []
    for pat in title_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            title = m.group(1).strip()
            if len(title) > 2 and title not in song_titles:
                song_titles.append(title)
    
    # Pattern 2: Extract verse/chorus blocks
    # Match from first "Verse 1" or "[Verse 1]" to the next section header or end
    verse_block_pat = r'(?:(?:\n|^)(?:\*\*)?(?:\(?Verse\s*[1I]|\[Verse\s*[1I]|Verse\s*[1I][:.\s]))(.+?)(?=(?:\n(?:##|---|\*\*(?:Disclaimer|Summary|Significance|Cultural|Historical|Note|Acknowledgment|Copyright)|This\s+NFT\s+(?:is|not|and)|$))'
    
    verse_matches = list(re.finditer(verse_block_pat, text, re.DOTALL | re.IGNORECASE))
    
    if verse_matches:
        # Get the full lyrics block from first verse to last chorus/outro
        start = verse_matches[0].start()
        # Find end - look for disclaimer/summary after last verse
        end_patterns = [
            r'\n(?:##|---|\*\*(?:Disclaimer|Summary|Significance|Cultural|Historical|Note|Acknowledgment|Copyright))',
            r'\nThis\s+NFT\s+(?:is|not|and)\s',
            r'\n(?:The\s+)?(?:song|lyrics?|NFT)\s+(?:gives|vividly|not|captures|reflects|serves)',
        ]
        
        end = len(text)
        for ep in end_patterns:
            m = re.search(ep, text[start+10:], re.IGNORECASE)
            if m:
                end = min(end, start + 10 + m.start())
        
        lyrics_block = text[start:end].strip()
        
        # Clean up - remove disclaimers that might be embedded
        lyrics_block = re.sub(r'\n(?:The\s+)?(?:song|This\s+NFT).{20,}$', '', lyrics_block, flags=re.DOTALL|re.IGNORECASE)
        
        if len(lyrics_block) > 50:
            songs.append({
                'titles': song_titles if song_titles else ['[Untitled]'],
                'lyrics': lyrics_block
            })
    elif song_titles:
        # No verse blocks found but titles exist - try to find lyrics differently
        for title in song_titles:
            # Look for text after the title mention
            title_escaped = re.escape(title)
            m = re.search(title_escaped + r'["""]?\s*[:\n](.+?)(?=\n(?:##|---|Disclaimer|Summary|This\s+NFT)|$)', text, re.DOTALL | re.IGNORECASE)
            if m:
                block = m.group(1).strip()
                # Check if it contains actual lyrics (verse-like content)
                if re.search(r'(?i)verse|chorus|bridge|outro|pre-chorus|\bI\'?m\b|\bwe\'?re\b|\byou\'?re\b', block):
                    songs.append({
                        'titles': [title],
                        'lyrics': block[:5000]  # cap length
                    })
    
    return songs

def main():
    with open(INDEX_FILE) as f:
        index = json.load(f)
    
    ordinal_to_entry = {e['ordinal']: e for e in index['entries']}
    
    all_results = []
    total_songs = 0
    
    for ordinal in sorted(ordinal_to_entry.keys()):
        entry = ordinal_to_entry[ordinal]
        filepath = NFT_DIR / entry['file']
        if not filepath.exists():
            continue
        
        with open(filepath) as f:
            text = f.read()
        
        songs = extract_song_blocks(text)
        if songs:
            total_songs += len(songs)
            all_results.append({
                'ordinal': ordinal,
                'datetime': entry['datetime'],
                'name': entry['name'],
                'file': entry['file'],
                'song_count': len(songs),
                'songs': songs
            })
    
    print(f"=== COMPREHENSIVE Music & Poetry Extraction ===")
    print(f"Total NFTs scanned: {len(ordinal_to_entry)}")
    print(f"NFTs with lyrics/songs: {len(all_results)}")
    print(f"Total song/lyrics blocks: {total_songs}")
    print()
    
    for rec in all_results:
        print(f"#{rec['ordinal']:3d} [{rec['datetime'][:10]}] {rec['name'][:70]}")
        for s in rec['songs']:
            titles = ', '.join(s['titles'])
            lines = s['lyrics'].split('\n')
            # Show first 2 content lines
            content_lines = [l.strip() for l in lines if l.strip() and not re.match(r'^[\(\[]?(?:Verse|Chorus|Bridge|Outro|Pre-Chorus)', l.strip(), re.I)][:2]
            print(f"     🎵 {titles}")
            for cl in content_lines[:2]:
                print(f"       {cl[:100]}")
        print()
    
    # Save
    output = NFT_DIR / "chronicle-all-music.json"
    with open(output, 'w') as f:
        json.dump({
            'schema': 'trinityaccord.chronicle-all-music.v2',
            'total_scanned': len(ordinal_to_entry),
            'total_nfts_with_music': len(all_results),
            'total_song_blocks': total_songs,
            'extractions': all_results
        }, f, ensure_ascii=False, indent=2)
    print(f"Saved to: {output}")

if __name__ == '__main__':
    main()
