# LiveVoice

**LiveVoice** is a free, open-source TikTok LIVE text-to-speech and sound-alert application.

It reads live chat messages aloud, plays customizable sounds when someone follows or sends a gift, and filters unwanted messages before they reach your speakers.

Designed for streamers who want a lightweight, customizable alternative to subscription-based TTS and alert tools.

## Features

### TikTok LIVE Integration
- Connect to a TikTok LIVE stream using a username.
- Receive live chat messages, follows, and gifts.
- Automatically reconnecting is not yet guaranteed.

### Text-to-Speech
- Read incoming chat messages aloud.
- Select from supported Microsoft Edge TTS voices.
- Adjust speech volume.
- Configure a cooldown between messages.
- Queue speech to avoid overlapping playback.
- Test TTS directly from the dashboard.

### Chat Filtering
- Built-in profanity and offensive-language filtering.
- Detect common attempts to disguise blocked words using spacing, punctuation, repeated letters, and character substitutions.
- Custom blocked words and phrases.
- URL and domain blocking.
- Maximum message length.
- Duplicate-message protection.
- Username filtering.

Filtering is configurable and designed to reduce TTS abuse, but no automated filter can guarantee that every offensive message will be caught.

### Sound Alerts
- Play a custom sound when someone follows.
- Play a custom sound when someone sends a gift.
- Handle repeating gift streaks to reduce duplicate alerts.
- Enable or disable supported features independently.

### Dashboard
- Local browser-based interface.
- Configure TTS, filters, and alerts.
- Connect to a LIVE stream without using terminal commands inside the dashboard.
- View connection status and recent activity.

## Installation

### Windows

A Windows installer is planned.

Once the Windows build is successfully produced and tested, users will be able to download `LiveVoice-Setup.exe` from the project's GitHub Releases page.

The goal is to require **no separate Python installation, virtual environment, or command-line setup**.

**Note:** The Windows installer has not yet been verified. Until then, use the source installation instructions below.

### Linux / Development

Requires Python 3.12 or another compatible Python 3 version.

Clone the repository:

```bash
git clone https://github.com/noctis-lucius-caelum-cloud-strife-leon/LiveVoice.git
cd LiveVoice
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch LiveVoice in browser mode:

```bash
python -m livevoice.main --browser
```

The dashboard should open in your default web browser.

On Linux, browser mode avoids requiring the GTK or Qt libraries used by the desktop window.

## Usage

1. Start LiveVoice.
2. Enter the TikTok username of the account broadcasting LIVE.
3. Click **Connect**.
4. Enable chat TTS and configure your preferred voice and volume.
5. Configure follower and gift alert sounds.
6. Set up chat filtering and custom blocked phrases.
7. Save your settings.

The broadcaster must be LIVE for the TikTok connection to receive live events.

## Building for Windows

LiveVoice uses **PyInstaller** to bundle the Python application and its dependencies, and **Inno Setup** to produce a Windows installer.

The repository includes packaging configuration intended for GitHub Actions.

To build the installer:

1. Push the project and packaging files to GitHub.
2. Open the repository's **Actions** tab.
3. Run the Windows installer build workflow.
4. Download the resulting build artifact.

The Windows build process still requires testing on a Windows environment.

## Technology

- **Python** — application backend
- **TikTokLive** — unofficial TikTok LIVE integration
- **edge-tts** — text-to-speech
- **pygame** — audio playback
- **FastAPI / Uvicorn** — local backend API
- **HTML, CSS, JavaScript** — dashboard
- **PyInstaller** — application packaging
- **Inno Setup** — Windows installation

## Privacy

LiveVoice runs locally and does not require a LiveVoice account.

It processes public LIVE chat and event data to provide TTS and sound alerts. Diagnostic logs may contain usernames, chat messages, and event information.

TikTokLive and edge-tts may communicate with external services to perform their respective functions.

Do not publish personal settings, logs, or other private runtime files in your GitHub repository.

## Known Limitations

- TikTokLive is an unofficial library and may break if TikTok changes its systems.
- Gift and follow events depend on the data made available by TikTok.
- Automated chat filtering is not foolproof.
- Internet connectivity is required for TikTok LIVE integration and online TTS.
- Windows installer compatibility has not yet been fully tested.

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

If you encounter a problem, open a GitHub issue with:
- Your operating system
- Your Python version, if running from source
- Steps to reproduce the problem
- Relevant error messages, with personal information removed

## License

LiveVoice is released under the **MIT License**. See [LICENSE](LICENSE) for details.

## Disclaimer

LiveVoice is an independent, unofficial project and is not affiliated with, endorsed by, or sponsored by TikTok or ByteDance.

TikTok is a trademark of its respective owner.
