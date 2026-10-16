import asyncio
import json
import os
import queue
import threading
import time
import traceback
import re
import unicodedata
from collections import deque
from pathlib import Path

APP_DIR = Path(os.getenv('APPDATA', str(Path.home() / '.config'))) / 'LiveVoice'
APP_DIR.mkdir(parents=True, exist_ok=True)
SOUNDS_DIR = APP_DIR / 'sounds'
SOUNDS_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = APP_DIR / 'settings.json'
GIFTED_FILE = APP_DIR / 'gifted_users.json'
LOG_FILE = APP_DIR / 'livevoice.log'
DEFAULTS = {
    'username': '', 'chat_tts': True, 'follow_alert': True, 'follow_sound': '',
    'gift_alert': True, 'gift_sound': '', 'gift_speak': False,
    'voice': 'en-US-AriaNeural', 'volume': 0.8, 'cooldown': 3,
    'filter_enabled': True, 'filter_profanity': True,
    'filter_urls': True, 'filter_max_chars': 180,
    'filter_blocked_terms': '', 'filter_repeated': True,
}


# Conservative built-in word list. Custom terms are editable in the dashboard.
BUILTIN_TERMS = ('fuck', 'shit', 'bitch', 'cunt', 'nigger', 'faggot', 'retard')
LEET = str.maketrans({'0':'o','1':'i','3':'e','4':'a','5':'s','7':'t','8':'b','@':'a','$':'s','!':'i'})
ZERO_WIDTH = {chr(n) for n in (0x200b,0x200c,0x200d,0x2060,0xfeff)}
URL_RE = re.compile(r'(?i)(?:https?://|www\.|\b[a-z0-9-]+\.(?:com|net|org|gg|io|tv|co|ru|xyz)\b)')


def normalize(text):
    """Return both spaced and joined forms for obfuscated-word checks."""
    text = unicodedata.normalize('NFKC', str(text)).casefold()
    text = ''.join(ch for ch in text if ch not in ZERO_WIDTH and unicodedata.category(ch) != 'Cf')
    text = text.translate(LEET)
    # Break up punctuation, emojis and symbols; keep letters/digits in all scripts.
    spaced = ''.join(ch if ch.isalnum() else ' ' for ch in text)
    spaced = re.sub(r'\s+', ' ', spaced).strip()
    # Collapse excessive character stretching (e.g. shiiiit).
    squashed = re.sub(r'(.)\1{2,}', r'\1', spaced)
    return spaced, squashed


def blocked_reason(text, settings):
    if not settings.get('filter_enabled', True):
        return None
    if len(text) > int(settings.get('filter_max_chars', 180)):
        return 'message too long'
    if settings.get('filter_urls', True) and URL_RE.search(text):
        return 'URL'
    terms = []
    if settings.get('filter_profanity', True):
        terms.extend(BUILTIN_TERMS)
    terms.extend(x.strip() for x in str(settings.get('filter_blocked_terms', '')).splitlines() if x.strip())
    spaced, squashed = normalize(text)
    for term in terms:
        term_spaced, _ = normalize(term)
        if not term_spaced:
            continue
        # Word-boundary checks prevent matching innocuous substrings.
        # Joining across punctuation catches f.u.c.k, f u c k, etc.
        term_joined = term_spaced.replace(' ', '')
        for candidate in (spaced, squashed):
            if re.search(r'(?<!\w)' + re.escape(term_spaced) + r'(?!\w)', candidate):
                return 'blocked phrase'
            words = candidate.split()
            for i in range(len(words)):
                combined = ''
                for word in words[i:i+min(16, len(term_joined)+2)]:
                    combined += word
                    if len(combined) >= len(term_joined):
                        if combined == term_joined:
                            return 'obfuscated phrase'
                        break
    return None

def user_key(user):
    """Stable viewer key for cooldowns and repeat detection."""
    for field in ('user_id', 'id', 'unique_id', 'sec_uid'):
        value = getattr(user, field, None)
        if value is not None and str(value).strip():
            return str(value)
    return ''


