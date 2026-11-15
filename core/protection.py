import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.scanner import ScanEngine
from core.quarantine import add_to_quarantine
from core.config import load_config

class ThreatHandler(FileSystemEventHandler):
    def __init__(self, on_threat_cb=None):
        super().__init__()
        self.on_threat_cb = on_threat_cb
        self.engine = ScanEngine()
        self._recent = set()

    def _check(self, path: str):
        cfg = load_config()
        if not cfg.get("rt_enabled", True):
            return

        p = Path(path)
        if not p.is_file():
            return

        for exc in cfg.get("exclusions", []):
            if exc.lower() in str(p).lower():
                return

        if str(p) in self._recent:
            return
        self._recent.add(str(p))
        if len(self._recent) > 100:
            self._recent.clear()

        res = self.engine._analyze_file(p)
        if res:
            res["reason"] = "Real-Time Protection: " + res["reason"]
            add_to_quarantine(res)
            if self.on_threat_cb:
                self.on_threat_cb(res)

    def on_created(self, event):
        if not event.is_directory:
            self._check(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._check(event.src_path)

class RealTimeProtection:
    def __init__(self, on_threat_cb=None):
        self.observer = Observer()
        self.handler = ThreatHandler(on_threat_cb)
        self.active = False

    def start(self):
        if self.active:
            return
        
        cfg = load_config()
        if not cfg.get("rt_enabled", True):
            return

        # Мониторим только безопасные папки (без Temp, чтобы не лагало)
        paths = [
            Path.home() / "Downloads",
            Path.home() / "Desktop"
        ]
        
        for p in paths:
            if p.exists():
                self.observer.schedule(self.handler, str(p), recursive=True)
        
        self.observer.start()
        self.active = True

    def stop(self):
        if self.active:
            self.observer.stop()
            self.observer.join()
            self.active = False
