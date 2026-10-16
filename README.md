# LiveVoice

**Free, open-source TikTok LIVE text-to-speech and sound alerts.**

LiveVoice is a lightweight application that reads TikTok LIVE chat messages aloud and plays customizable sounds when viewers follow or send gifts.

It includes chat filtering, voice customization, and a simple local dashboard. No subscriptions, API keys, or TikTok login required.

## Features

### 💬 Live Chat Text-to-Speech
- Automatically reads TikTok LIVE comments aloud.
- Multiple Microsoft Edge TTS voices.
- Adjustable TTS volume and message cooldown.
- Queued audio playback to prevent overlapping messages.
- Built-in TTS testing.

### 🛡️ Chat Filtering
- Custom blocked words and phrases.
- Detection of common text obfuscation techniques, including spacing, punctuation, repeated letters, and character substitutions.
- URL and domain blocking.
- Maximum message length.
- Duplicate-message protection.
- Username filtering.

**Note:** No automated filter is perfect. LiveVoice provides an additional layer of protection, not a replacement for TikTok's moderation tools.

### 🔊 Sound Alerts
- **Follower alerts:** Play a customizable sound when someone follows.
- **Gift alerts:** Play a customizable sound when someone sends a gift.
- Supports custom MP3 sound files.
- Gift streak handling to reduce duplicate alerts.
- Independently enable or disable chat TTS, follower alerts, and gift alerts.

**Note:** Sound files must currently be selected manually. LiveVoice does not automatically assign default alert sounds.

### 🖥️ Local Dashboard
- Configure LiveVoice through a browser-based interface.
- Connect to a LIVE stream using a TikTok username.
- Customize voices, sounds, volume, and filtering.
- View connection status and recent events.

## Installation

### Windows (Recommended)

1. Open the repository's [Releases](https://github.com/noctis-lucius-caelum-cloud-strife-leon/LiveVoice/releases) page.
2. Download `LiveVoice-Setup.exe` from the latest release, if available.
3. Run the installer.
4. Launch LiveVoice from the Start menu or desktop shortcut.
5. The dashboard opens in your default browser.

**No Python installation or virtual environment is required.**

**Important:** LiveVoice currently opens a console window alongside the dashboard. Keep this window open while using the application. Closing it will stop LiveVoice.

Windows may display a SmartScreen warning because the application is not code-signed.

### Linux / Running from Source

Python 3.11 or newer is recommended.

Clone the repository:

```bash
git clone https://github.com/noctis-lucius-caelum-cloud-strife-leon/LiveVoice.git
cd LiveVoice
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Start LiveVoice:

```bash
python -m livevoice.main --browser
```

Browser mode avoids the need for additional GTK or Qt desktop dependencies.

## How to Use

1. Launch LiveVoice.
2. Enter the TikTok username of the account currently broadcasting LIVE.
3. Click **Connect**.
4. Enable chat TTS and choose your preferred voice.
5. Configure follower and gift sound alerts.
6. Adjust chat filtering as needed.
7. Save your settings.

LiveVoice must remain running to receive LIVE events and play sounds.

## Building the Windows Installer

The Windows installer is built automatically using GitHub Actions.

The build uses:

- **PyInstaller** to bundle the Python application and its dependencies.
- **Inno Setup** to create the Windows installer.
- **GitHub Actions** to build on a Windows runner.

To build your own installer:

1. Fork or clone the repository.
2. Open the **Actions** tab on GitHub.
3. Select **Build Windows installer**.
4. Click **Run workflow**.
5. Download the installer artifact after the workflow completes.

The workflow also produces a portable Windows build.

The current working Windows configuration uses PyInstaller's `--console` option.

## Technology Stack

| Component | Technology |
|---|---|
| Application backend | Python |
| TikTok LIVE integration | TikTokLive |
| Text-to-speech | edge-tts |
| Audio playback | pygame |
| Local API | FastAPI / Uvicorn |
| Dashboard | HTML, CSS, JavaScript |
| Windows executable | PyInstaller |
| Windows installer | Inno Setup |

## Known Limitations

- The Windows application currently requires its console window to remain open.
- The application requires an internet connection.
- TTS filtering cannot catch every offensive or deliberately disguised message.
- TikTok LIVE connectivity depends on an unofficial third-party library.
- Some antivirus products or Windows SmartScreen may flag unsigned executables.

## Contributing

Contributions, bug reports, and suggestions are welcome!

If you encounter a bug, please [open an issue](https://github.com/noctis-lucius-caelum-cloud-strife-leon/LiveVoice/issues) and include your operating system, steps to reproduce the problem, and relevant error messages.

Please remove personal information from logs before sharing them.

## License

LiveVoice is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## Disclaimer

LiveVoice is an independent, unofficial application and is not affiliated with, endorsed by, or sponsored by TikTok or ByteDance.

TikTok is a trademark of its respective owner.
