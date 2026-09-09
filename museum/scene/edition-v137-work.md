# museum-v1.37.0 production record

Candidate built locally; publication and browser acceptance still pending.
Baseline: 047e9978cf2e8537ec9d6b242a73c3481662045e.

- Reviewed all 175 NFT records and 70 lyric/poem texts. Selected 43 wall entries with 30 verified own or explicitly attributed recordings; complete original sources remain available.
- Fifteen-stop English route covers contemporary witness, making and work, fear and waiting, critique, medium choice, six hashes, the crystal and the changing Church symbol. The three Bitcoin Originals and evidence photographs are unchanged.
- The user cancelled Chinese narration. The active edition has fifteen English Qwen Aiden tour tracks and three English inspection tracks. Both interface languages use the same route and recordings. Narration and music share timed-subtitles.js and responsive CSS, with English acoustic word highlighting above Chinese sentence translations.
- English synthesis: Qwen3-TTS-12Hz-1.7B-CustomVoice revision 0c0e3051f131929182e2c023b9537f8b1c68adfe, local CPU. An unused legacy 25 Hz module eagerly imported ONNX Runtime and triggered blocked telemetry. The recorded lazy-import patch removes that dependency from the selected 12 Hz path. Import and model-load assertions confirm ONNX is absent. No telemetry permission or approval controls were changed.
- Ten new recordings / thirty used paragraphs have independent Whisper recognition review. Five unchanged English guide texts and three inspections reuse prior Qwen recordings. Unused trial takes are not distributed.
- All eighteen English tracks have acoustic CTC word boundaries and 111 Chinese sentence translations. Audio and script hashes are checked. Total measured guide/music/inspection estimate is 659.12 seconds; movement may add time.
- Thirty-two songs have acoustic word alignment and complete Chinese line translations. The 54:38 R1 cycle retains its full recording and source track list; the Chinese Farewell recording retains readable source lyrics. Neither receives invented word timing.
- Local source integrity, complete file inventory, language/voice, caption paging, navigation, walking, spatial layout, frames, playback, loading and inspection checks passed. No human listening or rendered-browser certification is claimed.
- Direct local browser preview was denied by URL policy; no alternate browser workaround was attempted. Use the repository's required browser jobs and review their outputs before merge.
- Git CLI has no write credential. The connected GitHub app uploads candidate objects. A separate media-assembly branch and hash-checking workflow reconstruct the oversized R1 blob; assembly succeeded. The final candidate tree excludes that temporary workflow and upload fragments.

Remaining: finish candidate commit/PR, inspect final-head CI and browser outputs, merge when accepted, and verify the Alibaba deployment receipt and published assets. Chinese voice production is cancelled by the user's latest instruction.
