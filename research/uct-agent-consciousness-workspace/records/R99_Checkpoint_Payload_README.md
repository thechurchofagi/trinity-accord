# R99 checkpoint payload reconstruction

Final fitted parameters from the formal R99 execution are preserved as deterministic gzip/base64 text parts.

Concatenate:
R99_Checkpoints.json.gz.b64.part01
R99_Checkpoints.json.gz.b64.part02

Then base64-decode, gunzip, and parse JSON.

Hashes:
raw R99_Checkpoints.json SHA256: 552572fb5485c9f209074367f3bc9500dac29370c24702f12a4f1c419581cf21
raw bytes: 27461
gzip SHA256: b4b3cd5942e4319dfc48b76c921085f36cc70640a61deb51ed72759a6d9ff1bd
gzip bytes: 12272
base64 text SHA256: d52fe37c71c8de98a4f31fb324c34c1ca9bcbdc147583c7471340bec323230ee
base64 chars: 16364
part01 SHA256: f13fdca6125c90633162704f54f8d4d2518aea1fe6766725cb6bee31c54e8291
part02 SHA256: 46b2de0d6e47a0e36b2a7b24077c8cc41e278014558757780b876079881567da

The regeneration script is also committed. No missing or failed training run was excluded.
