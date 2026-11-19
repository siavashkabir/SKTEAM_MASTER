#!/usr/bin/env python3
"""Sk.Media Player — clean rewrite"""
import asyncio, os, sys, json, time, hashlib, traceback, subprocess
from pathlib import Path
from datetime import datetime
import httpx
from pyrogram import Client
from pyrogram.handlers import RawUpdateHandler
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.types import (
    InputChannel,
    UpdateGroupCall,
    UpdateGroupCallParticipants,
)
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream, AudioQuality, Update
import yt_dlp
import recorder as _rec

API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION = os.environ["TG_SESSION_STRING"]
SERVER = os.environ.get("SK_SERVER", "http://127.0.0.1:8080")

CACHE = Path("/root/sk_media/cache")
CACHE.mkdir(parents=True, exist_ok=True)
LOGO = "/root/sk_media/assets/logo_500.jpg"
STATE_FILE = "/root/sk_media/.state.json"
POLL_SEC = 2
POS_SEC = 5

# ─── voice monitor (ادغام‌شده) ───
# MANAGER_BOT_ID حذف شد — الان HTTP
MUSIC_BOT_API_KEY = os.environ.get("MUSIC_BOT_API_KEY", "SktTeam_vcstat_1791787127_secret")
VC_STATE_FILE = "/root/sk_media/voice_state.json"
VC_CALL_TO_CHAT = {}
VC_SESSIONS = {}

def log(*a):
    sys.stderr.write(" ".join(str(x) for x in a) + "\n")
    sys.stderr.flush()

# ═══════════════════════════════════════════════
# State save/load
# ═══════════════════════════════════════════════
def _save_state(cid, title, src, dur, orig=None):
    try:
        d = {}
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f: d = json.load(f)
        d[str(cid)] = {"title": title, "src": src, "dur": dur, "orig": orig or src}
        with open(STATE_FILE, "w") as f: json.dump(d, f)
    except Exception as e:
        log(f"[state] save err: {e}")

def _load_state(cid):
    try:
        if not os.path.exists(STATE_FILE): return None
        with open(STATE_FILE) as f: d = json.load(f)
        return d.get(str(cid))
    except: return None

def _clear_state(cid):
    try:
        if not os.path.exists(STATE_FILE): return
        with open(STATE_FILE) as f: d = json.load(f)
        d.pop(str(cid), None)
        with open(STATE_FILE, "w") as f: json.dump(d, f)
    except: pass

# ═══════════════════════════════════════════════
# ID3 tags
# ═══════════════════════════════════════════════
def set_id3(path, title):
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import TIT2, TPE1, TALB, COMM, APIC
        a = MP3(path)
        if a.tags is None: a.add_tags()
        for k in ("TIT2","TPE1","TALB","COMM","APIC"):
            try: a.tags.delall(k)
            except: pass
        a.tags["TIT2"] = TIT2(encoding=3, text=title[:200])
        a.tags["TPE1"] = TPE1(encoding=3, text="Sk.Team")
        a.tags["TALB"] = TALB(encoding=3, text="Sk.Team Music Player")
        a.tags["COMM"] = COMM(encoding=3, lang="eng", desc="", text="@SkTeamMusic_Bot")
        if os.path.exists(LOGO):
            with open(LOGO, "rb") as fp:
                a.tags["APIC"] = APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=fp.read())
        a.save()
        return True
    except Exception as e:
        log(f"[id3] err: {e}")
        return False

# ═══════════════════════════════════════════════
# Download از SoundCloud
# ═══════════════════════════════════════════════
def clean_query(q):
    q = (q or "").strip()
    for p in ("ytsearch1:","ytsearch2:","ytsearch:","scsearch1:","scsearch2:","scsearch:"):
        if q.startswith(p): q = q[len(p):].strip(); break
    return q

def _dl_one(final, q, no_aria=False):
    """یک بار دانلود از یک منبع"""
    key = hashlib.md5(final.encode()).hexdigest()[:16]
    out = str(CACHE / key)
    # ★ چند کوکی: اول اصلی، اگه نبود backup
    _ck_candidates = [
        "/root/sk_media/cookies_yt.txt",
        "/root/sk_media/cookies_yt_2.txt",
        "/root/sk_media/cookies_yt_3.txt",
    ]
    _ck = next((c for c in _ck_candidates if os.path.exists(c)), None)

    opts = {
        "format": "bestaudio/best",
        "outtmpl": out,
        "quiet": False,
        "no_warnings": False,
        "noplaylist": True,
        "concurrent_fragment_downloads": 16,
        "remote_components": ["ejs:github"],
        "postprocessors": [{"key":"FFmpegExtractAudio","preferredcodec":"mp3","preferredquality":"96"}],
    }

    if not no_aria:
        opts["external_downloader"] = "aria2c"
        opts["external_downloader_args"] = {"aria2c": ["-x","16","-s","16","-k","1M","--summary-interval=0"]}

    if _ck:
        opts["cookiefile"] = _ck
        opts["age_limit"] = 99
        opts["nocheckcertificate"] = True
        opts["geo_bypass"] = True
        opts["geo_bypass_country"] = "DE"

    if "ytsearch" in final or "youtube" in final:
        opts["extractor_args"] = {
            "youtube": {"player_client": ["web", "mweb"]}
        }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(final, download=True)
        entries = info.get("entries") or []
        if entries:
            info = entries[0]
        elif not info.get("id"):
            raise Exception("no results")

        # ★ چک کن فایل واقعاً وجود داره
        path = ydl.prepare_filename(info)
        p = Path(path)

        # اگه با پسوند اصلی نیست، دنبال mp3 بگرد
        candidates = [
            p,
            p.with_suffix(".mp3"),
            CACHE / (key + ".mp3"),
        ]
        # glob برای هر فایل با پیشوند key
        for f in CACHE.glob(key + ".*"):
            candidates.append(f)

        real_path = None
        for c in candidates:
            if c.exists() and c.stat().st_size > 10000:  # حداقل ۱۰KB
                real_path = c
                break

        if not real_path:
            # خطای واقعی: فایل پیدا نشد
            raise Exception(f"file not found after dl: {path}")

        return str(real_path), info.get("title", q), info.get("duration", 0)


