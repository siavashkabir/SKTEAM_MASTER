"""broadcast_worker.py — پردازش صف پیام سراسری (نسخه ۲ با job_queue)"""
import asyncio, sqlite3, logging, datetime
from pathlib import Path

log = logging.getLogger("broadcast_worker")


async def _process_once(app):
    """یک بار پردازش صف"""
    from config import DATABASE_PATH
    try:
        c = sqlite3.connect(DATABASE_PATH, timeout=5)
        rows = c.execute("""SELECT id, text, target FROM broadcast_queue 
                            WHERE sent_by_manager = 0 LIMIT 5""").fetchall()
        c.close()
        if not rows:
            return
        for rid, text, target in rows:
            try:
                c = sqlite3.connect(DATABASE_PATH, timeout=5)
                chats = set()
                if target in ("groups", "all"):
                    for r in c.execute("SELECT chat_id FROM groups").fetchall():
                        chats.add(r[0])
                if target in ("owners", "all"):
                    for r in c.execute("SELECT DISTINCT user_id FROM group_owners").fetchall():
                        chats.add(r[0])
                if target in ("admins", "all"):
                    for r in c.execute("SELECT user_id FROM bot_admins").fetchall():
                        chats.add(r[0])
                c.close()
                ok = 0
                fail = 0
                for cid in chats:
                    try:
                        await app.bot.send_message(cid, text)
                        ok += 1
                    except Exception:
                        fail += 1
                    await asyncio.sleep(0.05)
                c = sqlite3.connect(DATABASE_PATH, timeout=5)
                c.execute("""UPDATE broadcast_queue 
                             SET sent_by_manager=1, manager_sent_at=?, manager_ok=?, manager_fail=?
                             WHERE id=?""",
                          (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ok, fail, rid))
                c.commit()
                c.close()
                log.info(f"[BC-MGR] #{rid} ok={ok} fail={fail}")
            except Exception as e:
                log.warning(f"[BC-MGR] process err: {e}")
                try:
                    c = sqlite3.connect(DATABASE_PATH, timeout=5)
                    c.execute("UPDATE broadcast_queue SET sent_by_manager=1 WHERE id=?", (rid,))
                    c.commit()
                    c.close()
                except:
                    pass
    except Exception as e:
        log.warning(f"[BC-MGR] once err: {e}")


async def _job_callback(context):
    """callback برای job_queue"""
    await _process_once(context.application)


def register(app):
    """ثبت با job_queue"""
    try:
        jq = app.job_queue
        if jq:
            jq.run_repeating(_job_callback, interval=30, first=30, name="broadcast_worker")
            print("[broadcast_worker] registered (job_queue)")
        else:
            print("[broadcast_worker] no job_queue - skipping")
    except Exception as e:
        print(f"[broadcast_worker] register err: {e}")
