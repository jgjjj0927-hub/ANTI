import json
import requests
from pathlib import Path
from datetime import datetime

from core.config import BOT_TOKEN, ADMIN_ID, load_config, get_hwid, get_pc_name

REG_FILE = Path(__file__).resolve().parent.parent / "bot_registry.json"
STATE_FILE = Path(__file__).resolve().parent.parent / "bot_state.json"

_session = requests.Session()
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def _load_json(p, default):
    if p.exists():
        try: return json.loads(p.read_text("utf-8"))
        except: pass
    return default

def _save_json(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def _api(method, **kw):
    try:
        return _session.post(f"{API}/{method}", json=kw, timeout=5).json()
    except Exception:
        return {}

def send(chat_id, text, kb=None):
    kw = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if kb: kw["reply_markup"] = kb
    return _api("sendMessage", **kw)

def get_main_kb():
    return {"keyboard": [[{"text": "🖥️ Список устройств"}]], "resize_keyboard": True}

def get_auth_kb():
    return {"keyboard": [[{"text": "👤 Пользователь"}, {"text": "🛡️ Администратор"}]], "resize_keyboard": True, "one_time_keyboard": True}

def poll_loop():
    if not BOT_TOKEN: return
    off = 0
    states = _load_json(STATE_FILE, {})
    
    while True:
        try:
            r = _session.get(f"{API}/getUpdates", params={"offset": off, "timeout": 20}, timeout=25).json()
            for u in r.get("result", []):
                off = u["update_id"] + 1
                m = u.get("message")
                if not m or "text" not in m: continue
                
                chat_id = m["chat"]["id"]
                txt = m["text"].strip()
                st = states.get(str(chat_id), {"step": "start"})
                
                if txt == "/start":
                    states[str(chat_id)] = {"step": "role"}
                    _save_json(STATE_FILE, states)
                    send(chat_id, "Выберите роль для входа:", get_auth_kb())
                
                elif st["step"] == "role":
                    if txt == "🛡️ Администратор":
                        states[str(chat_id)] = {"step": "admin_pass"}
                        _save_json(STATE_FILE, states)
                        send(chat_id, "Введите пароль администратора:", {"remove_keyboard": True})
                    elif txt == "👤 Пользователь":
                        states[str(chat_id)] = {"step": "user_key"}
                        _save_json(STATE_FILE, states)
                        send(chat_id, "Введите ваш ключ активации:", {"remove_keyboard": True})
                
                elif st["step"] == "admin_pass":
                    if txt == "11/11/11/7777":
                        states[str(chat_id)] = {"step": "authorized", "role": "admin"}
                        _save_json(STATE_FILE, states)
                        send(chat_id, "✅ Вы вошли как Администратор.", get_main_kb())
                    else:
                        send(chat_id, "❌ Неверный пароль. Попробуйте /start")
                        states[str(chat_id)] = {"step": "start"}
                        _save_json(STATE_FILE, states)
                
                elif st["step"] == "user_key":
                    cfg = load_config()
                    if txt == cfg.get("license_key"):
                        states[str(chat_id)] = {"step": "user_name"}
                        _save_json(STATE_FILE, states)
                        send(chat_id, "Ключ верный. Введите название устройства (например, DESKTOP-1234):")
                    else:
                        send(chat_id, "❌ Неверный ключ. Попробуйте /start")
                        states[str(chat_id)] = {"step": "start"}
                        _save_json(STATE_FILE, states)
                
                elif st["step"] == "user_name":
                    if txt.lower().startswith("desktop-"):
                        reg = _load_json(REG_FILE, {})
                        reg[str(chat_id)] = {"name": txt, "hwid": get_hwid(), "role": "user"}
                        _save_json(REG_FILE, reg)
                        states[str(chat_id)] = {"step": "authorized", "role": "user"}
                        _save_json(STATE_FILE, states)
                        send(chat_id, f"✅ Вы привязаны к {txt}.", get_main_kb())
                    else:
                        send(chat_id, "❌ Имя должно начинаться с 'desktop-'. Повторите:")
                
                elif st["step"] == "authorized" and txt == "🖥️ Список устройств":
                    reg = _load_json(REG_FILE, {})
                    lines = ["<b>Устройства:</b>"]
                    for cid, info in reg.items():
                        lines.append(f"💻 {info['name']} (HWID: {info['hwid'][:8]}...) — В сети")
                    send(chat_id, "\n".join(lines) if len(lines)>1 else "Список пуст.")
        except Exception:
            pass
