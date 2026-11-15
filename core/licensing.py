import json
import secrets
import string
from datetime import datetime, timedelta
from core.config import HOME_DIR, load_config, save_config, get_hwid, sha256

LICENSE_DB = HOME_DIR / "licenses.json"

TARIFS = {
    "trial": {"name": "Trial", "days": 7, "price": 0},
    "monthly": {"name": "Monthly", "days": 30, "price": 149},
    "lifetime": {"name": "Lifetime", "days": None, "price": 300},
}

def _load_db() -> dict:
    if LICENSE_DB.exists():
        try:
            return json.loads(LICENSE_DB.read_text("utf-8"))
        except Exception:
            pass
    return {"keys": {}}

def _save_db(data: dict):
    LICENSE_DB.parent.mkdir(parents=True, exist_ok=True)
    LICENSE_DB.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def issue_key(tarif: str, hwid: str) -> str:
    if tarif not in TARIFS:
        return ""
    
    t = TARIFS[tarif]
    # Генерация ключа формата XXXX-XXXX-XXXX-XXXX
    key = "-".join("".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4)) for _ in range(4))
    
    now = datetime.now()
    if t["days"] is None:
        expires = None
    else:
        expires = (now + timedelta(days=t["days"])).isoformat(timespec="seconds")
        
    db = _load_db()
    db["keys"][key] = {
        "tarif": tarif,
        "hwid": hwid,
        "created": now.isoformat(timespec="seconds"),
        "expires": expires
    }
    _save_db(db)
    return key

def activate_key(key: str) -> dict:
    key = key.strip().upper()
    db = _load_db()
    rec = db["keys"].get(key)
    
    if not rec:
        return {"ok": False, "reason": "Ключ не найден"}
        
    if rec["hwid"] and rec["hwid"] != get_hwid():
        return {"ok": False, "reason": "Ключ привязан к другому ПК"}
        
    if rec["expires"]:
        if datetime.fromisoformat(rec["expires"]) < datetime.now():
            return {"ok": False, "reason": "Срок действия ключа истёк"}
            
    # Сохраняем в конфиг
    cfg = load_config()
    cfg["activated"] = True
    cfg["license_key"] = key
    save_config(cfg)
    
    return {"ok": True, "tarif": rec["tarif"], "expires": rec["expires"]}

def get_license_info() -> dict:
    cfg = load_config()
    if not cfg.get("activated"):
        return {"active": False}
        
    key = cfg.get("license_key", "")
    db = _load_db()
    rec = db["keys"].get(key)
    
    if not rec:
        return {"active": True, "tarif": "unknown"}
        
    return {
        "active": True,
        "tarif": rec["tarif"],
        "expires": rec["expires"],
        "is_lifetime": rec["expires"] is None
    }
