#!/usr/bin/env python3
"""Userbot Service — با Pyrogram"""
import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyrogram import Client
from userbot_config import API_ID, API_HASH, STRING_SESSION
from config import DATABASE_PATH
import sqlite3

LOG_FILE = os.path.expanduser("~/userbot_service.log")


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def get_pending():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT id, chat_id, msg_id, count, requested_by FROM purge_requests WHERE status = %s ORDER BY id ASC LIMIT 10" % "pending")
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        log(f"get_pending ERR: {e}")
        return []


def mark_done(req_id, result):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("UPDATE purge_requests SET status = %s, result = ?, processed_at = CURRENT_TIMESTAMP WHERE id = ?" % "done", (result, req_id))
        conn.commit()
        conn.close()
    except Exception as e:
        log(f"mark_done ERR: {e}")


async def process_request(app, req_id, chat_id, msg_id, count, requested_by):
    log(f"پردازش #{req_id}: chat={chat_id}, msg={msg_id}, count={count}")
    deleted = 0
    failed = 0
    ids = list(range(msg_id, max(0, msg_id - count), -1))
    for i in range(0, len(ids), 100):
        chunk = ids[i:i+100]
        try:
            await app.delete_messages(chat_id, chunk)
            deleted += len(chunk)
            log(f"  ✅ دسته {i//100 + 1}: {len(chunk)} پیام")
        except Exception as e:
            log(f"  ❌ دسته {i//100 + 1} خطا: {e}")
            for mid in chunk:
                try:
                    await app.delete_messages(chat_id, mid)
                    deleted += 1
                except Exception:
                    failed += 1
        await asyncio.sleep(0.5)
    result = f"{deleted} پیام پاک شد"
    if failed > 0:
        result += f" ({failed} پیام قابل حذف نبود)"
    mark_done(req_id, result)
    log(f"✅ #{req_id}: {result}")
    return deleted, failed


async def main():
    log("=" * 50)
    log("Userbot Service (Pyrogram) started")
    log(f"API_ID: {API_ID}")
    log("=" * 50)
    app = Client(name="userbot_session", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
    await app.start()
    me = await app.get_me()
    log(f"✅ وصل شدم به: {me.first_name} (@{me.username}, id={me.id})")
    while True:
        try:
            pending = get_pending()
            if pending:
                log(f"📥 {len(pending)} درخواست pending")
                for row in pending:
                    req_id, chat_id, msg_id, count, requested_by = row
                    try:
                        await process_request(app, req_id, chat_id, msg_id, count, requested_by)
                    except Exception as e:
                        log(f"❌ req #{req_id} خطا: {e}")
                        mark_done(req_id, f"خطا: {e}")
            await asyncio.sleep(3)
        except Exception as e:
            log(f"❌ حلقه خطا: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
