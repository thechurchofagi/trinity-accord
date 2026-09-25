#!/usr/bin/env python3
import json
from publication_common import validate_local_package
expected,digest=validate_local_package()
print(json.dumps({
  "state":"EXACT_PUBLICATION_PACKAGE_REVIEW_PASS",
  "report_number":expected["report_number"],
  "version":expected["version"],
  "record_id":expected["record_id"],
  "doi":expected["doi"],
  "file_count":expected["file_count"],
  "expected_manifest_sha256":digest
},indent=2))
