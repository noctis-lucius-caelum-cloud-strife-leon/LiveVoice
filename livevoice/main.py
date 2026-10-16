import socket
import threading
import time
import uvicorn
from .server import app

def main():
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    thread = threading.Thread(target=lambda: uvicorn.run(app, host='127.0.0.1', port=port, log_level='warning'), daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{port}'
    for _ in range(60):
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.1):
                break
        except OSError:
            time.sleep(0.1)
    try:
        import webview
        webview.create_window('LiveVoice', url, width=1080, height=800, min_size=(750, 580))
        webview.start()
    except ImportError:
        import webbrowser
        webbrowser.open(url)
        print(f'LiveVoice running at {url}; Ctrl+C to exit')
        thread.join()

if __name__ == '__main__':
    main()
