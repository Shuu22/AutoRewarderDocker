import base64
import json
import os
import subprocess
import threading
from datetime import datetime, timezone
from typing import Any

from flask import Flask, Response, jsonify, render_template, request

APP_DIR = os.getenv("APP_DATA_DIR", os.path.expanduser("~/.local/share/AutoRewarder"))
LOG_FILE = os.path.join(APP_DIR, "background_log.txt")
ACCOUNT_ID = os.getenv("AR_ACCOUNT_ID", "main")
WEBUI_HOST = os.getenv("WEBUI_HOST", "0.0.0.0")
WEBUI_PORT = int(os.getenv("WEBUI_PORT", "8080"))
USER = os.getenv("WEBUI_USERNAME", "")
PWD = os.getenv("WEBUI_PASSWORD", "")

app = Flask(__name__)
state: dict[str, Any] = {
    "proc": None,
    "pid": None,
    "started_at": None,
    "finished_at": None,
    "last_exit_code": None,
    "last_status": "idle",
}
lock = threading.Lock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _clamp_int(value: Any, default: int, min_v: int, max_v: int) -> int:
    try:
        v = int(value)
    except (TypeError, ValueError):
        return default
    return max(min_v, min(v, max_v))


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _auth_ok(req) -> bool:
    if not USER or not PWD:
        return True
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Basic "):
        return False
    try:
        raw = base64.b64decode(auth.split(" ", 1)[1]).decode("utf-8")
        u, p = raw.split(":", 1)
    except Exception:
        return False
    return u == USER and p == PWD


def _guard():
    if _auth_ok(request):
        return None
    return Response(
        "Auth required",
        401,
        {"WWW-Authenticate": 'Basic realm="AutoRewarder"'},
    )


def _tail(path: str, lines: int = 300) -> str:
    if not os.path.exists(path):
        return ""
    safe_lines = max(1, min(lines, 2000))
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return "".join(f.readlines()[-safe_lines:])


def _schedule_path() -> str:
    return os.path.join(APP_DIR, "accounts", ACCOUNT_ID, "meta.json")


def _refresh_state_locked() -> None:
    proc = state.get("proc")
    if proc is None:
        return
    rc = proc.poll()
    if rc is None:
        return
    state["last_exit_code"] = rc
    if state.get("last_status") != "stopped":
        state["last_status"] = "success" if rc == 0 else "failed"
    state["finished_at"] = _now_iso()
    state["proc"] = None


def _public_state() -> dict[str, Any]:
    with lock:
        _refresh_state_locked()
        running = state["proc"] is not None
        return {
            "running": running,
            "pid": state["pid"] if running else None,
            "started_at": state["started_at"],
            "finished_at": state["finished_at"],
            "last_exit_code": state["last_exit_code"],
            "last_status": state["last_status"],
            "account_id": ACCOUNT_ID,
        }


@app.route("/")
def index():
    g = _guard()
    if g:
        return g
    return render_template("index.html", auth_enabled=bool(USER and PWD))


@app.get("/api/logs")
def logs():
    g = _guard()
    if g:
        return g
    n = _clamp_int(request.args.get("tail", "300"), 300, 1, 2000)
    return jsonify({"log": _tail(LOG_FILE, n)})


@app.get("/api/status")
def status():
    g = _guard()
    if g:
        return g
    return jsonify(_public_state())


@app.post("/api/run")
def run_now():
    g = _guard()
    if g:
        return g
    body = request.get_json(silent=True) or {}
    pc = _clamp_int(body.get("pc", 30), 30, 0, 130)
    mobile = _clamp_int(body.get("mobile", 20), 20, 0, 99)
    force = _parse_bool(body.get("force", False))

    with lock:
        _refresh_state_locked()
        if state["proc"] is not None:
            return jsonify({"error": "already running"}), 409

        cmd = [
            "python",
            "AutoRewarder_CLI.py",
            "--account",
            ACCOUNT_ID,
            "--pc",
            str(pc),
            "--mobile",
            str(mobile),
        ]
        if force:
            cmd.append("--force")

        os.makedirs(APP_DIR, exist_ok=True)
        logf = open(LOG_FILE, "a", encoding="utf-8")
        p = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT)
        state.update(
            {
                "proc": p,
                "pid": p.pid,
                "started_at": _now_iso(),
                "finished_at": None,
                "last_exit_code": None,
                "last_status": "running",
            }
        )
    return jsonify({"ok": True, "pid": p.pid})


@app.post("/api/stop")
def stop():
    g = _guard()
    if g:
        return g
    with lock:
        _refresh_state_locked()
        p = state.get("proc")
        if p is None:
            return jsonify({"ok": True, "message": "not running"})
        p.terminate()
        state["last_status"] = "stopped"
        state["finished_at"] = _now_iso()
    return jsonify({"ok": True})


@app.get("/api/accounts")
def accounts():
    g = _guard()
    if g:
        return g
    p = os.path.join(APP_DIR, "accounts.json")
    data = []
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    data = loaded
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            data = []
    return jsonify({"accounts": data})


@app.route("/api/schedule", methods=["GET", "POST"])
def schedule():
    g = _guard()
    if g:
        return g
    mp = _schedule_path()
    os.makedirs(os.path.dirname(mp), exist_ok=True)
    meta = {"first_setup_done": True, "schedule": {}}
    if os.path.exists(mp):
        try:
            with open(mp, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    meta = loaded
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            pass
    if request.method == "POST":
        body = request.get_json(silent=True) or {}
        sch = meta.get("schedule", {}) if isinstance(meta.get("schedule"), dict) else {}
        if "enabled" in body:
            sch["enabled"] = _parse_bool(body["enabled"])
        if "advancedScheduling" in body:
            sch["advancedScheduling"] = _parse_bool(body["advancedScheduling"])
        if "runDuration" in body:
            sch["runDuration"] = _clamp_int(body["runDuration"], 3, 1, 24)
        if "queriesPerHour" in body:
            sch["queriesPerHour"] = _clamp_int(body["queriesPerHour"], 10, 1, 99)
        if "queries_pc" in body:
            sch["queries_pc"] = _clamp_int(body["queries_pc"], 30, 0, 130)
        if "queries_mobile" in body:
            sch["queries_mobile"] = _clamp_int(body["queries_mobile"], 20, 0, 99)
        meta["schedule"] = sch
        with open(mp, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
    return jsonify({"schedule": meta.get("schedule", {})})


if __name__ == "__main__":
    app.run(host=WEBUI_HOST, port=WEBUI_PORT)
