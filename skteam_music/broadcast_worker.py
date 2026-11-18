"""broadcast_worker.py — پردازش صف پیام سراسری (ربات موزیک)"""
import asyncio, sqlite3, logging, datetime
from pathlib import Path
log = logging.getLogger("bc_music")


async def _process_queue(app):
    await asyncio.sleep(45)
    while True:
        try:
            gb = Path.home() / "groupbot" / "data" / "groupbot.db"
            if not gb.exists():
                await asyncio.sleep(60)
                continue
            c = sqlite3.connect(str(gb), timeout=5)
            rows = c.execute("""SELECT id, text, target FROM broadcast_queue 
                                WHERE sent_by_music = 0 LIMIT 5""").fetchall()
            c.close()
            for rid, text, target in rows:
                try:
                    # فقط گروه‌ها (ربات موزیک توی گروه‌ها عضوه)
                    c = sqlite3.connect(str(gb), timeout=5)
                    chats = set()
                    if target in ("groups", "all"):
                        for r in c.execute("SELECT chat_id FROM groups").fetchall():
                            chats.add(r[0])
                    # برای مالکین هم تلاش کن ولی اگه fail شد ok
                    if target in ("owners", "all"):
                        for r in c.execute("SELECT DISTINCT user_id FROM group_owners").fetchall():
                            chats.add(r[0])
                    if target in ("admins", "all"):
                        for r in c.execute("SELECT user_id FROM bot_admins").fetchall():
                            chats.add(r[0])
                    c.close()
                    ok = 0; fail = 0
                    for cid in chats:
                        try:
                            await app.bot.send_message(cid, text)
                            ok += 1
                        except Exception:
                            fail += 1
                        await asyncio.sleep(0.05)
                    # علامت بزن
                    c = sqlite3.connect(str(gb), timeout=5)
                    c.execute("""UPDATE broadcast_queue 
                                 SET sent_by_music=1, music_sent_at=?, music_ok=?, music_fail=?
                                 WHERE id=?""",
                              (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ok, fail, rid))
                    c.commit(); c.close()
                    log.warning(f"[BC-MUSIC] #{rid} ok={ok} fail={fail}")
                except Exception as e:
                    log.warning(f"[BC-MUSIC] process err: {e}")
                    try:
                        c = sqlite3.connect(str(gb), timeout=5)
                        c.execute("UPDATE broadcast_queue SET sent_by_music=1 WHERE id=?", (rid,))
                        c.commit(); c.close()
                    except: pass
            await asyncio.sleep(30)
        except Exception as e:
            log.warning(f"[BC-MUSIC] loop err: {e}")
            await asyncio.sleep(60)


def start(app):
    """شروع کن — از post_init صدا زده میشه"""
    app.create_task(_process_queue(app))
    log.warning("[BC-MUSIC] worker started")
