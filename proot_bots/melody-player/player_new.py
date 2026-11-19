#!/usr/bin/env python3
"""Sk.Team Music Player - clean rewrite"""
import asyncio, os, sys, json, re, hashlib, urllib.request, traceback
from pathlib import Path

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

import httpx
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, AudioQuality
import yt_dlp

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION = os.environ["TG_SESSION_STRING"]
BASE_URL = os.environ.get("PLAYER_BASE_URL", "https://project--b8962080-6b65-4712-a6ea-051e02bdecb9-dev.lovable.app/api/public")
API_KEY = os.environ["PLAYER_API_KEY"]
DEFAULT_CHAT = int(os.environ.get("PLAYER_CHAT_ID", "-1004349813270"))

CACHE = Path("/root/melody-player/cache")
CACHE.mkdir(parents=True, exist_ok=True)
HEADERS = {"X-Api-Key": API_KEY}
POLL_SEC = 2

def log(*a):
    sys.stderr.write(" ".join(str(x) for x in a) + "\n")
    sys.stderr.flush()

# ─── Download ───
def _clean(q):
    for p in ("ytsearch1:", "ytsearch2:", "ytsearch:", "scsearch1:", "scsearch2:", "scsearch:"):
        if q.startswith(p): return q[len(p):].strip()
    return q.strip()

def _title_from_yt(url):
    m = re.search(r"(?:v=|youtu.be/)([A-Za-z0-9_-]{11})", url)
    if not m: return ""
    api = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={m.group(1)}&format=json"
    try:
        req = urllib.request.Request(api, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("title", "") or ""
    except Exception as e:
        log(f"oembed err: {e}"); return ""

def download(query):
    q = _clean(query)
    if "youtube.com" in q or "youtu.be" in q:
        t = _title_from_yt(q)
        if t: q = t
    final = f"scsearch1:{q}" if not q.startswith("scsearch") else q
    log(f"download: {final}")
    key = hashlib.md5(final.encode()).hexdigest()[:16]
    out = str(CACHE / key)
    opts = {
        "format": "bestaudio/best",
        "outtmpl": out,
        "quiet": True, "no_warnings": True, "noplaylist": True,
        "postprocessors": [{"key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3", "preferredquality": "320"}],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(final, download=True)
        if "entries" in info: info = info["entries"][0]
        path = ydl.prepare_filename(info)
        p = Path(path)
        if not p.exists(): p = p.with_suffix(".mp3")
        return str(p), info.get("title", q), info.get("duration", 0)

# ─── Handle ───
async def handle(cmd, calls):
    if not isinstance(cmd, dict): return
    action = (cmd.get("action") or cmd.get("type") or "").lower()
    chat_id = int(cmd.get("chat_id", DEFAULT_CHAT))
    log(f">>> {action} chat={chat_id}")

    if action in ("play_next", "play", "add"):
        q = cmd.get("source_url") or cmd.get("title") or cmd.get("query") or cmd.get("args")
        if not q: log("no query"); return
        try:
            path, title, dur = await asyncio.to_thread(download, q)
            log(f"ok: {title} ({dur}s) -> {path}")
            stream = MediaStream(path, audio_parameters=AudioQuality.STUDIO,
                                 video_flags=MediaStream.Flags.IGNORE)
            await calls.play(chat_id, stream)
            log(f"✅ PLAYING: {title}")
        except Exception as e:
            log(f"❌ {e}"); log(traceback.format_exc())
    elif action == "pause":
        try: await calls.pause(chat_id); log("paused")
        except Exception as e: log(f"err {e}")
    elif action == "resume":
        try: await calls.resume(chat_id); log("resumed")
        except Exception as e: log(f"err {e}")
    elif action == "stop":
        try: await calls.leave_call(chat_id); log("left")
        except Exception as e: log(f"err {e}")
    elif action == "mute":
        try: await calls.mute(chat_id); log("muted")
        except Exception as e: log(f"err {e}")
    elif action == "unmute":
        try: await calls.unmute(chat_id); log("unmuted")
        except Exception as e: log(f"err {e}")
    elif action == "skip":
        log("skip noted")
    else:
        log(f"unknown: {action}")

# ─── Poll ───
async def poll_loop(calls):
    async with httpx.AsyncClient(timeout=20) as h:
        n = 0
        while True:
            try:
                r = await h.get(f"{BASE_URL}/mgmt/player/commands", headers=HEADERS)
                if r.status_code == 200:
                    d = r.json()
                    cmds = d if isinstance(d, list) else (d.get("commands", []) if isinstance(d, dict) else [])
                    if cmds:
                        log(f"poll #{n}: {len(cmds)} cmds")
                        for c in cmds:
                            try: await handle(c, calls)
                            except Exception as e: log(f"cmd err: {e}")
                    n += 1
                    if n % 30 == 0: log(f"heartbeat #{n}")
                else:
                    log(f"poll status {r.status_code}")
            except Exception as e:
                log(f"poll err: {e}")
            await asyncio.sleep(POLL_SEC)

# ─── Main ───
async def main():
    log("=== START ===")
    log(f"session len: {len(SESSION)}")
    app = Client(name="player_new", api_id=API_ID, api_hash=API_HASH,
                 session_string=SESSION, workdir="/root/melody-player")
    calls = PyTgCalls(app)

    try:
        @calls.on_update()
        async def _on_update(client, update):
            log(f"update: {type(update).__name__}")
    except Exception as e:
        log(f"update handler err: {e}")

    log("pyrogram start...")
    await app.start()
    log("pyrogram ok")
    me = await app.get_me()
    log(f"me: id={me.id} @{me.username}")

    log("pytgcalls start...")
    await calls.start()
    log("pytgcalls ok")

    log("entering poll loop")
    try:
        await poll_loop(calls)
    except KeyboardInterrupt:
        pass
    finally:
        log("shutdown")
        try: await app.stop()
        except: pass

if __name__ == "__main__":
    try: _loop.run_until_complete(main())
    except Exception as e:
        log(f"FATAL: {e}"); log(traceback.format_exc())
