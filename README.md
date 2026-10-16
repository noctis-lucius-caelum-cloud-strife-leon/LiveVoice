# LiveVoice

An experimental, MIT-licensed TikTok LIVE text-to-speech and follower sound app for Windows. **Early prototype, not production ready.**

## Features in this prototype
- TTS eligibility gates: follower, observed previous gifter, moderator (OR/AND)
- Gift events and follow events, configurable sound alerts and gift thank-you TTS
- Persistent gifted-user identifiers and timestamped event log (`livevoice.log`) in the LiveVoice application data folder

- Connect to a currently live TikTok username without asking for a password
- Read chat messages using Edge neural voices (internet required)
- Follow sound alert: drag/drop MP3, WAV, or OGG, max 10 MB
- Test buttons, audio volume, per-user cooldown, queue, emergency stop
- Saved settings under `%APPDATA%\LiveVoice`
- Local FastAPI server embedded in a pywebview desktop window

## Run from source (development)

Requires Python 3.11+ on Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m livevoice.main
```

The desktop app runs a local HTTP server bound to `127.0.0.1` only. TikTokLive is an **unofficial** integration, and events may stop working when TikTok changes its service. Edge TTS requires internet access. Follow events are best-effort. You must route Windows audio into TikTok LIVE Studio or OBS as appropriate; this is not automatically configured.

## Windows packaging

The included GitHub Actions workflow builds a PyInstaller **one-folder** Windows distribution and uploads a ZIP as an artifact. This is a starting point, not a signed installer. Build/release validation on a Windows machine is still required.

## Known limitations

- No share, subscription, AI, overlays, or advanced moderation modules yet.
- Follow/moderator flag accuracy and gift streak behavior still need live-stream validation.
- Event logs contain viewer names and comments; handle them as personal data.
- No automatic reconnect or device selection yet.
- TikTokLive versions and event interfaces need real-stream integration testing.
- Stop/mute clears the queue and stops current audio, but concurrent event races need more testing.
- No code-signing; Windows SmartScreen may warn.
- The local HTTP API is unauthenticated; it binds only to loopback. Do not expose its port externally.

## License

MIT. See [LICENSE](LICENSE). Third-party dependencies retain their own licenses.

## Linux / browser development mode

The dashboard can run in your default browser without GTK, Qt, PySide6, or pywebview:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m livevoice.main --browser
```

If installing from scratch on Linux, you can omit `pywebview` (a desktop-only dependency):

```bash
pip install fastapi uvicorn TikTokLive edge-tts pygame python-multipart
python -m livevoice.main --browser
```

Open the localhost URL printed in the terminal if the browser doesn't open automatically. Use `--browser --no-open` to start the server without launching a browser. Press Ctrl+C to stop. Sound plays through the machine running the Python backend, not necessarily the browser's machine. The application is still experimental; TikTok connection and audio require separate real-world testing.

## Chat filtering
All chat messages are eligible for TTS (no follower/mod/gift gates). Safety filtering is enabled by default: common profanity/slurs, obfuscated text, URLs, maximum length, and per-viewer duplicate messages. Add custom blocked words/phrases in the dashboard (one per line), then save. The filter checks both message and nickname before speech. False positives and bypasses are possible; mute remains available. Gift and follow sounds continue independently of chat filters.
