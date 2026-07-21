# Speech-to-Text Subsystem

Speech-to-Text (STT) subsystem for the Smart Conference Room Speech
Transcription System.

## Scope

This repository owns **only** the Speech-to-Text subsystem:

```
Presenter
   |
Laptop Microphone
   |
Python Backend
   |
Speech-to-Text API
   |
Receive Transcript
   |
Display Transcript
```

- **Milestone 1**: microphone capture, a runnable pipeline, console
  display.
- **Milestone 2**: a pluggable Speech-to-Text provider layer -
  `SpeechProvider` interface, an OpenAI implementation, and a factory for
  adding Deepgram / Google Speech-to-Text / a local Whisper model later.
- **Milestone 3** (this one): rebuilt microphone capture as a continuous,
  overlapping-chunk stream, fixing audio loss during transcription and
  clipped/quiet speech (see "Design Decisions").

## Design Decisions

### Why microphone capture was rebuilt

The original capture used `speech_recognition`'s `recognizer.listen()` in
a loop: listen for one phrase (silence-delimited), yield it, listen for
the next. Two problems fell out of that:

1. **Audio was lost during transcription.** `stream()` is a generator; the
   loop only resumes listening when the *consumer* asks for the next
   chunk. Since the consumer is `SpeechProviderEngine`, which blocks on an
   OpenAI API call per chunk, the microphone was effectively **not
   listening** for the entire duration of every API round-trip. Anything
   said during that window was silently dropped - this was the source of
   the "audio not clear / some audio not visible" issue.
2. **Energy-threshold silence detection could drop quiet speech
   entirely**, since `listen()` decides phrase boundaries by comparing
   volume to a calibrated threshold.

The fix is a genuine architecture change, not a tuning tweak: capture now
runs on PyAudio's callback API, which PortAudio drives on its own internal
thread, filling an in-memory queue continuously and independently of
whatever the Python-level consumer (transcription) is doing. The
microphone is never paused while an API call is in flight.

### Overlapping, fixed-duration chunks

Chunking is now time-based (e.g. 4-second windows) rather than
silence-based, so quiet speech is never classified away. Consecutive
chunks overlap (e.g. by 1 second): without overlap, a word spoken exactly
on a chunk boundary is split across two independent transcription
requests and is frequently garbled or dropped in *both*. Overlap
guarantees boundary audio appears whole in at least one chunk.

The pure sliding-window math lives in `src/audio/chunker.py`
(`OverlappingAudioChunker`), deliberately with **no** PyAudio or threading
dependency, so it's unit-testable with plain bytes - see
`tests/test_audio_chunker.py`, which verifies chunk sizing, overlap
correctness, and that a trailing partial chunk isn't dropped when capture
stops (`flush()`).

### Known limitation: duplicate text in overlaps

Because consecutive chunks overlap, the words spoken in that overlapping
audio region will appear in **both** chunks' transcripts. This subsystem
does not currently de-duplicate that text - each `Transcript` is exactly
what the Speech-to-Text API returned for its chunk. Stitching/de-duplicating
overlapping transcripts (e.g. by aligning trailing/leading words) is a
natural extension to `SpeechProviderEngine` or the display layer, but is
out of scope here.

### Chunks are saved to disk as `.wav` files

Every chunk is written to `AUDIO_CHUNK_SAVE_DIR` (default `audio_chunks/`)
as a self-contained `.wav` file, independent of whether it's also
transcribed successfully. This exists specifically so audio quality can
be inspected directly (open the file, listen to it) rather than only
trusting the transcribed text - which is exactly how the original issue
was diagnosed. Set `AUDIO_CHUNK_SAVE_DIR=` (empty) to disable.

### Error handling

`MicrophoneAudioSource` never lets a `pyaudio`-specific exception escape;
everything is translated to `AudioCaptureError` from
`src/core/exceptions.py`. Saving a chunk to disk is best-effort: an
`OSError` while writing a debug `.wav` file is logged and skipped, never
allowed to interrupt a live transcription session.

## Project Structure

