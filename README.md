# LiveVoice

An experimental, MIT-licensed TikTok LIVE text-to-speech and follower sound app for Windows. **Early prototype, not production ready.**

## Features in this prototype
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

- No gift, share, subscription, AI, overlays, or advanced moderation modules yet.
- No automatic reconnect or device selection yet.
- TikTokLive versions and event interfaces need real-stream integration testing.
- Stop/mute clears the queue and stops current audio, but concurrent event races need more testing.
- No code-signing; Windows SmartScreen may warn.
- The local HTTP API is unauthenticated; it binds only to loopback. Do not expose its port externally.

## License

MIT. See [LICENSE](LICENSE). Third-party dependencies retain their own licenses.
