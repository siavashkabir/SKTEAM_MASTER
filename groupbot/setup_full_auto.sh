#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "🚀 راه‌اندازی auto-join + auto-promote کامل"
echo "═══════════════════════════════════════════════════"
echo ""

source venv/bin/activate

# ═══════════════════════════════════════════════════
# ۱. جدول userbot_join_queue
# ═══════════════════════════════════════════════════
echo "─── ۱. ساخت جدول userbot_join_queue ───"
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS userbot_join_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        invite_link TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        result TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed_at TIMESTAMP
    )
""")
conn.commit()
conn.close()
print("✅ جدول ساخته شد")
PYEOF
echo ""

# ═══════════════════════════════════════════════════
# ۲. توابع دیتابیس
# ═══════════════════════════════════════════════════
echo "─── ۲. اضافه کردن توابع به database.py ───"
python3 << 'PYEOF'
DB = "database.py"
with open(DB, "r", encoding="utf-8") as f:
    content = f.read()

if "def queue_userbot_join" in content:
    print("⚠️ از قبل هست")
else:
    content += '''


def queue_userbot_join(chat_id, invite_link):
    """ثبت درخواست join userbot"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        # چک کن قبلاً نبوده
        c.execute("SELECT id FROM userbot_join_queue WHERE chat_id=? AND status='pending'", (chat_id,))
        if c.fetchone():
            conn.close()
            return None
        c.execute("INSERT INTO userbot_join_queue (chat_id, invite_link) VALUES (?, ?)",
                  (chat_id, invite_link))
        req_id = c.lastrowid
        conn.commit()
        conn.close()
        print(f"[QUEUE JOIN] id={req_id}, chat={chat_id}")
        return req_id
    except Exception as e:
        print(f"[QUEUE JOIN ERR] {e}")
        return None


