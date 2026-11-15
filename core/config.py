import os
import json
import hashlib
import platform
import uuid
import subprocess
import socket
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "ANTI-VURUS"
APP_VERSION = "3.0.0"
HOME_DIR = Path.home() / ".anti_vurus"
QUARANTINE_DIR = HOME_DIR / "quarantine"
CONFIG_FILE = HOME_DIR / "config.json"
KEY_FILE = HOME_DIR / "license.key"

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = os.getenv("ADMIN_ID", "")

DEFAULT_CONFIG = {
    "activated": False,
    "license_key": "",
    "hwid": "",
    "theme": "dark",
    "rt_enabled": True,
    "exclusions": [],
    "code_hash": "",
    "code_expires": ""
}

def ensure_dirs():
    HOME_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def load_config() -> dict:
    ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            return {**DEFAULT_CONFIG, **json.loads(CONFIG_FILE.read_text("utf-8"))}
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)

def save_config(cfg: dict):
    ensure_dirs()
    tmp = CONFIG_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, CONFIG_FILE)

def get_hwid() -> str:
    cfg = load_config()
    if cfg.get("hwid"):
        return cfg["hwid"]
    
    raw = [platform.node(), platform.machine(), str(uuid.getnode())]
    try:
        out = subprocess.check_output("wmic csproduct get uuid", shell=True, timeout=3).decode(errors="ignore")
        raw.append(out)
    except Exception:
        pass
    hwid = sha256("|".join(raw))[:32]
    cfg["hwid"] = hwid
    save_config(cfg)
    return hwid

def get_pc_name() -> str:
    return socket.gethostname()

def is_activated() -> bool:
    cfg = load_config()
    if not cfg.get("activated"):
        return False
    if cfg.get("hwid") != get_hwid():
        return False
    return True
