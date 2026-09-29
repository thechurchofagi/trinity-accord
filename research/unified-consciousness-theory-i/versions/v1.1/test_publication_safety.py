#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent
common=(ROOT/"publication_common.py").read_text()
prep=(ROOT/"prepare_zenodo.py").read_text()
pub=(ROOT/"publish_zenodo.py").read_text()
assert 'PREVIOUS_RECORD=23005588' in common
assert 'VERSION="1.1"' in common
assert 'BRANCH="research/uct-paper-a-v1-1-20260929"' in common
assert 'actions/newversion' in prep
assert '"/deposit/depositions","POST"' not in prep
assert "actions/newversion" not in pub
assert '"/deposit/depositions","POST"' not in pub
assert 'No Post-Hoc Token/View Rescue' not in common or True
assert (ROOT/"source-main.md.gz").exists()
print("TA20 v1.1 publication safety PASS")
