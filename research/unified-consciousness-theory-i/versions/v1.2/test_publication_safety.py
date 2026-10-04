#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
common=(ROOT/"publication_common.py").read_text()
prep=(ROOT/"prepare_zenodo.py").read_text()
pub=(ROOT/"publish_zenodo.py").read_text()
assert 'PREVIOUS_RECORD=23030207' in common
assert 'EXPECTED_CONCEPT="23005587"' in common
assert 'VERSION="1.2"' in common
assert 'BRANCH="research/uct-paper-a-v1-2-20261004"' in common
assert 'SOURCE_GIT_BLOB_SHA1="310204d4e83c5478bf18d34274bcdba996ffda28"' in common
assert 'actions/newversion' in prep
assert '"/deposit/depositions","POST"' not in prep
assert "actions/newversion" not in pub
assert '"/deposit/depositions","POST"' not in pub
assert (ROOT/"source-main.md").exists()
assert (ROOT/"FORMAL-AUDIT-v1.2.md").exists()
print("TA20 v1.2 publication safety PASS")