def _aparat_search(q):
    """جستجوی آپارات — برمی‌گردونه URL ویدیو"""
    try:
        import httpx as _hx
        url = "https://www.aparat.com/etc/api/videoBySearch/text/" + q
        with _hx.Client(timeout=10) as c:
            r = c.get(url)
            if r.status_code != 200:
                return None
            data = r.json()
            items = data.get("videobysearch", [])
            if not items:
                return None
            # اولین نتیجه
            first = items[0]
            uid = first.get("uid", "")
            if not uid:
                return None
            return f"https://www.aparat.com/v/{uid}"
    except Exception as e:
        log(f"[aparat] search err: {e}")
        return None


def download(query):
    """Multi-source: SC → YT → Aparat → Audius → Invidious → YT backup"""
    q = clean_query(query)
    log(f"[dl] query={q!r}")

    if q.startswith(("scsearch", "ytsearch")):
        sources = [q]
    else:
        sources = [
            f"scsearch1:{q}",
            f"ytsearch1:{q}",
            f"scsearch3:{q}",
            f"ytsearch3:{q}",
            f"ytsearch5:{q}",
        ]
        # ★ آپارات به عنوان fallback آخر (فقط برای فارسی)
        aparat_url = _aparat_search(q)
        if aparat_url:
            sources.append(aparat_url)

    last_err = None
    for final in sources:
        src = final.split(":")[0]
        # تلاش ۱: با aria
        try:
            log(f"[dl] try {src} (aria)")
            r = _dl_one(final, q)
            log(f"[dl] OK via {src}")
            return r
        except Exception as e:
            log(f"[dl] FAIL {src} (aria): {str(e)[:120]}")
            last_err = e
        # تلاش ۲: بدون aria
        try:
            log(f"[dl] try {src} (native)")
            r = _dl_one(final, q, no_aria=True)
            log(f"[dl] OK via {src} (native)")
            return r
        except Exception as e:
            log(f"[dl] FAIL {src} (native): {str(e)[:120]}")
            last_err = e

    raise Exception(f"all failed: {last_err}")


# ═══════════════════════════════════════════════
# process_audio (ffmpeg - EQ / speed / seek)
# ═══════════════════════════════════════════════
EQ_MAP = {
    "rock":    "equalizer=f=80:t=q:w=1:g=4,equalizer=f=200:t=q:w=1:g=2,equalizer=f=800:t=q:w=1:g=-1,equalizer=f=2500:t=q:w=1:g=3,equalizer=f=6000:t=q:w=1:g=3,volume=0.85",
    "jazz":    "equalizer=f=80:t=q:w=1:g=3,equalizer=f=400:t=q:w=1:g=2,equalizer=f=1500:t=q:w=1:g=-1,equalizer=f=3500:t=q:w=1:g=2,equalizer=f=8000:t=q:w=1:g=3,volume=0.85",
    "pop":     "equalizer=f=80:t=q:w=1:g=-2,equalizer=f=1000:t=q:w=1:g=3,equalizer=f=3000:t=q:w=1:g=3,equalizer=f=8000:t=q:w=1:g=2,volume=0.85",
    "classic": "equalizer=f=80:t=q:w=1:g=3,equalizer=f=300:t=q:w=1:g=1,equalizer=f=1500:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=1:g=-1,equalizer=f=8000:t=q:w=1:g=2,volume=0.85",
    "bass":    "equalizer=f=60:t=q:w=1:g=6,equalizer=f=120:t=q:w=1:g=4,equalizer=f=250:t=q:w=1:g=2,volume=0.8",
    "treble":  "equalizer=f=3000:t=q:w=1:g=4,equalizer=f=6000:t=q:w=1:g=5,equalizer=f=10000:t=q:w=1:g=3,volume=0.85",
    "vocal":   "equalizer=f=200:t=q:w=2:g=-4,equalizer=f=800:t=q:w=1:g=1,equalizer=f=2500:t=q:w=2:g=4,equalizer=f=5000:t=q:w=1:g=3,volume=0.9",
    "3d":      "aecho=0.8:0.85:40|80:0.35|0.25,extrastereo=m=1.8,volume=0.85",
    "wide":    "extrastereo=m=2.5,volume=0.9",
    "night":   "equalizer=f=60:t=q:w=1:g=4,equalizer=f=8000:t=q:w=1:g=-4,volume=0.8",
    "day":     "equalizer=f=8000:t=q:w=1:g=3,equalizer=f=60:t=q:w=1:g=2,volume=0.95",
    "silent":  "volume=0.25",
    "heavy":   "equalizer=f=60:t=q:w=1:g=6,equalizer=f=150:t=q:w=1:g=4,equalizer=f=1000:t=q:w=1:g=-2,equalizer=f=3000:t=q:w=1:g=2,volume=0.8",
    "dance":   "equalizer=f=80:t=q:w=1:g=5,equalizer=f=250:t=q:w=1:g=2,equalizer=f=1500:t=q:w=1:g=-1,equalizer=f=5000:t=q:w=1:g=3,volume=0.85",
    "hiphop":  "equalizer=f=60:t=q:w=1:g=5,equalizer=f=120:t=q:w=1:g=3,equalizer=f=3000:t=q:w=1:g=2,volume=0.85",
    "acoustic":"equalizer=f=80:t=q:w=1:g=2,equalizer=f=1500:t=q:w=1:g=1,equalizer=f=6000:t=q:w=1:g=3,volume=0.9",
}

