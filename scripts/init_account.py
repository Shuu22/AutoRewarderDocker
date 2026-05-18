import json
import os
import re
from datetime import datetime

APP_DIR = os.getenv("APP_DATA_DIR", os.path.expanduser("~/.local/share/AutoRewarder"))


def _clean_account_id(raw: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", (raw or "main").strip())
    return cleaned or "main"


def _to_int(name: str, default: int, min_v: int, max_v: int) -> int:
    raw = os.getenv(name, str(default))
    try:
        val = int(raw)
    except ValueError:
        return default
    return max(min_v, min(val, max_v))


def _to_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


ACCOUNT_ID = _clean_account_id(os.getenv("AR_ACCOUNT_ID", "main"))
ACCOUNT_LABEL = (os.getenv("AR_ACCOUNT_LABEL", "Main") or "Main").strip() or "Main"
Q_PC = _to_int("AR_QUERIES_PC", 30, 0, 130)
Q_MOBILE = _to_int("AR_QUERIES_MOBILE", 20, 0, 99)
S_ENABLED = _to_bool("AR_SCHEDULE_ENABLED", True)

os.makedirs(APP_DIR, exist_ok=True)
acc_dir = os.path.join(APP_DIR, "accounts", ACCOUNT_ID)
os.makedirs(os.path.join(acc_dir, "EdgeProfile"), exist_ok=True)


def rw(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def ww(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


settings_p = os.path.join(APP_DIR, "settings.json")
accounts_p = os.path.join(APP_DIR, "accounts.json")
meta_p = os.path.join(acc_dir, "meta.json")

settings = rw(settings_p, {})
settings.setdefault("hide_browser", True)
settings.setdefault("current_account_id", ACCOUNT_ID)
settings.setdefault("schema_version", 3)
settings.setdefault("autoStartUp", False)
ww(settings_p, settings)

accounts = rw(accounts_p, [])
if not any(a.get("id") == ACCOUNT_ID for a in accounts if isinstance(a, dict)):
    accounts.append(
        {
            "id": ACCOUNT_ID,
            "label": ACCOUNT_LABEL,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
    )
    ww(accounts_p, accounts)

meta = rw(meta_p, {})
meta["first_setup_done"] = True
sched = meta.get("schedule", {}) if isinstance(meta.get("schedule"), dict) else {}
sched.setdefault("enabled", S_ENABLED)
sched.setdefault("advancedScheduling", False)
sched.setdefault("runDuration", 3)
sched.setdefault("queriesPerHour", 10)
sched["queries_pc"] = Q_PC
sched["queries_mobile"] = Q_MOBILE
sched.setdefault("last_triggered_date", None)
meta["schedule"] = sched
ww(meta_p, meta)
print(f"Initialized account={ACCOUNT_ID} label={ACCOUNT_LABEL} at {APP_DIR}")
