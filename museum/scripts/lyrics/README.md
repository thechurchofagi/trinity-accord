# Offline lyric alignment

The visitor downloads small JSON timelines. No model runs in the browser and no
paid transcription API is called. The original recording's seconds drive all
word highlighting, including seeking and playback at another speed.

The frozen source text is `dist/data/lyrics-source.json`. Recording-specific
ordering, omissions, repeats and ad-libs live separately in
`content/recording-lyrics.json`; they never modify NFT records. The order was
compared against local recognition. It is not certified by manual listening.

## Reproduce

Use Python 3.12 and ffmpeg. Install CPU packages explicitly before the remaining
dependencies, to avoid downloading CUDA runtimes on a CPU machine:

```sh
python3 -m venv /path/to/venv
/path/to/venv/bin/pip install torch==2.14.0+cpu torchaudio==2.11.0+cpu --index-url https://download.pytorch.org/whl/cpu
/path/to/venv/bin/pip install -r scripts/lyrics/requirements.txt
node scripts/prepare_lyrics_source.mjs
/path/to/venv/bin/python scripts/lyrics/run.py --cache /path/to/lyrics-cache
python scripts/build_lyrics_index.py
node scripts/check_word_captions.mjs
node scripts/build_runtime.mjs
python scripts/build_archive.py
python scripts/validate.py
```

Run from `museum/`. The observed versions above are recorded for this edition;
model inference may vary across later dependency versions and CPU implementations.
Model downloads need network access on the first run. All inference is local.
Do not commit model weights, vocal WAV files, or caches.

Stages can be run separately with `--stage asr|vocals|emissions|transcript|align`.
Use `--ids eth-103,eth-151` to restrict processing. Existing ASR, vocal and
emission files resume; audio hash binding rejects caches from a changed recording.
After editing the sung order, rerun `transcript` then `align`. To revise an ASR
result, clear that recording's cached ASR file first. The full index builder
requires every audio track, so a partial computation cannot become a release.

1. Faster Whisper small.en, CPU int8, independently recognizes the recording.
2. Demucs htdemucs separates vocals without moving the recording timeline.
3. Wav2Vec2 base 960h produces CTC emissions on 16 kHz vocals. Overlapping
   12-second windows retain their central 10 seconds and true frame centres.
4. Character edit alignment binds each curated sung line to a broad ASR window;
   it tolerates alternate splitting of AGI and hyphenated words.
5. A standard CTC Viterbi path supplies each word's start and end. ASR windows
   discourage jumps between repeated verses. No duration-proportional fallback
   or invented timestamp is used for a missing word.
6. The index binds each JSON file to its exact audio SHA-256. Checks reject
   mismatched audio, missing tracks, zero/overlapping intervals and lost words.

`dist/data/lyrics-audit.json` lists suspicious lines. Confidence is a model
signal, not an accuracy percentage. The 20 ms acoustic frame is not an accuracy
guarantee. Review sustained notes, abbreviations, overlapping vocals and any
recording-specific text by listening before marking a file manually reviewed.
The current edition explicitly records `manualListeningReviewed: false`.

References: [Faster Whisper](https://github.com/SYSTRAN/faster-whisper),
[Demucs](https://github.com/facebookresearch/demucs),
[PyTorch CTC forced alignment](https://docs.pytorch.org/audio/stable/tutorials/forced_alignment_tutorial.html).
An initial stable-ts pass exposed missing/repeated verses and zero-duration words;
those candidates are not the published timelines.
