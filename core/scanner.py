import os
import math
import hashlib
import threading
import time
import subprocess
from collections import Counter
from pathlib import Path

class ScanEngine:
    def __init__(self, progress_cb=None, found_cb=None, done_cb=None):
        self.progress_cb = progress_cb
        self.found_cb = found_cb
        self.done_cb = done_cb
        self._stop_event = threading.Event()
        self._thread = None
        self._stopped = False

    def start(self, target_path: str):
        self._stop_event.clear()
        self._stopped = False
        self._thread = threading.Thread(target=self._run_scan, args=(target_path,), daemon=True)
        self._thread.start()

    def stop(self):
        self._stopped = True
        self._stop_event.set()

    def _calc_entropy(self, data: bytes) -> float:
        if not data:
            return 0.0
        entropy = 0.0
        counts = Counter(data)
        length = len(data)
        for count in counts.values():
            p_x = count / length
            entropy += - p_x * math.log2(p_x)
        return entropy

    def _check_signature(self, file_path: Path) -> bool:
        """Проверяет цифровую подпись файла (только Windows)"""
        if os.name != "nt":
            return False
        try:
            cmd = f'powershell -NoProfile -Command "(Get-AuthenticodeSignature \'{file_path}\').Status"'
            out = subprocess.check_output(cmd, shell=True, timeout=5, creationflags=0x08000000).decode(errors="ignore").strip()
            return out == "Valid"
        except Exception:
            return False

    def _analyze_file(self, file_path: Path) -> dict:
        try:
            size = file_path.stat().st_size
            if size == 0 or size > 100 * 1024 * 1024:
                return None
            
            with open(file_path, "rb") as f:
                chunk = f.read(8192)
                
            is_pe = chunk.startswith(b"MZ")
            entropy = self._calc_entropy(chunk)
            dangerous_exts = {".exe", ".dll", ".bat", ".cmd", ".vbs", ".ps1", ".scr"}
            is_dangerous_ext = file_path.suffix.lower() in dangerous_exts
            
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    hasher.update(byte_block)
            file_hash = hasher.hexdigest()
            
            reasons = []
            
            # Эвристика энтропии для PE файлов
            if is_pe and entropy > 7.2:
                # Игнорируем, если файл имеет валидную цифровую подпись (это скорее всего установщик)
                if not self._check_signature(file_path):
                    reasons.append("Высокая энтропия PE (возможная упаковка/шифрование)")
                    
            if is_dangerous_ext and size < 1024:
                reasons.append("Подозрительно маленький размер исполняемого файла")
            
            if reasons:
                return {
                    "path": str(file_path),
                    "name": file_path.name,
                    "severity": "Высокая" if "энтропия" in reasons[0] else "Средняя",
                    "type": "Эвристика",
                    "reason": " | ".join(reasons),
                    "hash": file_hash,
                    "size": size
                }
        except Exception:
            pass
        return None

    def _run_scan(self, target_path: str):
        p = Path(target_path)
        files = []
        
        if p.is_file():
            files = [p]
        elif p.is_dir():
            for root, _, fs in os.walk(p):
                for f in fs:
                    files.append(Path(root) / f)
                    if len(files) >= 10000:
                        break
                if len(files) >= 10000:
                    break
        
        total = max(len(files), 1)
        found = []
        
        for i, file in enumerate(files):
            if self._stop_event.is_set():
                break
                
            res = self._analyze_file(file)
            if res:
                found.append(res)
                if self.found_cb:
                    self.found_cb(res)
            
            if self.progress_cb and i % 5 == 0:
                self.progress_cb(int((i + 1) / total * 100))
                
            time.sleep(0.01)
            
        if self.progress_cb:
            self.progress_cb(100)
        if self.done_cb:
            self.done_cb(found, self._stopped)
