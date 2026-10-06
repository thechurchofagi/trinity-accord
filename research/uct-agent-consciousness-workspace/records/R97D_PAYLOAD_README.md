# R97D pre-reconciliation payload reconstruction

The experiment executed before the concurrent official R97 was discovered, so the immutable JSON payload internally uses the local round label "R97". It is intentionally preserved unchanged under R97D_PreReconciliation_* names.

Results:
base64 -d R97D_PreReconciliation_Results.json.gz.b64 | gunzip > R97D_PreReconciliation_Results.json

Checkpoints:
cat R97D_PreReconciliation_Checkpoints.json.gz.b64.part* | base64 -d | gunzip > R97D_PreReconciliation_Checkpoints.json

Raw SHA256:
Results JSON d93d3d473702b3bbaaee07cf4e331b404eae35f2f07ab015024316c78ffa7674
Checkpoints JSON afaf4a4287109ea6fddccb963bf9d07574a0cf389ee00ff2a8fa4057f1b215fd
Concatenated checkpoint base64 text 5c46e28e6c85c5a085320ef466a4b3ab8a64452db7e6607edba0376183a1c690
