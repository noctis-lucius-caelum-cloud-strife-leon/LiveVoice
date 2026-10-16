"""Launch LiveVoice in an embedded window or in the system browser."""
import argparse
import socket
import threading
import time
import webbrowser

import uvicorn
from .server import app


def main():
    parser = argparse.ArgumentParser(description='LiveVoice launcher')
    parser.add_argument('--browser', action='store_true', help='Open the dashboard in a regular browser (no Qt/GTK required)')
    parser.add_argument('--no-open', action='store_true', help='Print the URL without opening a browser (requires --browser)')
    args = parser.parse_args()
    if args.no_open and not args.browser:
        parser.error('--no-open requires --browser')

    # Select an available loopback port. Uvicorn owns the socket after startup.
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    url = f'http://127.0.0.1:{port}'

    if args.browser:
        config = uvicorn.Config(app, host='127.0.0.1', port=port, log_level='info')
        server = uvicorn.Server(config)
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        for _ in range(100):
            if server.started:
                break
            if not thread.is_alive():
                raise RuntimeError('Local server exited during startup')
            time.sleep(0.1)
        if not server.started:
            raise RuntimeError('Local server did not start')
        print(f'LiveVoice running at {url} (Ctrl+C to exit)', flush=True)
        if not args.no_open:
            webbrowser.open(url)
        try:
            while thread.is_alive():
                thread.join(timeout=0.5)
        except KeyboardInterrupt:
            print('\nStopping LiveVoice...', flush=True)
        finally:
            server.should_exit = True
            thread.join(timeout=5)
        return

    # Keep the original embedded desktop experience for Windows users.
    thread = threading.Thread(target=lambda: uvicorn.run(app, host='127.0.0.1', port=port, log_level='info'), daemon=True)
    thread.start()
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
        webbrowser.open(url)
        print(f'LiveVoice running at {url}; Ctrl+C to exit')
        try:
            thread.join()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