```
speech-to-text-subsystem/
├── config.py                          # Centralized configuration
├── main.py                            # Application entry point
├── requirements.txt
├── examples/
│   └── transcribe_audio_file.py       # Standalone SpeechProvider usage example
├── src/
│   ├── core/
│   │   ├── interfaces.py              # AudioSource / SpeechToTextEngine / TranscriptDisplay
│   │   ├── models.py                  # Transcript
│   │   ├── exceptions.py              # Subsystem-specific exceptions
│   │   └── logging_config.py          # Logging setup
│   ├── audio/
│   │   ├── microphone_input.py        # AudioSource: continuous overlapping-chunk capture
│   │   ├── chunker.py                 # Pure sliding-window chunking logic (unit-testable)
│   │   └── wav_encoding.py            # Pure PCM -> WAV encoding (unit-testable)
│   ├── stt/
│   │   ├── engine.py                  # SpeechProviderEngine (SpeechToTextEngine impl)
│   │   └── providers/
│   │       ├── base.py                # SpeechProvider interface
│   │       ├── openai_provider.py     # OpenAISpeechProvider
│   │       └── factory.py             # create_speech_provider()
│   ├── display/
│   │   └── console_display.py         # TranscriptDisplay: console output
│   └── pipeline/
│       └── transcription_pipeline.py  # Orchestrates the above via interfaces
└── tests/
```

## Setup

Microphone capture depends on PyAudio, which requires the PortAudio
system library.

**Linux (Debian/Ubuntu):** `sudo apt-get install portaudio19-dev`
**macOS:** `brew install portaudio`
**Windows:** no extra system package needed.

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set your OpenAI API key, e.g. in a `.env` file at the project root:

```
OPENAI_API_KEY=sk-...
```

Optional overrides (defaults shown):

```
STT_PROVIDER=openai
OPENAI_STT_MODEL=whisper-1
STT_LANGUAGE=en

AUDIO_SAMPLE_RATE_HZ=16000
AUDIO_CHUNK_DURATION_SECONDS=4.0
AUDIO_CHUNK_OVERLAP_SECONDS=1.0
AUDIO_FRAMES_PER_BUFFER=1024
AUDIO_CHUNK_SAVE_DIR=audio_chunks

LOG_LEVEL=INFO
```

Tuning notes:
- Increase `AUDIO_CHUNK_OVERLAP_SECONDS` if words still seem to be getting
  cut off at chunk boundaries.
- Decrease `AUDIO_CHUNK_DURATION_SECONDS` for lower transcription latency
  (shorter wait before each chunk is sent to the API); increase it for
  fewer, cheaper API calls with more context per request.

## Running

```bash
python main.py
```

Listens continuously, in real time, regardless of how long each chunk
takes to transcribe. Every chunk is saved to `AUDIO_CHUNK_SAVE_DIR` and
its transcript is printed to the console as it comes back. Press `Ctrl+C`
to stop (the final, possibly-shorter chunk is still flushed and
transcribed before exiting).

## Example: Transcribing a File Directly

```bash
python examples/transcribe_audio_file.py path/to/recording.wav
```

## Testing

```bash
pip install pytest
python -m pytest tests/ -v
```

`chunker`, `wav_encoding`, provider, and engine tests are fully
deterministic and require no real microphone or network access.
Live microphone capture (`MicrophoneAudioSource.stream()`) is exercised
manually by running `python main.py`, not by the automated suite.

## Adding a New Provider

1. Create `src/stt/providers/<name>_provider.py` implementing
   `SpeechProvider.transcribe(audio: bytes) -> str`, translating that
   backend's exceptions into `TranscriptionError`.
2. Add its configuration fields to `config.py`.
3. Add one branch in `create_speech_provider()`
   (`src/stt/providers/factory.py`).
4. Set `STT_PROVIDER=<name>`. No changes needed anywhere else.

## Future Work

- De-duplicate transcribed text across overlapping chunk boundaries.
- Implement `DeepgramSpeechProvider`, `GoogleSpeechProvider`, and
  `LocalWhisperSpeechProvider`.
- A streaming-capable `SpeechProvider`/engine pair for lower latency.