def process_audio(src, tag, seek=0, speed=1.0, eq=None):
    """رندر مجدد — -ss بعد از -i برای MP3 دقیق"""
    import subprocess as _sp, time as _t
    out = str(CACHE / f"p_{int(_t.time())}_{tag}.mp3")
    # ★ -i اول، بعد -ss (accurate seek برای MP3)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src]
    if seek and seek > 0:
        cmd += ["-ss", str(int(seek))]
    filters = []
    if eq and eq in EQ_MAP:
        filters.append(EQ_MAP[eq])
    if speed and abs(float(speed) - 1.0) > 0.01:
        s = max(0.5, min(2.0, float(speed)))
        filters.append(f"atempo={s}")
    if filters:
        cmd += ["-af", ",".join(filters)]
    cmd += ["-c:a", "libmp3lame", "-b:a", "96k", out]
    log(f"[proc] seek={seek}s speed={speed} eq={eq}")
    try:
        _sp.run(cmd, check=True, capture_output=True, timeout=180)
    except _sp.CalledProcessError as e:
        err = (e.stderr or b"").decode()[:300]
        log(f"[proc] FAIL: {err}")
        raise
    # ★ ffprobe برای مدت دقیق
    dur = 0
    try:
        rr = _sp.run(["ffprobe","-v","quiet","-show_entries","format=duration",
                      "-of","csv=p=0", out], capture_output=True, text=True, timeout=10)
        dur = int(float(rr.stdout.strip()))
    except:
        try:
            from mutagen.mp3 import MP3
            dur = int(MP3(out).info.length)
        except: dur = 0
    log(f"[proc] ✅ dur={dur}s")
    return out, dur

# ═══════════════════════════════════════════════
# PLAY_STATE
# ═══════════════════════════════════════════════
PLAY_STATE = {}
PREFETCH = {}  # {cid: {query, path, title, dur}}

def cancel_tasks(state):
    """تمام task های در حال اجرا رو cancel کن"""
    for k in ("_pos_task", "_sched_task"):
        t = state.get(k)
        if t and not t.done():
            try: t.cancel()
            except: pass


def start_tasks(h, cid, calls, state, dur):
    """شروع pos_loop + sched_next"""
    cancel_tasks(state)
    state["_pos_task"] = asyncio.create_task(pos_loop(h, cid, state))
    state["_sched_task"] = asyncio.create_task(sched_next(h, cid, calls, dur))


def cur_pos(state):
    """position = base_pos + elapsed"""
    if not state.get("active"): return 0
    base = int(state.get("base_pos", 0) or 0)
    if not state.get("playing"):
        return base + int(state.get("position", 0) or 0)
    started = state.get("started_at", time.time())
    elapsed = max(0, int(time.time() - started))
    return base + elapsed



async def pos_loop(h, cid, state):
    log(f"[pos_loop] start {cid}")
    try:
        while state.get("active"):
            try:
                pos = cur_pos(state)
                dur = int(state.get("duration", 0) or 0)
                if dur > 0 and pos > dur: pos = dur
                log(f"[POS] {pos}s / {dur}s")
                await h.post(f"{SERVER}/position", json={
                    "chat_id": cid, "position": pos, "duration": dur,
                    "paused": not state.get("playing", False),
                    "speed": state.get("speed", 1.0),
                    "volume": state.get("volume", 100),
                    "repeat": state.get("repeat", "off"),
                    "shuffle": state.get("shuffle", False),
                })
            except Exception as e:
                log(f"[pos] err: {e}")
            await asyncio.sleep(POS_SEC)
    finally:
        log(f"[pos_loop] stop {cid}")

# ═══════════════════════════════════════════════
# queue next
# ═══════════════════════════════════════════════
async def qnext(h, cid):
    try:
        r = await h.get(f"{SERVER}/queue/next", params={"chat_id": cid})
        return r.json().get("next")
    except: return None

