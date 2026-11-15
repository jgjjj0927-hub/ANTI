import json
import shutil
from pathlib import Path
from datetime import datetime
from core.config import QUARANTINE_DIR, HOME_DIR

DB_FILE = HOME_DIR / "quarantine.json"

def _load_db() -> list:
    if DB_FILE.exists():
        try:
            return json.loads(DB_FILE.read_text("utf-8"))
        except Exception:
            pass
    return []

def _save_db(data: list):
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    DB_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def add_to_quarantine(threat: dict) -> bool:
    src = Path(threat["path"])
    if not src.exists():
        return False
        
    q_name = f"{threat['hash'][:16]}_{src.name}.quar"
    dst = QUARANTINE_DIR / q_name
    
    try:
        shutil.move(str(src), str(dst))
    except Exception:
        return False
        
    db = _load_db()
    threat["quarantine_path"] = str(dst)
    threat["date_added"] = datetime.now().isoformat()
    db.append(threat)
    _save_db(db)
    return True

def list_quarantine() -> list:
    return _load_db()

def restore_file(index: int) -> bool:
    db = _load_db()
    if not (0 <= index < len(db)):
        return False
        
    item = db[index]
    q_path = Path(item["quarantine_path"])
    orig_path = Path(item["path"])
    
    if not q_path.exists():
        return False
        
    # Защита от перезаписи
    if orig_path.exists():
        orig_path = orig_path.with_name(orig_path.stem + "_restored" + orig_path.suffix)
        
    try:
        orig_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(q_path), str(orig_path))
        db.pop(index)
        _save_db(db)
        return True
    except Exception:
        return False

def delete_permanently(index: int) -> bool:
    db = _load_db()
    if not (0 <= index < len(db)):
        return False
        
    item = db[index]
    q_path = Path(item["quarantine_path"])
    
    try:
        if q_path.exists():
            q_path.unlink()
        db.pop(index)
        _save_db(db)
        return True
    except Exception:
        return False