class Engine:
    def __init__(self):
        try:
            self.settings = {**DEFAULTS, **{k: v for k, v in json.loads(SETTINGS_FILE.read_text('utf-8')).items() if k in DEFAULTS}}
        except (OSError, ValueError):
            self.settings = dict(DEFAULTS)
        self.status = 'Disconnected'
        self.events = []
        self.queue = queue.Queue(maxsize=100)
        self.client = None
        self.loop = None
        self.generation = 0
        self.last_message = {}
        self.recent_text = {}
        self.audio_lock = threading.Lock()
        self.state_lock = threading.RLock()
        threading.Thread(target=self._audio_worker, daemon=True).start()

    def save(self, changes):
        with self.state_lock:
            for key, value in changes.items():
                if key in DEFAULTS:
                    self.settings[key] = value
            SETTINGS_FILE.write_text(json.dumps(self.settings, indent=2), 'utf-8')
            return dict(self.settings)

    def log(self, message):
        with self.state_lock:
            self.events.insert(0, str(message))
            del self.events[100:]
        print('[LiveVoice]', message, flush=True)
        try:
            with LOG_FILE.open('a', encoding='utf-8') as log_file:
                log_file.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} | {message}\n')
        except OSError:
            pass

    def snapshot(self):
        with self.state_lock:
            return {'settings': dict(self.settings), 'status': self.status,
                    'events': list(self.events[:50])}

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
                    if kind == 'tts':
                        import edge_tts
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                            path = Path(tmp.name)
                        try:
                            asyncio.run(edge_tts.Communicate(str(text), self.settings['voice']).save(str(path)))
                            pygame.mixer.music.load(str(path))
                            pygame.mixer.music.set_volume(float(self.settings['volume']))
                            pygame.mixer.music.play()
                            while pygame.mixer.music.get_busy():
                                pygame.time.wait(80)
                            pygame.mixer.music.unload()
                        finally:
                            path.unlink(missing_ok=True)
                    else:
                        pygame.mixer.music.load(str(text))
                        pygame.mixer.music.set_volume(float(self.settings['volume']))
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            pygame.time.wait(80)
                        pygame.mixer.music.unload()
            except Exception as exc:
                self.log(f'Audio error: {exc}')
            finally:
                self.queue.task_done()

    def _sound(self, setting):
        filename = self.settings.get(setting, '')
        path = SOUNDS_DIR / filename
        if filename and path.is_file() and path.parent == SOUNDS_DIR:
            self.enqueue('sound', path)

    def connect(self, username):
        username = username.strip().lstrip('@')
        if not username:
            raise ValueError('Enter a TikTok username')
        with self.state_lock:
            if self.status in ('Connecting', 'Connected'):
                return
            self.generation += 1
            generation = self.generation
            self.status = 'Connecting'
        self.save({'username': username})
        self.log(f'Connecting to @{username}...')
        threading.Thread(target=self._run_tiktok, args=(username, generation), daemon=True).start()

    def _run_tiktok(self, username, generation):
        try:
            from TikTokLive import TikTokLiveClient
            from TikTokLive.events import ConnectEvent, CommentEvent, FollowEvent, GiftEvent, DisconnectEvent
            client = TikTokLiveClient(unique_id='@' + username)
            with self.state_lock:
                if generation != self.generation:
                    return
                self.client = client
                self.loop = asyncio.new_event_loop()
                loop = self.loop

            @client.on(ConnectEvent)
            async def on_connect(event):
                with self.state_lock:
                    if generation != self.generation:
                        return
                    self.status = 'Connected'
                self.log(f'Connected to @{username} (room {client.room_id})')

            @client.on(CommentEvent)
            async def on_comment(event):
                if generation != self.generation:
                    return
                user = event.user
                name = str(getattr(user, 'nickname', 'Viewer'))[:60]
                comment = str(getattr(event, 'comment', ''))[:240]
                self.log(f'COMMENT | {name}: {comment}')
                if not self.settings['chat_tts'] or not comment:
                    return
                reason = blocked_reason(comment, self.settings) or blocked_reason(name, self.settings)
                if reason:
                    self.log(f'TTS BLOCKED | {name}: {reason}')
                    return
                key = user_key(user) or name
                now = time.monotonic()
                if now - self.last_message.get(key, 0) < float(self.settings['cooldown']):
                    self.log(f'TTS SKIPPED | {name}: cooldown')
                    return
                normalized = normalize(comment)[1]
                if self.settings.get('filter_enabled', True) and self.settings.get('filter_repeated', True):
                    last = self.recent_text.get(key)
                    if last and last[0] == normalized and now - last[1] < 120:
                        self.log(f'TTS BLOCKED | {name}: repeated message')
                        return
                self.recent_text[key] = (normalized, now)
                self.last_message[key] = now
                self.log(f'TTS QUEUED | {name}')
                self.enqueue('tts', f'{name} says {comment}')

            @client.on(FollowEvent)
            async def on_follow(event):
                if generation != self.generation:
                    return
                name = str(getattr(event.user, 'nickname', 'Someone'))[:60]
                self.log(f'FOLLOW | {name}')
                if self.settings['follow_alert']:
                    self._sound('follow_sound')

            @client.on(GiftEvent)
            async def on_gift(event):
                if generation != self.generation:
                    return
                user = event.user
                if getattr(event, 'streaking', False):
                    return  # Announce only the final streak event.
                name = str(getattr(user, 'nickname', 'Someone'))[:60]
                gift = getattr(event, 'gift', None)
                gift_name = str(getattr(gift, 'name', 'a gift'))[:80]
                count = max(1, int(getattr(event, 'repeat_count', 1) or 1))
                self.log(f'GIFT | {name}: {count}x {gift_name}')
                if self.settings['gift_alert']:
                    self._sound('gift_sound')
                    if self.settings['gift_speak']:
                        self.enqueue('tts', f'Thank you {name} for {count} {gift_name}')

            @client.on(DisconnectEvent)
            async def on_disconnect(event):
                if generation == self.generation:
                    self.status = 'Disconnected'
                    self.log('TikTok disconnected')

            self.log('TikTok connector initialized; waiting for LIVE connection...')
            asyncio.set_event_loop(loop)
            loop.run_until_complete(client.connect())
            self.log('TikTok connection ended')
        except Exception as exc:
            self.log(f'Connection error: {type(exc).__name__}: {exc}')
            traceback.print_exc()
        finally:
            with self.state_lock:
                if generation == self.generation:
                    self.status = 'Disconnected'
                    self.client = None
                    self.loop = None
            if 'loop' in locals():
                try:
                    loop.close()
                except Exception:
                    pass
            self.log('TikTok worker stopped')

    def disconnect(self):
        with self.state_lock:
            self.generation += 1
            client, loop = self.client, self.loop
            self.client = None
            self.status = 'Disconnected'
        if client is not None and loop is not None and loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(client.disconnect(), loop).result(timeout=5)
            except Exception as exc:
                self.log(f'Disconnect warning: {exc}')
        self.log('Disconnected by user')

    def mute(self):
        with self.queue.mutex:
            self.queue.queue.clear()
            self.queue.unfinished_tasks = min(self.queue.unfinished_tasks, 1)
            if not self.queue.unfinished_tasks:
                self.queue.all_tasks_done.notify_all()
        try:
            import pygame
            pygame.mixer.music.stop()
        except Exception:
            pass

engine = Engine()
