"""Userbot Service — با Pyrogram + Telethon fallback + بهتر error handling"""
import asyncio
import os
import sys
import logging
from datetime import datetime

# ★ event loop قبل از import pyrogram
_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyrogram import Client
from userbot_config import API_ID, API_HASH, STRING_SESSION
from config import DATABASE_PATH
import turso_db as sqlite3

LOG_FILE = os.path.expanduser("~/userbot_service.log")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("userbot_service")


def get_pending():
    """دریافت درخواست‌های زیربات در انتظار"""
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=5)
        c = conn.cursor()
        c.execute("SELECT id, chat_id, msg_id, count, requested_by FROM purge_requests WHERE status = 'pending' ORDER BY id ASC LIMIT 10")
        rows = c.fetchall()
        conn.close()
        return rows
    except sqlite3.OperationalError as e:
        log.error(f"Database lock in get_pending: {e}")
        return []
    except sqlite3.DatabaseError as e:
        log.error(f"Database error in get_pending: {e}")
        return []
    except Exception as e:
        log.error(f"Unexpected error in get_pending: {e}")
        return []
    except Exception as e:
        log(f"get_pending ERR: {e}")
        return []


def mark_done(req_id, result):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("UPDATE purge_requests SET status = 'done', result = ?, processed_at = CURRENT_TIMESTAMP WHERE id = ?", (result, req_id))
        conn.commit()
        conn.close()
    except Exception as e:
        log(f"mark_done ERR: {e}")


def get_pending_joins():
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT id, chat_id, invite_link FROM userbot_join_queue WHERE status='pending' ORDER BY id ASC LIMIT 10")
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        log(f"get_pending_joins ERR: {e}")
        return []


def mark_join_done(req_id, result):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("UPDATE userbot_join_queue SET status='done', result=?, processed_at=CURRENT_TIMESTAMP WHERE id=?", (result, req_id))
        conn.commit()
        conn.close()
    except Exception as e:
        log(f"mark_join_done ERR: {e}")


async def process_join(app, req_id, chat_id, invite_link):
    log(f"Join #{req_id}: chat={chat_id}")
    try:
        # استخراج hash
        if "+" in invite_link:
            hash_part = invite_link.split("+")[-1]
        else:
            hash_part = invite_link.rstrip("/").split("/")[-1]
        log(f"  hash: {hash_part}")
        # ★ raw API برای invite link
        from pyrogram.raw.functions.messages import ImportChatInvite, CheckChatInvite
        try:
            _check = await app.invoke(CheckChatInvite(hash=hash_part))
            print(f'[JOIN] check: {type(_check).__name__}')
            if hasattr(_check, 'chat'):
                print(f'[JOIN] از قبل عضوه: {_check.chat.title}')
                chat = _check.chat
            else:
                raise ValueError('need join')
        except Exception as _check_err:
            if 'USER_ALREADY_PARTICIPANT' in str(_check_err):
                print(f'[JOIN] از قبل عضوه')
                chat = None
            else:
                _result = await app.invoke(ImportChatInvite(hash=hash_part))
                if hasattr(_result, 'chats') and _result.chats:
                    chat = _result.chats[0]
                    print(f'[JOIN] ✅ موفق: {chat.title}')
                else:
                    chat = None
        log(f"  ✅ join موفق: {chat.title}")
        mark_join_done(req_id, f"عضو شد: {chat.title}")
    except Exception as e:
        log(f"  ❌ join خطا: {e}")
        mark_join_done(req_id, f"خطا: {e}")



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
        result += f" ({failed} قابل حذف نبود)"
    mark_done(req_id, result)
    log(f"✅ #{req_id}: {result}")
    return deleted, failed


async def main():
    _sk_acquire_lock("userbot")
    log("=" * 50)
    log("Userbot Service started")
    log(f"API_ID: {API_ID}")
    log("=" * 50)
    
    app = Client(
        name="userbot_service",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        no_updates=True,  # ★ بدون update handler
    )
    await app.start()
    me = await app.get_me()
    log(f"✅ وصل شدم: {me.first_name} (@{me.username}, id={me.id})")
    
    while True:
        try:
            # ★ پردازش join queue
            joins = get_pending_joins()
            if joins:
                log(f"📥 {len(joins)} join pending")
                for j in joins:
                    j_id, j_chat, j_link = j
                    try:
                        await process_join(app, j_id, j_chat, j_link)
                    except Exception as e:
                        log(f"❌ join #{j_id}: {e}")
                        mark_join_done(j_id, f"خطا: {e}")
                await asyncio.sleep(2)

            pending = get_pending()
            if pending:
                log(f"📥 {len(pending)} درخواست")
                for row in pending:
                    req_id, chat_id, msg_id, count, requested_by = row
                    try:
                        await process_request(app, req_id, chat_id, msg_id, count, requested_by)
                    except Exception as e:
                        log(f"❌ #{req_id}: {e}")
                        mark_done(req_id, f"خطا: {e}")
            await asyncio.sleep(3)
        except Exception as e:
            log(f"❌ حلقه: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    _loop.run_until_complete(main())