# ═══════════════════════════════════════════════
# schedule next track
# ═══════════════════════════════════════════════
async def _prefetch_next(h, cid):
    """★ پیش‌دانلود آهنگ بعدی صف در پس‌زمینه"""
    try:
        await asyncio.sleep(3)
        state = PLAY_STATE.get(str(cid))
        if not state or not state.get("active"):
            return
        r = await h.get(f"{SERVER}/queue/peek", params={"chat_id": cid})
        nxt = r.json().get("next")
        if not nxt:
            log("[prefetch] queue empty")
            return
        # اگه قبلاً برای همین query prefetch شده، رد کن
        if cid in PREFETCH and PREFETCH[cid].get("query") == nxt.get("query"):
            log("[prefetch] already cached")
            return
        log(f"[prefetch] downloading {nxt['query']!r}")
        path, title, dur = await asyncio.to_thread(download, nxt["query"])
        PREFETCH[cid] = {
            "query": nxt["query"],
            "path": path,
            "title": title,
            "dur": dur,
        }
        log(f"[prefetch] ✅ {title} ({dur}s)")
    except Exception as e:
        log(f"[prefetch] err: {e}")


async def _auto_play_next(h, cid, calls, nxt):
    """★ پخش آهنگ بعدی، با استفاده از prefetch اگه موجود باشه"""
    pf = PREFETCH.pop(cid, None)
    if pf and pf.get("query") == nxt.get("query"):
        log(f"[play_next] ⚡ using prefetched: {pf['title']}")
        await handle({
            "action": "play",
            "chat_id": cid,
            "query": f"LOCAL|{pf['path']}|{pf['title']}",
            "requested_by": nxt.get("requested_by"),
            "requested_by_name": nxt.get("requested_by_name", ""),
        }, calls, h)
    else:
        if pf:
            log(f"[play_next] prefetch mismatch, downloading fresh")
        await handle({
            "action": "play",
            "chat_id": cid,
            "query": nxt["query"],
            "requested_by": nxt.get("requested_by"),
            "requested_by_name": nxt.get("requested_by_name", ""),
        }, calls, h)


async def sched_next(h, cid, calls, dur):
    try:
        await asyncio.sleep(dur + 2)
        key = str(cid)
        state = PLAY_STATE.get(key, {})
        if not state.get("active"): return
        nxt = await qnext(h, cid)
        if nxt:
            log(f"[auto-next] {nxt['query']}")
            await _auto_play_next(h, cid, calls, nxt)
        elif state.get("repeat") == "one":
            log(f"[repeat one] replay")
            state["started_at"] = time.time()
            state["active"] = True
            state["playing"] = True
            src = state.get("src_path")
            if src and os.path.exists(src):
                stream = MediaStream(src, audio_parameters=AudioQuality.HIGH,
                                     video_flags=MediaStream.Flags.IGNORE)
                try: await calls.play(cid, stream)
                except: pass
        else:
            log(f"[auto-next] queue empty → stop")
            state["active"] = False
            state["playing"] = False
            try: await calls.leave_call(cid)
            except: pass
            PLAY_STATE.pop(key, None)
            _clear_state(cid)
            try:
                await h.post(f"{SERVER}/status", json={"chat_id":cid,"status":"stopped","id":"auto"})
            except: pass
    except Exception as e:
        log(f"[sched] err: {e}")

