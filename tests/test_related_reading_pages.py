"""Protect the fixed quoted bodies while their reading interface evolves."""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]


def test_all_three_inscription_mirror_bodies_remain_exact():
    source = (ROOT / 'inscriptions.md').read_text()
    bodies = re.findall(
        r'<div class="inscription-header"[^>]*>.*?\n  </div>\n(.*?)\n</div>',
        source, re.S,
    )
    # Includes both original languages and the existing adjacent boundary notes.
    assert [hashlib.sha256(body.encode()).hexdigest() for body in bodies] == [
        '28463e43cb7dd4adf4b143d6b7cf5d8a6493a964369cb736d3b8836b10ccf9e4',
        '6676ec7a363b124a652578fb1c80df14cd255c5bf70b789d8657a80712c5c842',
        '05dfc653fd0792e546e2761419ae0b9483fa0e77b3f3808fcd436306a34c8ab1',
    ]
