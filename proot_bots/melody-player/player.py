import asyncio
import os
import time
import logging
from pathlib import Path
import httpx
import yt_dlp
from pyrogram import Client
from pytgcalls import PyTgCalls, filters
from pytgcalls.types import MediaStream, AudioQuality, VideoQuality, Update

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("player")

API_BASE = os.environ["PANEL_API_BASE"].rstrip("/")
PLAYER_KEY = os.environ["PLAYER_API_KEY"]
API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION = os.environ.get("TG_SESSION_STRING")
POLL_SECONDS = float(os.environ.get("POLL_SECONDS", "2"))
CACHE = Path(os.environ.get("CACHE_DIR", "/data/cache"))
CACHE.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "X-Api-Key": PLAYER_KEY,
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 SKTeamPlayer/2.0",
    "Accept": "*/*",
}
MAX_FAILS = 3
locks: dict[int, asyncio.Lock] = {}

EQ = {
    "normal": "", "bass": "bass=g=8", "pop": "bass=g=3,equalizer=f=1000:t=q:w=1:g=3,treble=g=3",
    "rock": "bass=g=5,equalizer=f=1000:t=q:w=1:g=-2,treble=g=4", "vocal": "bass=g=-3,equalizer=f=2500:t=q:w=1:g=5",
    "classical": "equalizer=f=250:t=q:w=1:g=2,treble=g=3",
}

app = Client("helper", api_id=API_ID, api_hash=API_HASH, session_string=SESSION, workdir=os.environ.get("PYRO_WORKDIR", "./data"))
calls = PyTgCalls(app)
http = httpx.AsyncClient(timeout=120, headers=HEADERS)
state: dict[int, dict] = {}

def ydl_opts(out: str, mp3: bool):
    o = {
        "format": "bestaudio/best", "outtmpl": out, "quiet": True, "noplaylist": True,
        "default_search": "ytsearch1", "extractor_args": {"youtube": {"player_client": ["android", "ios"]}},
    }
    if mp3: o["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}, {"key": "FFmpegMetadata"}]
    return o

def _yt_download(query: str, mp3: bool, video: bool = False) -> tuple[str, dict]:
    key = str(abs(hash(query)))
    out = str(CACHE / f"{key}{'_mp3' if mp3 else ''}{'_v' if video else ''}.%(ext)s")
    opts = ydl_opts(out, mp3)
    if video:
        opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best"
        opts["merge_output_format"] = "mp4"
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info: info = info["entries"][0]
        path = ydl.prepare_filename(info)
        if mp3: path = str(Path(path).with_suffix(".mp3"))
        elif video and not Path(path).exists(): path = str(Path(path).with_suffix(".mp4"))
    return path, info

async def fetch_media(item: dict) -> str:
    if item.get("tg_file_id"):
        path = CACHE / f"tg_{item['tg_file_id'][-40:]}"
        if not path.exists() or path.stat().st_size < 10000:
            r = await http.get(f"{API_BASE}/player/file", params={"file_id": item["tg_file_id"]})
            if r.status_code != 200 or "text/html" in r.headers.get("content-type", "") or len(r.content) < 10000:
                raise RuntimeError(f"file download failed [{r.status_code}]: {r.text[:150]}")
            tmp = path.with_suffix(".part")
            tmp.write_bytes(r.content)
            tmp.rename(path)
        return str(path)
    src = item["source_url"]
    if item.get("is_video") and src and (".m3u8" in src or src.startswith("rtmp") or src.endswith((".mp4", ".mkv", ".ts"))): return src
    path, _ = await asyncio.to_thread(_yt_download, src, False, bool(item.get("is_video")))
    return path

def stream(path: str, eq: str, seek: float = 0, video: bool = False) -> MediaStream:
    af = EQ.get(eq, "")
    ff = ""
    if seek > 1: ff += f"-ss {int(seek)} "
    if af: ff += f"-atend -af {af}"
    if video: return MediaStream(path, audio_parameters=AudioQuality.HIGH, video_parameters=VideoQuality.HD_720p, ffmpeg_parameters=ff.strip() or None)
    return MediaStream(path, audio_parameters=AudioQuality.STUDIO, video_flags=MediaStream.Flags.IGNORE, ffmpeg_parameters=ff.strip() or None)

def probe_duration(path: str) -> int | None:
    import subprocess
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True, timeout=20).stdout.strip()
        return int(float(out)) if out else None
    except Exception: return None

