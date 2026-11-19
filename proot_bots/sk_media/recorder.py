#!/usr/bin/env python3
"""Sk.Media Voice Chat Recorder — state machine"""
import asyncio, os, sys, time, subprocess, json
from datetime import datetime
from pathlib import Path
import httpx

SERVER = os.environ.get("SK_SERVER", "http://127.0.0.1:8080")

SHARED_REC = "/data/data/com.termux/files/home/sk_media/recordings"
LOCAL_TMP = "/root/sk_media/recordings_temp"
os.makedirs(SHARED_REC, exist_ok=True)
os.makedirs(LOCAL_TMP, exist_ok=True)

def log(*a):
    sys.stderr.write(" ".join(str(x) for x in a) + "\n")
    sys.stderr.flush()

# ─── state ───
STATE = {}  # {chat_id: {"enabled": bool, "clip_sec": int, "started_at": float, "task": Task, "paused": bool}}


async def start_rec(calls, chat_id, clip_sec=300):
    """شروع/ادامه رکورد"""
    st = STATE.setdefault(chat_id, {
        "enabled": True,
        "clip_sec": clip_sec,
        "task": None,
        "started_at": time.time(),
        "seg_idx": 0,
    })
    st["enabled"] = True
    st["clip_sec"] = clip_sec
    # اگه task فعاله، کاری نکن
    t = st.get("task")
    if t and not t.done():
        log(f"[rec] already running {chat_id}")
        return
    st["task"] = asyncio.create_task(_loop(calls, chat_id))
    log(f"[rec] ▶️  start {chat_id} clip={clip_sec}s")


async def stop_rec(calls, chat_id, pause_only=False):
    """توقف رکورد"""
    st = STATE.get(chat_id)
    if not st:
        return
    if pause_only:
        # فقط pause کن، enabled بمونه True
        st["_paused"] = True
        t = st.get("task")
        if t and not t.done():
            t.cancel()
        st["task"] = None
        try: await calls.record(chat_id, None)
        except: pass
        log(f"[rec] ⏸ pause {chat_id}")
        return
    # توقف کامل
    st["enabled"] = False
    t = st.get("task")
    if t and not t.done():
        try: t.cancel()
        except: pass
    STATE.pop(chat_id, None)
    try: await calls.record(chat_id, None)
    except: pass
    log(f"[rec] ⏹ stop {chat_id}")


async def resume_rec(calls, chat_id):
    """ادامه رکورد بعد پایان موزیک"""
    st = STATE.get(chat_id)
    if not st or not st.get("enabled"):
        return
    st.pop("_paused", None)
    t = st.get("task")
    if t and not t.done():
        return
    st["task"] = asyncio.create_task(_loop(calls, chat_id))
    log(f"[rec] ▶️  resume {chat_id}")


async def _loop(calls, chat_id):
    """حلقه رکورد — هر clip_sec یه segment"""
    st = STATE.get(chat_id)
    if not st:
        return
    try:
        while st.get("enabled") and not st.get("_paused"):
            clip = st["clip_sec"]
            idx = st["seg_idx"]
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            pcm = f"{LOCAL_TMP}/rec_{chat_id}_{idx}_{ts}.pcm"
            mp3 = f"{SHARED_REC}/rec_{chat_id}_{ts}_{clip}s.mp3"
            log(f"[rec] seg #{idx} ({clip}s) → {os.path.basename(mp3)}")
            try:
                await calls.record(chat_id, pcm)
            except Exception as e:
                log(f"[rec] record err: {e}")
                await asyncio.sleep(15)
                continue
            # صبر clip_sec
            try:
                await asyncio.sleep(clip)
            except asyncio.CancelledError:
                # قطع شد — ولی segment رو ذخیره کن
                pass
            try:
                await calls.record(chat_id, None)
            except: pass
            # تبدیل
            try:
                _pcm2mp3(pcm, mp3, chat_id)
                sz = os.path.getsize(mp3) // 1024
                log(f"[rec] ✅ {os.path.basename(mp3)} ({sz}KB)")
                await _notify(chat_id, mp3, clip)
            except Exception as e:
                log(f"[rec] convert err: {e}")
            finally:
                try: os.remove(pcm)
                except: pass
            st["seg_idx"] += 1
            # اگه paused یا stopped شده، بیرون
            if st.get("_paused") or not st.get("enabled"):
                break
    except asyncio.CancelledError:
        log(f"[rec] loop cancelled {chat_id}")
    except Exception as e:
        log(f"[rec] loop err: {e}")


def _pcm2mp3(pcm, mp3, chat_id):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "s16le", "-ar", "48000", "-ac", "1",
         "-i", pcm, "-c:a", "libmp3lame", "-b:a", "128k", mp3],
        check=True, capture_output=True, timeout=120,
    )
    try:
        from mutagen.mp3 import MP3
        from mutagen.id3 import TIT2, TPE1, TALB, COMM
        a = MP3(mp3)
        if a.tags is None: a.add_tags()
        now = datetime.now()
        a.tags["TIT2"] = TIT2(encoding=3, text=f"🎙 ضبط {now.strftime('%Y/%m/%d - %H:%M')}")
        a.tags["TPE1"] = TPE1(encoding=3, text="Sk.Team")
        a.tags["TALB"] = TALB(encoding=3, text="Sk.Team Recorder")
        a.tags["COMM"] = COMM(encoding=3, lang="eng", desc="",
                              text=f"@SkTeamMusic_Bot | chat={chat_id}")
        a.save()
    except Exception as e:
        log(f"[rec] id3 err: {e}")


async def _notify(chat_id, mp3, clip):
    try:
        async with httpx.AsyncClient(timeout=10) as h:
            await h.post(f"{SERVER}/record_ready", json={
                "chat_id": chat_id, "path": mp3,
                "clip_sec": clip, "ts": int(time.time()),
            })
    except Exception as e:
        log(f"[rec] notify err: {e}")


async def handle_cmd(calls, cmd):
    a = (cmd.get("action") or "").lower()
    cid = int(cmd.get("chat_id", 0))
    if a == "record_start":
        await start_rec(calls, cid, int(cmd.get("clip_sec", 300)))
    elif a == "record_stop":
        await stop_rec(calls, cid, pause_only=False)
    elif a == "record_pause":
        await stop_rec(calls, cid, pause_only=True)
    elif a == "record_resume":
        await resume_rec(calls, cid)
