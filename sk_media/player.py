#!/usr/bin/env python3
"""Sk.Media Player — Native Termux version"""
import asyncio, os, sys, json, hashlib, traceback
from pathlib import Path

# ═══ Load env از ~/player/player.env ═══
_env_path = Path.home() / "player" / "player.env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

import httpx
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, AudioQuality
import yt_dlp

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION = os.environ["TG_SESSION_STRING"]
SERVER = os.environ.get("SK_SERVER", "http://127.0.0.1:8080")
CACHE = Path.home() / "sk_media" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)
POLL_SEC = 2

def log(*a):
    sys.stderr.write(" ".join(str(x) for x in a) + "\n")
    sys.stderr.flush()

def clean_query(q):
    q = (q or "").strip()
    for p in ("ytsearch1:", "ytsearch2:", "ytsearch:",
              "scsearch1:", "scsearch2:", "scsearch:"):
        if q.startswith(p):
            q = q[len(p):].strip(); break
    return q

def download(query):
    q = clean_query(query)
    final = "scsearch1:" + q if not q.startswith("scsearch") else q
    log(f"[dl] {final}")
    key = hashlib.md5(final.encode()).hexdigest()[:16]
    out = str(CACHE / key)
    opts = {
        "format": "bestaudio/best",
        "outtmpl": out,
        "quiet": True, "no_warnings": True, "noplaylist": True,
        "postprocessors": [{"key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "320"}],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(final, download=True)
        if "entries" in info: info = info["entries"][0]
        path = ydl.prepare_filename(info)
        p = Path(path)
        if not p.exists(): p = p.with_suffix(".mp3")
        return str(p), info.get("title", q), info.get("duration", 0)

async def handle(cmd, calls, h):
    action = (cmd.get("action") or "").lower()
    chat_id = int(cmd.get("chat_id", 0))
    cid = cmd.get("id")
    log(f"[cmd] {action} chat={chat_id}")
    async def report(status, **kw):
        try:
            await h.post(f"{SERVER}/status",
                         json={"id": cid, "chat_id": chat_id, "status": status, **kw})
        except Exception as e:
            log(f"report err: {e}")
    try:
        if action in ("play", "play_next"):
            q = cmd.get("query") or cmd.get("url") or cmd.get("title")
            if not q:
                await report("error", error="no query"); return
            path, title, dur = await asyncio.to_thread(download, q)
            log(f"[dl ok] {title} ({dur}s) -> {path}")
            await report("downloaded", title=title, path=path, duration=dur)
            stream = MediaStream(path, audio_parameters=AudioQuality.STUDIO,
                                 video_flags=MediaStream.Flags.IGNORE)
            await calls.play(chat_id, stream)
            log(f"✅ PLAYING: {title}")
            await report("playing", title=title, duration=dur)
        elif action == "pause":
            await calls.pause(chat_id); await report("paused")
        elif action == "resume":
            await calls.resume(chat_id); await report("playing")
        elif action == "stop":
            try: await calls.leave_call(chat_id)
            except: pass
            await report("stopped")
        elif action == "mute":
            try: await calls.mute(chat_id)
            except: pass
            await report("muted")
        elif action == "unmute":
            try: await calls.unmute(chat_id)
            except: pass
            await report("unmuted")
        else:
            log(f"[cmd] unknown: {action}")
    except Exception as e:
        log(f"❌ {e}")
        log(traceback.format_exc())
        await report("error", error=str(e))

async def poll_loop(calls):
    async with httpx.AsyncClient(timeout=30) as h:
        n = 0
        while True:
            try:
                r = await h.get(f"{SERVER}/commands")
                if r.status_code == 200:
                    cmds = r.json()
                    for c in cmds:
                        await handle(c, calls, h)
                n += 1
                if n % 60 == 0: log(f"[hb] poll#{n}")
            except Exception as e:
                log(f"poll err: {e}")
            await asyncio.sleep(POLL_SEC)

async def main():
    log("=== Sk.Media Player START ===")
    log(f"session len: {len(SESSION)}")
    log(f"server: {SERVER}")
    app = Client(name="sk_player", api_id=API_ID, api_hash=API_HASH,
                 session_string=SESSION, workdir=str(Path.home() / "player"))
    calls = PyTgCalls(app)
    @calls.on_update()
    async def _on_update(client, update):
        log(f"[update] {type(update).__name__}")
    await app.start()
    me = await app.get_me()
    log(f"me: @{me.username} id={me.id}")
    await calls.start()
    log("✅ ready — polling")
    try:
        await poll_loop(calls)
    except KeyboardInterrupt:
        pass
    finally:
        try: await app.stop()
        except: pass

if __name__ == "__main__":
    asyncio.run(main())
