#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_rewrite_$TS"
echo "✅ بک‌آپ: $ST.bak_rewrite_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن "if action == \"menu_admin_perms\":"
start = -1
for i, line in enumerate(lines):
    if 'if action == "menu_admin_perms":' in line:
        start = i
        break

# پیدا کردن "if action == \"menu_deputy_perms\":"
end = -1
for i in range(start + 1, len(lines)):
    if 'if action == "menu_deputy_perms":' in lines[i]:
        end = i
        break

if start == -1 or end == -1:
    print(f"❌ پیدا نشد (start={start}, end={end})")
    exit(1)

print(f"✅ بازه: خط {start + 1} تا {end}")

# کد جدید — تمیز و کامل
new_block = '''if action == "menu_admin_perms":
    # [SECURITY FIX]
    try:
        from config import OWNER_ID
        from database import is_bot_admin
        _is_owner = (query.from_user.id == OWNER_ID)
        _is_sudo = False
        if not _is_owner:
            try:
                _is_sudo = is_bot_admin(query.from_user.id)
            except Exception:
                pass
        if not (_is_owner or _is_sudo):
            await query.answer("❌ شما دسترسی به این بخش را ندارید.", show_alert=True)
            return
    except Exception:
        return

    try:
        import sqlite3 as _sq
        from config import DATABASE_PATH as _DBP
        from database import get_group_admins
        import asyncio as _aio

        chat_id = int(parts[2]) if len(parts) > 2 else chat.id
        
        # ★ گرفتن ادمین‌ها از دیتابیس
        _db_admins = get_group_admins(chat_id)
        
        # ★ گرفتن مالکین و ادمین‌های تلگرام
        _tg_admins = await context.bot.get_chat_administrators(chat_id)
        _owner_ids = {a.user.id for a in _tg_admins if a.status == "creator"}
        _bot_id = context.bot.id
        
        # ★ اطلاعات اعضا از members
        _members_info = {}
        try:
            _conn = _sq.connect(_DBP)
            _cur = _conn.cursor()
            _cur.execute("SELECT user_id, first_name, username FROM members WHERE chat_id=?", (chat_id,))
            for _row in _cur.fetchall():
                _members_info[_row[0]] = {"first_name": _row[1], "username": _row[2]}
            _conn.close()
        except Exception as _e:
            print(f"[CFG MEMBERS ERR] {_e}")
        
        # ★ ساخت لیست
        _lines = []
        
        # مالکین
        for _oa in _tg_admins:
            if _oa.status != "creator":
                continue
            _oid = _oa.user.id
            _info = _members_info.get(_oid, {})
            _fname = _info.get("first_name") or _oa.user.first_name or "?"
            _uname = _info.get("username") or _oa.user.username
            _uname_str = f" (@{_uname})" if _uname else ""
            _lines.append(f"👑 {_fname}{_uname_str} — مالک")
        
        # ربات خودش
        _bot_uname = context.bot.username
        _bot_uname_str = f" (@{_bot_uname})" if _bot_uname else ""
        _lines.append(f"🤖 ربات مدیریت گروه{_bot_uname_str} — ادمین")
        
        # بقیه ادمین‌ها
        for _a in _db_admins:
            _uid = _a.get("user_id")
            if _uid in _owner_ids or _uid == _bot_id:
                continue
            _info = _members_info.get(_uid, {})
            _fname = _info.get("first_name") or _a.get("name") or "?"
            _uname = _info.get("username")
            _uname_str = f" (@{_uname})" if _uname else ""
            _lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")
        
        _owner_count = len(_owner_ids)
        _admin_count = sum(1 for _l in _lines if "🛡️" in _l or "🤖" in _l)
        _details = "\\n".join(_lines) if _lines else "─ لیست خالیه ─"
        
        from datetime import datetime as _dt
        _now = _dt.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ★ متن فرمت‌شده
        _text = (
            "⚙️ پیکربندی گروه\\n" +
            "━━━━━━━━━━━━━━━\\n" +
            f"👥 گروه: {chat.title or '?'}\\n" +
            f"👑 مالکین: {_owner_count}\\n" +
            f"🛡️ ادمین‌ها: {_admin_count}\\n" +
            "\\n" +
            "📋 لیست اعضا:\\n" +
            _details + "\\n" +
            "\\n" +
            f"⏱️ {_now}"
        )
        
        # ★ ارسال پیام
        _msg = await query.message.reply_text(_text)
        
        # ★ بستن منو
        try:
            await query.message.delete()
        except Exception:
            pass
        
        # ★ پاک کردن خودکار بعد از ۱۵ ثانیه
        async def _auto_close():
            await _aio.sleep(15)
            try:
                await _msg.delete()
            except Exception:
                pass
        _aio.create_task(_auto_close())
        
    except Exception as e:
        print(f"[ADMIN PERMS ERR] {e}")
        import traceback
        traceback.print_exc()
    return

'''

new_lines = lines[:start] + [new_block] + lines[end:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ جایگزین شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_rewrite_$TS" "$ST"
    python3 -m py_compile "$ST" 2>&1 | head -5
    exit 1
fi
echo ""

echo "─── چک ───"
grep -n "پیکربندی گروه\|_auto_close" "$ST" | head -5
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
