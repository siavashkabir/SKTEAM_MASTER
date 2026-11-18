#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "🤖 راه‌اندازی Userbot"
echo "═══════════════════════════════════════════════════"
echo ""

source venv/bin/activate

# ═══════════════════════════════════════════════════
# ۱. جدول purge_requests
# ═══════════════════════════════════════════════════
echo "─── ۱. ساخت جدول purge_requests ───"
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS purge_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        msg_id INTEGER NOT NULL,
        count INTEGER NOT NULL,
        requested_by INTEGER NOT NULL,
        status TEXT DEFAULT 'pending',
        result TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP
    )
""")
conn.commit()

# چک
c.execute("PRAGMA table_info(purge_requests)")
print("ستون‌ها:")
for r in c.fetchall(): print(f"  {r}")

conn.close()
print("✅ جدول purge_requests ساخته شد")
PYEOF

echo ""

# ═══════════════════════════════════════════════════
# ۲. userbot_service.py
# ═══════════════════════════════════════════════════
echo "─── ۲. ساخت userbot_service.py ───"
cat > userbot_service.py << 'PYEOF'
#!/usr/bin/env python3
"""
Userbot Service — با Telethon به تلگرام وصل می‌شه
و درخواست‌های پاکسازی رو از دیتابیس می‌خونه و انجام می‌ده.
"""
import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import DeleteMessagesRequest
from telethon.tl.functions.messages import DeleteMessagesRequest as DeleteMessagesReq

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
    """درخواست‌های pending رو بگیر"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT id, chat_id, msg_id, count, requested_by
            FROM purge_requests
            WHERE status = 'pending'
            ORDER BY id ASC
            LIMIT 10
        """)
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
        c.execute("""
            UPDATE purge_requests
            SET status = 'done', result = ?, processed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (result, req_id))
        conn.commit()
        conn.close()
    except Exception as e:
        log(f"mark_done ERR: {e}")


async def process_request(client, req_id, chat_id, msg_id, count, requested_by):
    """یه درخواست پاکسازی رو انجام بده"""
    log(f"پردازش #{req_id}: chat={chat_id}, msg={msg_id}, count={count}")
    
    deleted = 0
    failed = 0
    
    # آیدی‌های پیام (از msg_id به عقب)
    ids = list(range(msg_id, max(0, msg_id - count), -1))
    
    # دسته‌بندی ۱۰۰ تایی
    for i in range(0, len(ids), 100):
        chunk = ids[i:i+100]
        try:
            # با MTProto پاک کن
            await client.delete_messages(chat_id, chunk)
            deleted += len(chunk)
            log(f"  ✅ دسته {i//100 + 1}: {len(chunk)} پیام")
        except Exception as e:
            log(f"  ❌ دسته {i//100 + 1} خطا: {e}")
            # تک‌تک
            for mid in chunk:
                try:
                    await client.delete_messages(chat_id, [mid])
                    deleted += 1
                except Exception:
                    failed += 1
        await asyncio.sleep(0.5)  # anti-flood
    
    result = f"{deleted} پیام پاک شد"
    if failed > 0:
        result += f" ({failed} پیام قابل حذف نبود)"
    
    mark_done(req_id, result)
    log(f"✅ #{req_id}: {result}")
    
    return deleted, failed


async def main():
    log("=" * 50)
    log("Userbot Service started")
    log(f"API_ID: {API_ID}")
    log("=" * 50)
    
    client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    await client.start()
    
    me = await client.get_me()
    log(f"✅ وصل شدم به: {me.first_name} (@{me.username}, id={me.id})")
    
    while True:
        try:
            pending = get_pending()
            if pending:
                log(f"📥 {len(pending)} درخواست pending")
                for row in pending:
                    req_id, chat_id, msg_id, count, requested_by = row
                    try:
                        await process_request(client, req_id, chat_id, msg_id, count, requested_by)
                    except Exception as e:
                        log(f"❌ req #{req_id} خطا: {e}")
                        mark_done(req_id, f"خطا: {e}")
            
            await asyncio.sleep(3)
        except Exception as e:
            log(f"❌ حلقه خطا: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())
PYEOF

chmod +x userbot_service.py
echo "✅ userbot_service.py ساخته شد"
echo ""

# ═══════════════════════════════════════════════════
# ۳. تست import
# ═══════════════════════════════════════════════════
echo "─── ۳. تست import ───"
python3 -c "
import sys
sys.path.insert(0, '.')
from userbot_config import API_ID, API_HASH, STRING_SESSION
from telethon import TelegramClient
from telethon.sessions import StringSession
print('✅ همه import ها OK')
print(f'   API_ID: {API_ID}')
"

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ راه‌اندازی انجام شد"
echo ""
echo "🎯 قدم بعدی: تست اتصال userbot"
echo ""
echo "این رو بزن:"
echo "cd ~/groupbot && timeout 30 python3 userbot_service.py"
echo "═══════════════════════════════════════════════════"