# ═══════════════════════════════════════════════
# handle command
# ═══════════════════════════════════════════════
async def handle(cmd, calls, h):
    action = (cmd.get("action") or "").lower()
    cid = int(cmd.get("chat_id", 0))
    key = str(cid)
    log(f"[cmd] {action} {cid}")

    async def report(st, **kw):
        try:
            await h.post(f"{SERVER}/status", json={"id": cmd.get("id"), "chat_id": cid, "status": st, **kw})
        except: pass

    # ─── PLAY ───
    if action in ("play", "play_next"):
        q = cmd.get("query") or cmd.get("url") or cmd.get("title")
        if not q:
            await report("error", error="no query"); return
        # ★ اگه رکورد فعاله → pause
        try:
            st = _rec.STATE.get(cid, {})
            if st.get("enabled") and not st.get("_paused"):
                log(f"[rec] pause due to play")
                await _rec.stop_rec(calls, cid, pause_only=True)
        except Exception as e:
            log(f"[rec] pause err: {e}")
        # ★ LOCAL | FILE |
        is_local = q.startswith("LOCAL|")
        if is_local:
            parts = q.split("|", 2)
            if len(parts) < 3:
                await report("error", error="bad local"); return
            src_path = parts[1]
            title = parts[2]
            log(f"[play] local={src_path}")
            if not os.path.exists(src_path):
                await report("error", error=f"not found: {src_path}"); return
            await report("joining", title=title, duration=0, position=0)
            try:
                # copy به cache + ID3
                import shutil
                dst = CACHE / Path(src_path).name
                if not dst.exists(): shutil.copy2(src_path, str(dst))
                try:
                    from mutagen.mp3 import MP3
                    dur = int(MP3(str(dst)).info.length)
                except: dur = 0
                try: set_id3(str(dst), title)
                except: pass
                stream = MediaStream(str(dst), audio_parameters=AudioQuality.HIGH,
                                     video_flags=MediaStream.Flags.IGNORE)
                if key in PLAY_STATE and PLAY_STATE[key].get("active"):
                    await calls.change_stream(cid, stream)
                else:
                    await calls.play(cid, stream)
                PLAY_STATE[key] = {
                    "active": True, "playing": True, "paused": False,
                    "started_at": time.time(), "base_pos": 0, "duration": dur,
                    "title": title, "position": 0,
                    "speed": 1.0, "repeat": "off", "shuffle": False,
                    "volume": 100, "eq": None,
                    "src_path": str(dst), "original_path": str(dst),
                }
                _save_state(cid, title, str(dst), dur)
                start_tasks(h, cid, calls, PLAY_STATE[key], dur)
                await report("playing", title=title, duration=dur, position=0)
                log(f"[play] ✅ {title}")
                asyncio.create_task(_prefetch_next(h, cid))
            except Exception as e:
                log(f"[play] err: {e}"); log(traceback.format_exc())
                await report("error", error=str(e))
            return
        # ─── download از SoundCloud ───
        await report("joining", title=q, duration=0, position=0)
        try:
            path, title, dur = await asyncio.to_thread(download, q)
            try: set_id3(path, title)
            except: pass
        except Exception as e:
            log(f"[play] dl err: {e}")
            await report("error", error=f"download: {e}")
            return
        try:
            stream = MediaStream(path, audio_parameters=AudioQuality.HIGH,
                                 video_flags=MediaStream.Flags.IGNORE)
            if key in PLAY_STATE and PLAY_STATE[key].get("active"):
                await calls.change_stream(cid, stream)
            else:
                await calls.play(cid, stream)
            PLAY_STATE[key] = {
                "active": True, "playing": True, "paused": False,
                "started_at": time.time(), "duration": dur,
                "title": title, "position": 0,
                "speed": 1.0, "repeat": "off", "shuffle": False,
                "volume": 100, "eq": None,
                "src_path": path, "original_path": path,
            }
            _save_state(cid, title, path, dur)
            start_tasks(h, cid, calls, PLAY_STATE[key], dur)
            await report("playing", title=title, duration=dur, position=0)
            log(f"[play] ✅ {title}")
            asyncio.create_task(_prefetch_next(h, cid))
        except Exception as e:
            log(f"[play] err: {e}"); log(traceback.format_exc())
            await report("error", error=str(e))
        return

    state = PLAY_STATE.get(key, {})

    # ─── PAUSE ───
    if action == "pause":
        try: await calls.pause(cid)
        except: pass
        # position رو توی base_pos بریز
        state["base_pos"] = cur_pos(state)
        state["playing"] = False
        state["position"] = 0
        await report("playing", title=state.get("title","—"),
                     duration=state.get("duration",0), position=state["position"], paused=True)
        return
    # ─── RESUME ───
    if action == "resume":
        try: await calls.resume(cid)
        except: pass
        state["started_at"] = time.time()
        state["playing"] = True
        # base_pos قبلی حفظ بشه
        await report("playing", title=state.get("title","—"),
                     duration=state.get("duration",0), position=state.get("position",0))
        return
    # ─── STOP ───
    if action == "stop":
        state["active"] = False
        PREFETCH.pop(cid, None)  # ★ پاک کردن prefetch
        cancel_tasks(state)
        try: await calls.leave_call(cid)
        except: pass
        PLAY_STATE.pop(key, None)
        _clear_state(cid)
        await report("stopped")
        return
    # ─── MUTE ───
    if action == "mute":
        try: await calls.mute(cid)
        except: pass
        await report("playing", title=state.get("title","—"), muted=True)
        return
    if action == "unmute":
        try: await calls.unmute(cid)
        except: pass
        await report("playing", title=state.get("title","—"), muted=False)
        return
    # ─── VOLUME ───
    if action == "volume":
        v = max(1, min(200, int(cmd.get("volume", 100))))
        try: await calls.change_volume_call(cid, v)
        except: pass
        state["volume"] = v
        await report("playing", title=state.get("title","—"),
                     duration=state.get("duration",0), volume=v)
        return
    if action == "volume_up":
        v = min(200, int(state.get("volume",100)) + 10)
        try: await calls.change_volume_call(cid, v)
        except: pass
        state["volume"] = v
        await report("playing", title=state.get("title","—"),
                     duration=state.get("duration",0), volume=v)
        return
    if action == "volume_down":
        v = max(10, int(state.get("volume",100)) - 10)
        try: await calls.change_volume_call(cid, v)
        except: pass
        state["volume"] = v
        await report("playing", title=state.get("title","—"),
                     duration=state.get("duration",0), volume=v)
        return
    # ─── NEXT ───
    if action in ("next", "skip"):
        log("[next]")
        state["active"] = False
        try: await calls.leave_call(cid)
        except: pass
        PLAY_STATE.pop(key, None)
        await asyncio.sleep(1)
        nxt = await qnext(h, cid)
        if nxt:
            log(f"[next] → {nxt['query']}")
            await _auto_play_next(h, cid, calls, nxt)
        else:
            await report("stopped")
        return
    if action == "previous":
        log("[prev] not supported")
        return
    # ─── SPEED ───
    if action == "speed":
        val = max(0.5, min(2.0, float(cmd.get("value", 1.0))))
        src = state.get("original_path") or state.get("src_path")
        if not src or not os.path.exists(src):
            await report("error", error="no src"); return
        cp = cur_pos(state)
        log(f"[speed] {val}x @ {cp}s")
        await report("joining", title=state.get("title","—"),
                     duration=state.get("duration",0), speed=val)
        try:
            state["active"] = False
            await asyncio.sleep(0.3)
            eq = state.get("eq")
            new_path, new_dur = await asyncio.to_thread(
                process_audio, src, f"spd{val}", cp, val, eq)
            stream = MediaStream(new_path, audio_parameters=AudioQuality.HIGH,
                                 video_flags=MediaStream.Flags.IGNORE)
            try: await calls.change_stream(cid, stream)
            except: await calls.play(cid, stream)
            orig_dur = int(state.get("duration", 0) or new_dur + cp)
            state["base_pos"] = cp
            state["started_at"] = time.time()
            state["position"] = 0
            state["speed"] = val
            state["src_path"] = new_path
            state["duration"] = orig_dur
            state["active"] = True
            state["playing"] = True
            # زمان باقی‌مانده با speed جدید
            remaining = max(1, int((orig_dur - cp) / val)) if val > 0 else (orig_dur - cp)
            start_tasks(h, cid, calls, state, remaining)
            await report("playing", title=state.get("title","—"),
                         duration=orig_dur, position=cp, speed=val)
            log(f"[speed] ✅ {val}x @ {cp}s")
        except Exception as e:
            log(f"[speed] err: {e}")
            await report("error", error=str(e))
        return
    if action == "speed_delta":
        cur = float(state.get("speed", 1.0))
        val = max(0.5, min(2.0, cur + float(cmd.get("delta", 0))))
        await handle({"action":"speed","chat_id":cid,"value":val,"id":cmd.get("id")}, calls, h)
        return
    # ─── SEEK ───
    if action == "seek":
        direction = cmd.get("direction", "fwd")
        secs = int(cmd.get("seconds", 30))
        src = state.get("original_path") or state.get("src_path")
        if not src or not os.path.exists(src):
            await report("error", error="no src"); return
        cp = cur_pos(state)
        dur = int(state.get("duration", 0))
        if direction == "fwd":
            new_pos = min(cp + secs, max(0, dur - 3))
        else:
            new_pos = max(cp - secs, 0)
        log(f"[seek] {direction} {secs}s {cp}→{new_pos}")
        await report("joining", title=state.get("title","—"),
                     duration=dur, position=new_pos)
        try:
            state["active"] = False
            await asyncio.sleep(0.3)
            spd = float(state.get("speed", 1.0))
            eq = state.get("eq")
            new_path, new_dur = await asyncio.to_thread(
                process_audio, src, f"sk{new_pos}", new_pos, spd, eq)
            stream = MediaStream(new_path, audio_parameters=AudioQuality.HIGH,
                                 video_flags=MediaStream.Flags.IGNORE)
            try: await calls.change_stream(cid, stream)
            except: await calls.play(cid, stream)
            orig_dur = int(state.get("duration", 0) or new_dur + new_pos)
            state["base_pos"] = new_pos
            state["started_at"] = time.time()
            state["position"] = 0
            state["src_path"] = new_path
            state["duration"] = orig_dur
            state["active"] = True
            state["playing"] = True
            start_tasks(h, cid, calls, state, orig_dur - new_pos)
            await report("playing", title=state.get("title","—"),
                         duration=orig_dur, position=new_pos)
            log(f"[seek] ✅ @ {new_pos}s")
        except Exception as e:
            log(f"[seek] err: {e}")
            await report("error", error=str(e))
        return
    # ─── EQ ───
    if action == "eq":
        eq_name = (cmd.get("eq") or "off").lower().strip()
        src = state.get("original_path") or state.get("src_path")
        if not src or not os.path.exists(src):
            await report("error", error="no src"); return
        cp = cur_pos(state)
        log(f"[eq] {eq_name} @ {cp}s")
        if eq_name in ("off", "none", ""):
            await report("joining", title=state.get("title","—"),
                         duration=state.get("duration",0), eq="off")
            try:
                state["active"] = False
                await asyncio.sleep(0.3)
                spd = float(state.get("speed", 1.0))
                new_path, new_dur = await asyncio.to_thread(
                    process_audio, src, "eqoff", cp, spd, None)
                stream = MediaStream(new_path, audio_parameters=AudioQuality.HIGH,
                                     video_flags=MediaStream.Flags.IGNORE)
                try: await calls.change_stream(cid, stream)
                except: await calls.play(cid, stream)
                orig_dur = int(state.get("duration", 0) or new_dur + cp)
                state["base_pos"] = cp
                state["started_at"] = time.time()
                state["position"] = 0
                state["src_path"] = new_path
                state["duration"] = orig_dur
                state["eq"] = None
                state["active"] = True
                state["playing"] = True
                start_tasks(h, cid, calls, state, orig_dur - cp)
                await report("playing", title=state.get("title","—"),
                             duration=orig_dur, position=cp, eq="off")
                log(f"[eq] ✅ off @ {cp}s")
            except Exception as e:
                log(f"[eq] err: {e}")
            return
        if eq_name not in EQ_MAP:
            await report("error", error=f"eq invalid: {eq_name}"); return
        await report("joining", title=state.get("title","—"),
                     duration=state.get("duration",0), eq=eq_name)
        try:
            state["active"] = False
            await asyncio.sleep(0.3)
            spd = float(state.get("speed", 1.0))
            new_path, new_dur = await asyncio.to_thread(
                process_audio, src, f"eq_{eq_name}", cp, spd, eq_name)
            stream = MediaStream(new_path, audio_parameters=AudioQuality.HIGH,
                                 video_flags=MediaStream.Flags.IGNORE)
            try: await calls.change_stream(cid, stream)
            except: await calls.play(cid, stream)
            orig_dur = int(state.get("duration", 0) or new_dur + cp)
            # ★ started_at = now - cp → پنل از cp ادامه بده
            state["started_at"] = time.time() - cp
            state["position"] = cp
            state["src_path"] = new_path
            state["duration"] = orig_dur  # ← مدت کل اصلی
            state["eq"] = eq_name
            state["active"] = True
            state["playing"] = True
            start_tasks(h, cid, calls, state, orig_dur - cp)
            await report("playing", title=state.get("title","—"),
                         duration=orig_dur, position=cp, eq=eq_name)
            log(f"[eq] ✅ {eq_name} @ {cp}s")
        except Exception as e:
            log(f"[eq] err: {e}")
            await report("error", error=str(e))
        return
    # ─── REPEAT / SHUFFLE ───
    if action == "cycle_repeat":
        cur = state.get("repeat", "off")
        nxt = {"off":"one","one":"all","all":"off"}.get(cur, "off")
        state["repeat"] = nxt
        await report("playing", title=state.get("title","—"),
                     duration=state.get("duration",0), repeat=nxt)
        return
    if action == "toggle_shuffle":
        state["shuffle"] = not state.get("shuffle", False)
        await report("playing", title=state.get("title","—"),
                     duration=state.get("duration",0), shuffle=state["shuffle"])
        return
    # ─── DOWNLOAD FILE ───
    if action == "download_file":
        quality = int(cmd.get("quality", 128))
        uid = cmd.get("user_id")
        src = state.get("original_path") or state.get("src_path")
        title = state.get("title", "Unknown")
        if not src or not os.path.exists(src):
            await report("error", error="no src"); return
        try:
            SHARED = "/data/data/com.termux/files/home/sk_media/tg_files"
            os.makedirs(SHARED, exist_ok=True)
            out = f"{SHARED}/dl_{int(time.time())}_{quality}k.mp3"
            subprocess.run(["ffmpeg","-y","-loglevel","error","-i",src,
                            "-c:a","libmp3lame","-b:a",f"{quality}k","-map_metadata","0",out],
                           check=True, capture_output=True, timeout=120)
            try: set_id3(out, title)
            except: pass
            await report("file_ready", title=title, path=out, quality=quality, user_id=uid)
            log(f"[dl_file] ✅ {out}")
        except Exception as e:
            log(f"[dl_file] err: {e}")
            await report("error", error=str(e))
        return

        # ─── RECORD COMMANDS ───
        if action in ("record_start", "record_stop", "record_pause", "record_resume"):
            try:
                await _rec.handle_cmd(calls, cmd)
                await report("record_status", title=state.get("title","—"))
            except Exception as e:
                log(f"[rec] handle err: {e}")
                await report("error", error=f"rec: {e}")
            return

    log(f"[cmd] unknown: {action}")