async def play_next(chat_id: int, finished: str | None = None, failed: bool = False, error: str = ""):
    lock = locks.setdefault(chat_id, asyncio.Lock())
    async with lock:
        fails = 0
        while True:
            body = {"chat_id": chat_id, "finished_item_id": finished}
            if failed: body.update(failed=True, error=error[:400])
            r = await http.post(f"{API_BASE}/player/next", json=body)
            data = r.json() if r.status_code == 200 else {}
            item = data.get("item")
            if not item:
                state.pop(chat_id, None)
                try: await calls.leave_call(chat_id)
                except Exception: pass
                return
            eq = data.get("eq", "normal")
            vid = bool(item.get("is_video"))
            try:
                path = await fetch_media(item)
                try: await calls.play(chat_id, stream(path, eq, video=vid))
                except Exception as e:
                    log.warning("play with EQ failed (%s), retrying without EQ", e)
                    await calls.play(chat_id, stream(path, "normal", video=vid))
                    eq = "normal"
            except Exception as e:
                fails += 1
                log.error("play failed (%d/%d): %s", fails, MAX_FAILS, e)
                finished, failed, error = item["id"], True, str(e)
                if fails >= MAX_FAILS:
                    await http.post(f"{API_BASE}/player/next", json={"chat_id": chat_id, "finished_item_id": finished, "failed": True, "error": error[:400]})
                    state.pop(chat_id, None)
                    return
                continue
            try: await set_volume(chat_id, int(data.get("volume", 100)))
            except Exception as e: log.warning("volume: %s (helper needs admin rights)", e)
            dur = item.get("duration") or (None if path.startswith(("http", "rtmp")) else await asyncio.to_thread(probe_duration, path))
            state[chat_id] = {"item": item, "path": path, "eq": eq, "video": vid, "started": time.time(), "paused_at": None, "offset": 0, "duration": dur}
            return

async def download_and_send(chat_id: int, p: dict):
    src = p.get("source_url")
    if not src: return
    path, info = await asyncio.to_thread(_yt_download, src, True)
    with open(path, "rb") as f:
        files = {"audio": (Path(path).name, f, "audio/mpeg")}
        data = {"chat_id": str(chat_id), "title": p.get("title") or info.get("title", ""), "performer": p.get("performer") or info.get("uploader", ""), "duration": str(int(info.get("duration") or 0)), "queue_item_id": p.get("queue_item_id") or ""}
        r = await http.post(f"{API_BASE}/player/upload", data=data, files=files)
    log.info("upload: %s", r.text[:200])

async def set_volume(chat_id: int, v: int):
    if v <= 0: await calls.mute(chat_id); return
    try: await calls.unmute(chat_id)
    except Exception: pass
    await calls.change_volume_call(chat_id, min(200, v))

def elapsed(s: dict) -> float:
    if s["paused_at"]: return s["paused_at"] - s["started"] + s["offset"]
    return time.time() - s["started"] + s["offset"]

async def handle(cmd: dict):
    chat_id = int(cmd["chat_id"])
    a = cmd["action"]
    p = cmd.get("payload") or {}
    s = state.get(chat_id)
    log.info("cmd %s %s", chat_id, a)
    if a == "play_next":
        if not s: await play_next(chat_id)
    elif a == "pause" and s: await calls.pause(chat_id); s["paused_at"] = time.time()
    elif a == "resume" and s:
        await calls.resume(chat_id)
        if s["paused_at"]: s["started"] += time.time() - s["paused_at"]; s["paused_at"] = None
    elif a == "skip": await play_next(chat_id, s["item"]["id"] if s else None)
    elif a == "stop":
        state.pop(chat_id, None)
        try: await calls.leave_call(chat_id)
        except Exception: pass
    elif a == "volume" and s: await set_volume(chat_id, int(p.get("volume", 100)))
    elif a == "eq" and s:
        pos = elapsed(s)
        s["eq"] = p.get("eq", "normal")
        await calls.play(chat_id, stream(s["path"], s["eq"], pos, video=s.get("video", False)))
        s.update(started=time.time(), offset=pos, paused_at=None)
    elif a == "download": asyncio.create_task(download_and_send(chat_id, p))

@calls.on_update(filters.stream_end())
async def on_end(_, update: Update):
    s = state.get(update.chat_id)
    if not s: return
    quick = time.time() - s["started"] < 5
    if quick and s["eq"] != "normal":
        s["eq"] = "normal"
        s["started"] = time.time()
        await calls.play(update.chat_id, stream(s["path"], "normal", video=s.get("video", False)))
        return
    await play_next(update.chat_id, s["item"]["id"], failed=quick, error="stream ended instantly" if quick else "")

async def progress_loop():
    while True:
        await asyncio.sleep(10)
        for chat_id, s in list(state.items()):
            try: await http.post(f"{API_BASE}/player/progress", json={"chat_id": chat_id, "item_id": s["item"]["id"], "position": int(elapsed(s)), "duration": s.get("duration"), "paused": bool(s["paused_at"])})
            except Exception as e: log.warning("progress: %s", e)

async def poll_loop():
    while True:
        try:
            r = await http.get(f"{API_BASE}/player/commands")
            if r.status_code == 200:
                for c in r.json().get("commands", []):
                    try: await handle(c)
                    except Exception as e: log.exception("command failed: %s", e)
            else: log.warning("poll %s %s", r.status_code, r.text[:200])
        except Exception as e: log.warning("poll error: %s", e)
        await asyncio.sleep(POLL_SECONDS)

async def main():
    await calls.start()
    me = await app.get_me()
    log.info("Helper account online: %s", me.username or me.id)
    asyncio.create_task(progress_loop())
    await poll_loop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