def get_pending_joins():
    """درخواست‌های join pending"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT id, chat_id, invite_link FROM userbot_join_queue WHERE status='pending' ORDER BY id ASC LIMIT 10")
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[GET JOINS ERR] {e}")
        return []


def mark_join_done(req_id, result):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("UPDATE userbot_join_queue SET status='done', result=?, processed_at=CURRENT_TIMESTAMP WHERE id=?", (result, req_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[MARK JOIN ERR] {e}")
'''
    with open(DB, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ توابع اضافه شد")
PYEOF
echo ""

if python3 -m py_compile database.py 2>&1; then
    echo "✅ database.py OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

# ═══════════════════════════════════════════════════
# ۳. ماژول userbot_autojoin (بازنویسی)
# ═══════════════════════════════════════════════════
echo "─── ۳. بازنویسی userbot_autojoin.py ───"
cat > modules/userbot_autojoin.py << 'PYEOF'
"""Auto: وقتی ربات به گروه جدید می‌ره، userbot رو با invite link میاره + ادمینش می‌کنه."""
import asyncio
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes

USERBOT_ID = 8250087472
USERBOT_USERNAME = "Skmusic001"


async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not msg.new_chat_members:
        return
    if chat.type not in ("group", "supergroup"):
        return

    bot_id = context.bot.id
    if not any(m.id == bot_id for m in msg.new_chat_members):
        return

    print(f"[AUTOJOIN] ربات به {chat.id} ({chat.title}) اضافه شد")
    await asyncio.sleep(3)

    # چک کن userbot از قبل عضوه
    userbot_in = False
    try:
        ub = await context.bot.get_chat_member(chat.id, USERBOT_ID)
        if ub.status not in ("left", "kicked"):
            userbot_in = True
            print(f"[AUTOJOIN] userbot از قبل عضوه ({ub.status})")
    except Exception:
        pass

    if not userbot_in:
        # ★ لینک invite بساز + queue کن
        try:
            from database import queue_userbot_join
            link = await context.bot.create_chat_invite_link(
                chat_id=chat.id,
                name=f"Userbot Join {chat.id}",
                member_limit=1,
            )
            print(f"[AUTOJOIN] لینک ساخته شد: {link.invite_link}")
            req_id = queue_userbot_join(chat.id, link.invite_link)
            if req_id:
                print(f"[AUTOJOIN] queue شد (id={req_id})")
                try:
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text="⏳ در حال فعال‌سازی دستیار گروه..."
                    )
                except Exception:
                    pass
        except Exception as e:
            print(f"[AUTOJOIN] لینک خطا: {e}")

    # اگه userbot عضو بود ولی ادمین نبود، promote کن
    if userbot_in:
        try:
            ub = await context.bot.get_chat_member(chat.id, USERBOT_ID)
            if ub.status == "member":
                await context.bot.promote_chat_member(
                    chat_id=chat.id,
                    user_id=USERBOT_ID,
                    can_delete_messages=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_invite_users=True,
                    can_change_info=False,
                    can_promote_members=False,
                    can_manage_video_chats=True,
                    can_manage_chat=False,
                    is_anonymous=False,
                )
                print(f"[AUTOJOIN] ✅ userbot promote شد")
        except Exception as e:
            print(f"[AUTOJOIN PROMOTE ERR] {e}")


async def auto_promote_job(context: ContextTypes.DEFAULT_TYPE):
    """job دوره‌ای: چک کن userbot عضوه ولی ادمین نیست → promote"""
    try:
        import sqlite3
        from config import DATABASE_PATH
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT chat_id FROM groups")
        chats = [r[0] for r in c.fetchall()]
        conn.close()

        for cid in chats:
            try:
                ub = await context.bot.get_chat_member(cid, USERBOT_ID)
                if ub.status == "member":
                    await context.bot.promote_chat_member(
                        chat_id=cid,
                        user_id=USERBOT_ID,
                        can_delete_messages=True,
                        can_restrict_members=True,
                        can_pin_messages=True,
                        can_invite_users=True,
                        can_change_info=False,
                        can_promote_members=False,
                        can_manage_video_chats=True,
                        can_manage_chat=False,
                        is_anonymous=False,
                    )
                    print(f"[AUTOPROMOTE JOB] userbot در {cid} promote شد")
                    try:
                        await context.bot.send_message(
                            chat_id=cid,
                            text="✅ دستیار گروه فعال شد."
                        )
                    except Exception:
                        pass
            except Exception:
                pass
            await asyncio.sleep(3)
    except Exception as e:
        print(f"[AUTOPROMOTE JOB ERR] {e}")


def register(app):
    # handler
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            on_bot_added,
            block=False
        ),
        group=-8
    )
    # job دوره‌ای هر ۳۰ ثانیه
    if hasattr(app, 'job_queue') and app.job_queue:
        app.job_queue.run_repeating(auto_promote_job, interval=30, first=10)
        print("OK userbot_autojoin job registered")
    print("OK module userbot_autojoin loaded")
PYEOF

if python3 -m py_compile modules/userbot_autojoin.py 2>&1; then
    echo "✅ userbot_autojoin.py OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

# ═══════════════════════════════════════════════════
# ۴. آپدیت userbot_service.py
# ═══════════════════════════════════════════════════
echo "─── ۴. آپدیت userbot_service.py ───"
python3 << 'PYEOF'
US = "userbot_service.py"
with open(US, "r", encoding="utf-8") as f:
    content = f.read()

# اضافه کردن توابع join
if "get_pending_joins" not in content:
    # اضافه بعد از import ها
    import re
    # پیدا کردن محل مناسب (بعد از mark_done)
    marker = "def mark_done(req_id, result):"
    idx = content.find(marker)
    if idx == -1:
        print("❌ mark_done پیدا نشد")
        exit(1)

    # پیدا کردن انتهای mark_done
    end_marker = 'log(f"mark_done ERR: {e}")'
    end_idx = content.find(end_marker, idx) + len(end_marker)
    
    join_funcs = '''


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
        chat = await app.join_chat(hash_part)
        log(f"  ✅ join موفق: {chat.title}")
        mark_join_done(req_id, f"عضو شد: {chat.title}")
    except Exception as e:
        log(f"  ❌ join خطا: {e}")
        mark_join_done(req_id, f"خطا: {e}")
'''
    content = content[:end_idx] + join_funcs + content[end_idx:]

    # اضافه کردن به حلقه main
    old_loop = '''            pending = get_pending()
            if pending:'''
    new_loop = '''            # ★ پردازش join queue
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
            if pending:'''
    
    if old_loop in content:
        content = content.replace(old_loop, new_loop, 1)
        print("✅ join loop اضافه شد")
    else:
        print("⚠️ حلقه پیدا نشد")

    with open(US, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ userbot_service.py آپدیت شد")
else:
    print("⚠️ از قبل هست")
PYEOF

if python3 -m py_compile userbot_service.py 2>&1; then
    echo "✅ userbot_service.py OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

# ═══════════════════════════════════════════════════
# ۵. ری‌استارت
# ═══════════════════════════════════════════════════
echo "─── ۵. ری‌استارت ───"

# userbot
pkill -9 -f "userbot_service.py" 2>/dev/null
sleep 2
nohup python3 -u userbot_service.py > ~/userbot_service.log 2>&1 &
echo "✅ userbot_service بالا اومد"

# ربات Manager
pkill -9 -f 'python3 -u main.py' 2>/dev/null
sleep 3
rm -f .bot.lock
nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &
echo "✅ ربات Manager بالا اومد"

sleep 10

echo ""
echo "─── چک نهایی ───"
pgrep -af "userbot_service.py"
pgrep -af "python3 -u main.py"

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ راه‌اندازی کامل شد"
echo ""
echo "🎯 حالا تست:"
echo ""
echo "1. برو توی گروه جدیدی که userbot نیست (مثلاً HERITAGE)"
echo "2. ربات Manager رو بردار و دوباره اضافه کن"
echo "3. صبر کن ۱۰-۳۰ ثانیه"
echo "4. باید ببینی:"
echo "   - ربات لینک invite می‌سازه"
echo "   - userbot با لینک join می‌شه"
echo "   - ربات userbot رو ادمین می‌کنه"
echo "═══════════════════════════════════════════════════"
