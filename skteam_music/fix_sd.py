import subprocess
from pathlib import Path

OUT = Path("/data/data/com.termux/files/home/player_spd.py")

r = subprocess.run(
    ["proot-distro", "login", "ubuntu", "--", "bash", "-c", "cat /root/sk_media/player.py"],
    capture_output=True, text=True
)
c = r.stdout

if "speed_delta" not in c or 'action == "speed_delta"' not in c:
    print("⚠️ speed_delta اصلاً نیست، اضافه می‌کنم")

# ─── چک کن bloc فعلی چیه ───
import re
m = re.search(r'elif action == "speed_delta":.*?(?=\n        elif|\n        else)', c, re.DOTALL)
if m:
    print(f"─── speed_delta فعلی ───\n{m.group()[:500]}")

new_sd = '''        elif action == "speed_delta":
            ch_key = str(chat_id)
            state = PLAY_STATE.get(ch_key, {})
            cur = float(state.get("speed", 1.0))
            delta = float(cmd.get("delta", 0))
            val = max(0.5, min(2.0, cur + delta))
            src = state.get("src_path")
            log(f"[speed_delta] cur={cur} delta={delta} val={val} src={src}")
            if not src or not os.path.exists(src):
                log("[speed_delta] no src, just set state")
                if ch_key in PLAY_STATE:
                    PLAY_STATE[ch_key]["speed"] = val
                await report("playing", title=state.get("title", "—"),
                             duration=state.get("duration", 0), speed=val)
                return
            await report("joining", title=state.get("title", "—"),
                         duration=state.get("duration", 0), speed=val)
            try:
                try: await calls.leave_call(chat_id)
                except: pass
                await asyncio.sleep(0.5)
                eq = state.get("eq")
                new_path, new_dur = await asyncio.to_thread(
                    process_audio, src, f"spd{val}", 0, val, eq
                )
                stream = MediaStream(new_path, audio_parameters=AudioQuality.HIGH,
                                     video_flags=MediaStream.Flags.IGNORE)
                await calls.play(chat_id, stream)
                import time as _t
                PLAY_STATE[ch_key]["started_at"] = _t.time()
                PLAY_STATE[ch_key]["position"] = 0
                PLAY_STATE[ch_key]["speed"] = val
                PLAY_STATE[ch_key]["src_path"] = new_path
                PLAY_STATE[ch_key]["duration"] = new_dur
                PLAY_STATE[ch_key]["active"] = True
                PLAY_STATE[ch_key]["playing"] = True
                await report("playing", title=state.get("title", "—"),
                             duration=new_dur, position=0, speed=val)
                log(f"[speed_delta] ✅ {val}x")
            except Exception as e:
                log(f"[speed_delta] err: {e}")
                await report("error", error=f"speed: {e}")
'''

if m:
    c = c[:m.start()] + new_sd + c[m.end():]
    print("✅ speed_delta جایگزین شد")
else:
    # اضافه قبل از cycle_repeat
    marker = '        elif action == "cycle_repeat":'
    if marker in c:
        c = c.replace(marker, new_sd + "\n" + marker, 1)
        print("✅ speed_delta اضافه شد")

OUT.write_text(c, encoding="utf-8")
import py_compile
py_compile.compile(str(OUT), doraise=True)
print(f"✅ ذخیره: {OUT}")
print(f"✅ compile OK")