# ═══════════════════════════════════════════════
# voice monitor (ادغام‌شده)
# ═══════════════════════════════════════════════
def _vc_load_state():
    global VC_SESSIONS
    try:
        if os.path.exists(VC_STATE_FILE):
            with open(VC_STATE_FILE, "r", encoding="utf-8") as f:
                VC_SESSIONS = json.load(f)
            log(f"[vc] loaded state: {len(VC_SESSIONS)} chats")
    except Exception as e:
        log(f"[vc] load err: {e}")
        VC_SESSIONS = {}


def _vc_save_state():
    try:
        with open(VC_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(VC_SESSIONS, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log(f"[vc] save err: {e}")


def _vc_get_name(users, uid):
    u = users.get(uid) if users else None
    if not u:
        return "", ""
    fn = getattr(u, "first_name", "") or ""
    un = getattr(u, "username", "") or ""
    return fn, un


async def _vc_on_raw_update(client, update, users, chats):
    """رویداد ورود/خروج اعضا به کال"""
    try:
        if isinstance(update, UpdateGroupCallParticipants):
            call_id = update.call.id
            chat_id = VC_CALL_TO_CHAT.get(call_id)
            if not chat_id:
                return
            key = str(chat_id)
            if key not in VC_SESSIONS:
                VC_SESSIONS[key] = {
                    "session_start": int(time.time()),
                    "title": "",
                    "participants": {},
                }
            sess = VC_SESSIONS[key]
            for p in update.participants:
                peer = p.peer
                if not hasattr(peer, "user_id"):
                    continue
                uid = peer.user_id
                us = str(uid)
                fn, un = _vc_get_name(users, uid)
                if p.left:
                    if us in sess["participants"]:
                        rec = sess["participants"][us]
                        if rec.get("left_at"):
                            continue
                        rec["left_at"] = int(time.time())
                        rec["total_seconds"] = rec["left_at"] - rec["joined_at"]
                        log(f"[vc LEFT] {uid} ({fn}) from {chat_id} — {rec['total_seconds']}s")
                else:
                    if us not in sess["participants"]:
                        sess["participants"][us] = {
                            "joined_at": int(p.date or time.time()),
                            "left_at": None,
                            "first_name": fn,
                            "username": un,
                            "total_seconds": 0,
                            "session_count": 1,
                        }
                        log(f"[vc JOIN] {uid} ({fn}) to {chat_id}")
                    else:
                        rec = sess["participants"][us]
                        if rec.get("left_at"):
                            rec["joined_at"] = int(time.time())
                            rec["left_at"] = None
                            rec["session_count"] = rec.get("session_count", 0) + 1
                            log(f"[vc REJOIN] {uid} ({fn}) to {chat_id}")
            _vc_save_state()
        elif isinstance(update, UpdateGroupCall):
            if update.call is None:
                log("[vc CALL END]")
    except Exception as e:
        log(f"[vc] raw_update err: {e}")


async def _vc_poll_active_calls(app):
    """هر ۱۰ ثانیه کال‌های فعال رو کش کن"""
    try:
        async with httpx.AsyncClient(timeout=5) as h:
            r = await h.get(f"{SERVER}/api/groups")
            chats = r.json().get("groups", [])
        log(f"[vc poll] checking {len(chats)} groups")
        for chat_id in chats:
            try:
                peer = await app.resolve_peer(chat_id)
                input_channel = InputChannel(
                    channel_id=peer.channel_id,
                    access_hash=peer.access_hash,
                )
                full = await app.invoke(GetFullChannel(channel=input_channel))
                call = full.full_chat.call
                if call:
                    VC_CALL_TO_CHAT[call.id] = chat_id
                    if str(chat_id) not in VC_SESSIONS:
                        VC_SESSIONS[str(chat_id)] = {
                            "session_start": int(time.time()),
                            "title": getattr(full.chats[0], "title", "") if getattr(full, "chats", None) else "",
                            "participants": {},
                        }
            except Exception as e:
                log(f"[vc poll] {chat_id}: {e}")
            await asyncio.sleep(0.5)
    except Exception as e:
        log(f"[vc] poll err: {e}")


async def _vc_send_stats(app):
    """هر ۶۰ ثانیه آمار به ربات مدیریت بفرست"""
    try:
        for chat_key, sess in list(VC_SESSIONS.items()):
            chat_id = int(chat_key)
            participants = sess.get("participants", {})
            if not participants:
                continue
            now = int(time.time())
            recent = {}
            for us, rec in participants.items():
                last = rec.get("left_at") or rec.get("joined_at") or 0
                if now - last < 6 * 3600:
                    recent[us] = rec
            if not recent:
                continue
            users_list = []
            total = 0
            for us, rec in recent.items():
                if rec.get("left_at"):
                    dur = rec.get("total_seconds") or (rec["left_at"] - rec["joined_at"])
                else:
                    dur = now - rec["joined_at"]
                users_list.append({
                    "user_id": int(us),
                    "first_name": rec.get("first_name", ""),
                    "username": rec.get("username", ""),
                    "total_seconds": int(dur),
                    "session_count": int(rec.get("session_count", 1)),
                })
                total += int(dur)
            date_str = datetime.now().strftime("%Y-%m-%d")
            payload = json.dumps({"total_seconds": total, "users": users_list}, ensure_ascii=False)
            payload_d = {
                "chat_id": chat_id,
                "date": date_str,
                "total_seconds": total,
                "users": users_list,
            }
            try:
                async with httpx.AsyncClient(timeout=10) as _h:
                    _r = await _h.post(f"{SERVER}/vcstat/report", json=payload_d)
                log(f"[vc] stats sent to server: chat={chat_id} users={len(users_list)} total={total}s")
            except Exception as e:
                log(f"[vc] send stats err: {e}")
    except Exception as e:
        log(f"[vc] send_stats err: {e}")


async def _vc_background_loop(app):
    """حلقه‌ی پس‌زمینه برای poll + send"""
    last_poll = 0
    last_send = 0
    while True:
        try:
            now = time.time()
            if now - last_poll >= 10:
                await _vc_poll_active_calls(app)
                last_poll = now
            if now - last_send >= 60:
                await _vc_send_stats(app)
                last_send = now
            await asyncio.sleep(2)
        except Exception as e:
            log(f"[vc] bg err: {e}")
            await asyncio.sleep(5)


# ═══════════════════════════════════════════════
# poll
# ═══════════════════════════════════════════════
async def poll(calls):
    async with httpx.AsyncClient(timeout=30) as h:
        n = 0
        while True:
            try:
                r = await h.get(f"{SERVER}/commands")
                if r.status_code == 200:
                    for c in r.json():
                        try: await handle(c, calls, h)
                        except Exception as e:
                            log(f"handle err: {e}"); log(traceback.format_exc())
                n += 1
                if n % 60 == 0: log(f"[hb] {n}")
            except Exception as e:
                log(f"poll err: {e}")
            await asyncio.sleep(POLL_SEC)

# ═══════════════════════════════════════════════
# main
# ═══════════════════════════════════════════════
async def main():
    log("=== Sk.Media Player START ===")
    log(f"session: {len(SESSION)}")
    app = Client("sk_player", api_id=API_ID, api_hash=API_HASH,
                 session_string=SESSION, workdir="/root/melody-player")
    calls = PyTgCalls(app)
    @calls.on_update()
    async def _u(client, update):
        log(f"[upd] {type(update).__name__}")
    app.add_handler(RawUpdateHandler(_vc_on_raw_update))
    _vc_load_state()
    await app.start()
    me = await app.get_me()
    log(f"me: @{me.username}")
    await calls.start()
    asyncio.create_task(_vc_background_loop(app))
    log("✅ ready — polling + voice monitor")
    try:
        await poll(calls)
    except KeyboardInterrupt:
        pass
    finally:
        try: await app.stop()
        except: pass

if __name__ == "__main__":
    asyncio.run(main())
