#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "🚀 راه‌اندازی نهایی userbot"
echo "═══════════════════════════════════════════════════"
echo ""

source venv/bin/activate

# ═══════════════════════════════════════════════════
# ۱. تابع `queue_purge` توی database.py
# ═══════════════════════════════════════════════════
echo "─── ۱. اضافه کردن queue_purge ───"

python3 << 'PYEOF'
DB = "database.py"

with open(DB, "r", encoding="utf-8") as f:
    content = f.read()

if "def queue_purge" in content:
    print("⚠️ از قبل هست")
else:
    content += '''


def queue_purge(chat_id, msg_id, count, requested_by):
    """ثبت درخواست پاکسازی برای userbot"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO purge_requests (chat_id, msg_id, count, requested_by)
            VALUES (?, ?, ?, ?)
        """, (chat_id, msg_id, count, requested_by))
        req_id = c.lastrowid
        conn.commit()
        conn.close()
        print(f"[QUEUE PURGE] id={req_id}, chat={chat_id}, count={count}")
        return req_id
    except Exception as e:
        print(f"[QUEUE PURGE ERR] {e}")
        return None


def get_purge_result(req_id):
    """گرفتن نتیجه پاکسازی"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT status, result FROM purge_requests WHERE id=?", (req_id,))
        row = c.fetchone()
        conn.close()
        return row
    except Exception as e:
        print(f"[GET PURGE ERR] {e}")
        return None
'''
    with open(DB, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ queue_purge اضافه شد")

PYEOF

echo ""

if python3 -m py_compile database.py 2>&1; then
    echo "✅ database.py کامپایل OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

# ═══════════════════════════════════════════════════
# ۲. توی start.py — جایگزینی پاکسازی با queue_purge
# ═══════════════════════════════════════════════════
echo "─── ۲. اتصال به userbot توی start.py ───"

python3 << 'PYEOF'
ST = "modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# پیدا کردن تابع قدیمی پاکسازی که خودمون نوشتیم (توی persian_handler)
old_pattern_start = "# ★ هندلر پاکسازی (حذف 100 / شروع پاکسازی 50)"
idx = content.find(old_pattern_start)
if idx == -1:
    print("⚠️ الگو پیدا نشد — شاید قبلاً عوض شده")
else:
    # پیدا کردن انتهای بلاک (تا return)
    end_marker = "print(f\"[PURGE PERSIAN] {_deleted} پیام پاک شد توسط {_usr.id}\")\n            return"
    end_idx = content.find(end_marker, idx)
    if end_idx == -1:
        print("⚠️ انتهای بلاک پیدا نشد")
    else:
        end_idx += len(end_marker)
        
        # کد جدید — استفاده از userbot
        new_code = '''# ★ هندلر پاکسازی از طریق userbot (حذف 100 / شروع پاکسازی 50)
    import re as _re_p
    _persian_digits = {"۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9"}
    _text_for_purge = text
    for _pd, _ed in _persian_digits.items():
        _text_for_purge = _text_for_purge.replace(_pd, _ed)
    _purge_match = _re_p.match(r'^(حذف|شروع پاکسازی|پاکسازی)\\s+(\\d+)$', _text_for_purge.strip())
    if _purge_match:
        try:
            _count = int(_purge_match.group(2))
            if _count < 1 or _count > 1000:
                await msg.reply_text("❌ عدد باید بین ۱ تا ۱۰۰۰ باشه.")
                return
            _chat = update.effective_chat
            _usr = update.effective_user
            # چک ادمین
            try:
                _member = await _chat.get_member(_usr.id)
                if _member.status not in ("creator", "administrator"):
                    await msg.reply_text("❌ فقط ادمین‌ها می‌تونن پاکسازی کنن.")
                    return
            except Exception:
                pass
            # ثبت درخواست در دیتابیس
            try:
                from database import queue_purge, get_purge_result
                _msg_id = msg.message_id
                _req_id = queue_purge(_chat.id, _msg_id, _count, _usr.id)
                if not _req_id:
                    await msg.reply_text("❌ خطا در ثبت درخواست.")
                    return
                # حذف پیام دستور
                try:
                    await msg.delete()
                except Exception:
                    pass
                # پیام "در حال پاکسازی"
                _info = await context.bot.send_message(_chat.id, f"⏳ در حال پاک کردن {_count} پیام...")
                # انتظار برای نتیجه (حداکثر ۳۰ ثانیه)
                import asyncio as _aio_p
                _result_text = None
                for _wait in range(30):
                    await _aio_p.sleep(1)
                    _res = get_purge_result(_req_id)
                    if _res and _res[0] == 'done':
                        _result_text = _res[1]
                        break
                try:
                    await _info.delete()
                except Exception:
                    pass
                if _result_text:
                    _final = await context.bot.send_message(_chat.id, f"🗑️ {_result_text}")
                else:
                    _final = await context.bot.send_message(_chat.id, "⏳ در حال انجام...")
                async def _del_later_pp():
                    await _aio_p.sleep(5)
                    try:
                        await _final.delete()
                    except Exception:
                        pass
                _aio_p.create_task(_del_later_pp())
                print(f"[PURGE QUEUED] req={_req_id}, count={_count}")
                return
            except Exception as _e:
                print(f"[PURGE QUEUE ERR] {_e}")
                return
        except Exception as _e:
            print(f"[PURGE PERSIAN ERR] {_e}")
            return'''
        
        content = content[:idx] + new_code + content[end_idx:]
        with open(ST, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ start.py آپدیت شد")

PYEOF

echo ""

if python3 -m py_compile modules/start.py 2>&1; then
    echo "✅ start.py کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp modules/start.py.bak_* modules/start.py 2>/dev/null
    exit 1
fi
echo ""

# ═══════════════════════════════════════════════════
# ۳. راه‌اندازی userbot service در پس‌زمینه
# ═══════════════════════════════════════════════════
echo "─── ۳. راه‌اندازی userbot در پس‌زمینه ───"

# kill قدیمی
pkill -9 -f "userbot_service.py" 2>/dev/null
sleep 2

# nohup
nohup python3 -u userbot_service.py > ~/userbot_service.log 2>&1 &
sleep 8

echo "─── چک ───"
pgrep -af "userbot_service.py" || echo "❌ بالا نیومد"
echo ""
tail -n 10 ~/userbot_service.log

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ راه‌اندازی کامل شد"
echo ""
echo "🎯 حالا:"
echo "1. ربات اصلی رو ری‌استارت کن:"
echo "   pkill -9 -f 'python3 -u main.py'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "2. توی گروه بنویس: «حذف 50»"
echo ""
echo "3. باید ببینی:"
echo "   - پیام «⏳ در حال پاک کردن ۵۰ پیام...»"
echo "   - بعد چند ثانیه: «🗑️ X پیام پاک شد»"
echo "═══════════════════════════════════════════════════"
