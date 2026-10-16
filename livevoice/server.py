import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from .core import engine, SOUNDS_DIR

app = FastAPI(title='LiveVoice local API')
WEB = Path(__file__).resolve().parent.parent / 'web'

class SettingsPayload(BaseModel):
    username: str = ''
    chat_tts: bool = True
    follow_alert: bool = True
    follow_sound: str = ''
    voice: str = 'en-US-AriaNeural'
    volume: float = 0.8
    cooldown: int = 3

class ConnectPayload(BaseModel):
    username: str

@app.get('/')
def index():
    return FileResponse(WEB / 'index.html')

@app.get('/api/state')
def state():
    return {'settings': engine.settings, 'status': engine.status, 'events': engine.events[:30]}

@app.post('/api/settings')
def settings(data: SettingsPayload):
    return engine.save(data.model_dump())

@app.post('/api/connect')
def connect(data: ConnectPayload):
    try:
        engine.connect(data.username)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return {'ok': True}

@app.post('/api/disconnect')
def disconnect():
    engine.disconnect()
    return {'ok': True}

@app.post('/api/test/tts')
def test_tts():
    engine.enqueue('tts', 'Hello from LiveVoice. Your text to speech is working.')
    return {'ok': True}

@app.post('/api/test/follow')
def test_follow():
    path = SOUNDS_DIR / engine.settings['follow_sound']
    if not path.is_file() or path.parent != SOUNDS_DIR:
        raise HTTPException(400, 'Upload a follow sound first')
    engine.enqueue('sound', path)
    return {'ok': True}

@app.post('/api/mute')
def mute():
    engine.mute()
    return {'ok': True}

@app.post('/api/upload/follow')
async def upload_follow(file: UploadFile = File(...)):
    suffix = Path(file.filename or '').suffix.lower()
    if suffix not in ('.mp3', '.wav', '.ogg'):
        raise HTTPException(400, 'Use MP3, WAV, or OGG')
    name = 'follow' + suffix
    path = SOUNDS_DIR / name
    total = 0
    with path.open('wb') as dest:
        while chunk := await file.read(1024 * 1024):
            total += len(chunk)
            if total > 10 * 1024 * 1024:
                path.unlink(missing_ok=True)
                raise HTTPException(413, 'Max sound size is 10 MB')
            dest.write(chunk)
    engine.save({'follow_sound': name})
    return {'filename': name}
