"""Home Assistant player control and live browser-audio stream."""

import json
import os
import secrets
import subprocess
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
HA_API = "http://supervisor/core/api"
try:
    OPTIONS = json.loads(Path("/data/options.json").read_text())
except (OSError, json.JSONDecodeError):
    OPTIONS = {}
STREAM_BASE_URL = OPTIONS.get("stream_base_url", "").rstrip("/")
STREAM_KEYS = {}


def ha_request(path, method="GET", payload=None):
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        HA_API + path,
        data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read()
    return json.loads(raw) if raw else None


def media_players():
    states = ha_request("/states") or []
    return [state for state in states if state.get("entity_id", "").startswith("media_player.")]


def stream_base(handler):
    """Use configured LAN URL or infer the Home Assistant host from ingress."""
    if STREAM_BASE_URL:
        return STREAM_BASE_URL
    forwarded = handler.headers.get("X-Forwarded-Host") or handler.headers.get("Host", "")
    host = urlparse("//" + forwarded.split(",", 1)[0].strip()).hostname or ""
    if not host:
        raise ValueError("Setze in den Add-on-Optionen stream_base_url auf die erreichbare HA-Adresse, z. B. http://192.168.1.20:8099")
    return f"http://{host}:8099"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/players":
            try:
                players = [
                    {"entity_id": p["entity_id"], "name": p.get("attributes", {}).get("friendly_name", p["entity_id"])}
                    for p in media_players()
                ]
                return self.send_json({"players": players})
            except Exception as err:
                return self.send_json({"error": str(err)}, 502)

        if self.path.startswith("/live/") and self.path.endswith(".mp3"):
            key = self.path[6:-4]
            expires = STREAM_KEYS.get(key, 0)
            if not expires or expires < time.time():
                return self.send_error(404)
            return self.stream_browser_audio()
        return self.send_error(404)

    def stream_browser_audio(self):
        """Capture Chromium's virtual PulseAudio output and stream it as MP3."""
        command = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
            "-f", "pulse", "-fragment_size", "4096", "-i", "ytmusic.monitor", "-ac", "2",
            "-codec:a", "libmp3lame", "-b:a", "128k", "-flush_packets", "1",
            "-f", "mp3", "pipe:1",
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Cache-Control", "no-store, no-cache")
        self.send_header("Transfer-Encoding", "chunked")
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            while True:
                chunk = process.stdout.read(2048)
                if not chunk:
                    break
                self.wfile.write(f"{len(chunk):X}\r\n".encode() + chunk + b"\r\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()

    def do_POST(self):
        if self.path != "/api/play":
            return self.send_error(404)
        try:
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            entity_id = data.get("entity_id", "")
            if not entity_id.startswith("media_player."):
                raise ValueError("Bitte wähle einen Media Player.")
            if not any(p.get("entity_id") == entity_id for p in media_players()):
                raise ValueError("Der ausgewählte Media Player wurde in Home Assistant nicht gefunden.")

            # Expire old URLs and keep this process's temporary endpoint list small.
            now = time.time()
            for old_key in [key for key, expiry in STREAM_KEYS.items() if expiry < now]:
                STREAM_KEYS.pop(old_key, None)
            key = secrets.token_urlsafe(24)
            STREAM_KEYS[key] = now + 6 * 60 * 60
            url = f"{stream_base(self)}/live/{key}.mp3"

            ha_request("/services/media_player/play_media", "POST", {
                "entity_id": entity_id,
                "media_content_id": url,
                "media_content_type": "audio/mpeg",
                "extra": {"stream_type": "LIVE"},
            })
            return self.send_json({"ok": True, "url": url})
        except Exception as err:
            return self.send_json({"error": str(err)}, 400)

    def log_message(self, *_):
        pass


if not TOKEN:
    raise RuntimeError("Supervisor-Token fehlt. Starte das Add-on über Home Assistant Supervisor.")
ThreadingHTTPServer(("0.0.0.0", 8098), Handler).serve_forever()
