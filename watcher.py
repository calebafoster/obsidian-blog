"""
Watchdog daemon: monitors POSTS_DIR for new .md files, then builds and notifies.
Run as a systemd service.
"""
import time
import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import config

SCRIPT_DIR = Path(__file__).parent


class PostHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix != ".md":
            return
        slug = path.stem
        print(f"[watcher] New post detected: {slug}", flush=True)
        try:
            subprocess.run([sys.executable, str(SCRIPT_DIR / "build.py")], check=True)
            print(f"[watcher] Build complete.", flush=True)
        except subprocess.CalledProcessError as e:
            print(f"[watcher] Build failed: {e}", flush=True)
            return
        try:
            subprocess.run([sys.executable, str(SCRIPT_DIR / "notifier.py"), slug], check=True)
            print(f"[watcher] Notifications sent for {slug}.", flush=True)
        except subprocess.CalledProcessError as e:
            print(f"[watcher] Notify failed: {e}", flush=True)


if __name__ == "__main__":
    observer = Observer()
    observer.schedule(PostHandler(), path=config.POSTS_DIR, recursive=False)
    observer.start()
    print(f"[watcher] Watching {config.POSTS_DIR} ...", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
