import asyncio
import json
import os
import queue
import threading
from pathlib import Path

APP_DIR = Path(os.getenv('APPDATA', str(Path.home() / '.config'))) / 'LiveVoice'
APP_DIR.mkdir(parents=True, exist_ok=True)
SOUNDS_DIR = APP_DIR / 'sounds'
SOUNDS_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = APP_DIR / 'settings.json'
DEFAULTS = {'username': '', 'chat_tts': True, 'follow_alert': True, 'follow_sound': '', 'voice': 'en-US-AriaNeural', 'volume': 0.8, 'cooldown': 3}

class Engine:
    def __init__(self):
        try:
            self.settings = {**DEFAULTS, **json.loads(SETTINGS_FILE.read_text('utf-8'))}
        except (OSError, ValueError):
            self.settings = dict(DEFAULTS)
        self.status = 'Disconnected'
        self.events = []
        self.queue = queue.Queue(maxsize=100)
        self.stop_event = threading.Event()
        self.client = None
        self.loop = None
        self.last_message = {}
        self.audio_lock = threading.Lock()
        threading.Thread(target=self._audio_worker, daemon=True).start()

    def save(self, changes):
        allowed = DEFAULTS.keys()
        for key, value in changes.items():
            if key in allowed:
                self.settings[key] = value
        SETTINGS_FILE.write_text(json.dumps(self.settings, indent=2), 'utf-8')
        return self.settings

    def log(self, message):
        self.events.insert(0, message)
        del self.events[60:]

    def enqueue(self, kind, text):
        try:
            self.queue.put_nowait((kind, text))
        except queue.Full:
            self.log('Audio queue full; skipped event')

    def _audio_worker(self):
        while True:
            kind, text = self.queue.get()
            try:
                with self.audio_lock:
                    import pygame
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    if kind == 'sound':
                        pygame.mixer.music.load(str(text))
                    else:
                        import edge_tts
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                            path = Path(tmp.name)
                        try:
                            asyncio.run(edge_tts.Communicate(text, self.settings['voice']).save(str(path)))
                            pygame.mixer.music.load(str(path))
                            pygame.mixer.music.set_volume(float(self.settings['volume']))
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy():
                                pygame.time.wait(80)
                            pygame.mixer.music.unload()
                        finally:
                            path.unlink(missing_ok=True)
                        continue
                    pygame.mixer.music.set_volume(float(self.settings['volume']))
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(80)
                    pygame.mixer.music.unload()
            except Exception as exc:
                self.log(f'Audio error: {exc}')
            finally:
                self.queue.task_done()

    def connect(self, username):
        if self.status in ('Connecting', 'Connected'):
            return
        username = username.strip().lstrip('@')
        if not username:
            raise ValueError('Enter a TikTok username')
        self.save({'username': username})
        self.status = 'Connecting'
        threading.Thread(target=self._run_tiktok, args=(username,), daemon=True).start()

    def _run_tiktok(self, username):
        try:
            from TikTokLive import TikTokLiveClient
            from TikTokLive.events import ConnectEvent, CommentEvent, FollowEvent, DisconnectEvent
            client = TikTokLiveClient(unique_id=username)
            self.client = client
            @client.on(ConnectEvent)
            async def on_connect(event):
                self.status = 'Connected'
                self.log(f'Connected to @{username}')
            @client.on(CommentEvent)
            async def on_comment(event):
                name = getattr(event.user, 'nickname', 'Viewer')
                comment = str(event.comment)[:240]
                self.log(f'{name}: {comment}')
                if self.settings['chat_tts']:
                    import time
                    key = getattr(event.user, 'unique_id', name)
                    now = time.monotonic()
                    if now - self.last_message.get(key, 0) >= float(self.settings['cooldown']):
                        self.last_message[key] = now
                        self.enqueue('tts', f'{name} says {comment}')
            @client.on(FollowEvent)
            async def on_follow(event):
                name = getattr(event.user, 'nickname', 'Someone')
                self.log(f'{name} followed')
                if self.settings['follow_alert'] and self.settings['follow_sound']:
                    path = SOUNDS_DIR / self.settings['follow_sound']
                    if path.is_file():
                        self.enqueue('sound', path)
            @client.on(DisconnectEvent)
            async def on_disconnect(event):
                self.status = 'Disconnected'
                self.log('TikTok disconnected')
            asyncio.run(client.start())
        except Exception as exc:
            self.log(f'Connection error: {exc}')
        finally:
            self.status = 'Disconnected'

    def disconnect(self):
        if self.client is not None:
            try:
                self.client.disconnect()
            except Exception as exc:
                self.log(f'Disconnect warning: {exc}')
        self.status = 'Disconnected'

    def mute(self):
        with self.queue.mutex:
            self.queue.queue.clear()
            self.queue.unfinished_tasks = 0
            self.queue.all_tasks_done.notify_all()
        try:
            import pygame
            pygame.mixer.music.stop()
        except Exception:
            pass

engine = Engine()
