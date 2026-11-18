#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_indent_$TS"
echo "✅ بک‌آپ: $ST.bak_indent_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن `if action == "menu_admin_perms":`
start = -1
for i, line in enumerate(lines):
    if 'if action == "menu_admin_perms":' in line:
        start = i
        break

end = -1
for i in range(start + 1, len(lines)):
    if 'if action == "menu_deputy_perms":' in lines[i]:
        end = i
        break

if start == -1 or end == -1:
    print(f"❌ پیدا نشد")
    exit(1)

print(f"✅ خط {start + 1} تا {end}")

# indent = 4 فاصله (از خود خط)
base = lines[start][:len(lines[start]) - len(lines[start].lstrip())]
i1 = base + "    "  # indent سطح ۱
i2 = base + "        "  # سطح ۲
i3 = base + "            "  # سطح ۳
i4 = base + "                "

# کد جدید با indent درست
new_block = f'''{base}if action == "menu_admin_perms":
{i1}# [SECURITY FIX]
{i1}try:
{i2}from config import OWNER_ID
{i2}from database import is_bot_admin
{i2}_is_owner = (query.from_user.id == OWNER_ID)
{i2}_is_sudo = False
{i2}if not _is_owner:
{i3}try:
{i4}_is_sudo = is_bot_admin(query.from_user.id)
{i3}except Exception:
{i4}pass
{i2}if not (_is_owner or _is_sudo):
{i3}await query.answer("❌ شما دسترسی به این بخش را ندارید.", show_alert=True)
{i3}return
{i1}except Exception:
{i2}return

{i1}try:
{i2}import sqlite3 as _sq
{i2}from config import DATABASE_PATH as _DBP
{i2}from database import get_group_admins
{i2}import asyncio as _aio
{i2}from datetime import datetime as _dt

{i2}chat_id = int(parts[2]) if len(parts) > 2 else chat.id
{i2}_db_admins = get_group_admins(chat_id)
{i2}_tg_admins = await context.bot.get_chat_administrators(chat_id)
{i2}_owner_ids = {{a.user.id for a in _tg_admins if a.status == "creator"}}
{i2}_bot_id = context.bot.id

{i2}_members_info = {{}}
{i2}try:
{i3}_conn = _sq.connect(_DBP)
{i3}_cur = _conn.cursor()
{i3}_cur.execute("SELECT user_id, first_name, username FROM members WHERE chat_id=?", (chat_id,))
{i3}for _row in _cur.fetchall():
{i4}_members_info[_row[0]] = {{"first_name": _row[1], "username": _row[2]}}
{i3}_conn.close()
{i2}except Exception as _e:
{i3}print(f"[CFG MEMBERS ERR] {{_e}}")

{i2}_lines = []

{i2}for _oa in _tg_admins:
{i3}if _oa.status != "creator":
{i4}continue
{i3}_oid = _oa.user.id
{i3}_info = _members_info.get(_oid, {{}})
{i3}_fname = _info.get("first_name") or _oa.user.first_name or "?"
{i3}_uname = _info.get("username") or _oa.user.username
{i3}_uname_str = f" (@{{_uname}})" if _uname else ""
{i3}_lines.append(f"👑 {{_fname}}{{_uname_str}} — مالک")

{i2}_bot_uname = context.bot.username
{i2}_bot_uname_str = f" (@{{_bot_uname}})" if _bot_uname else ""
{i2}_lines.append(f"🤖 ربات مدیریت گروه{{_bot_uname_str}} — ادمین")

{i2}for _a in _db_admins:
{i3}_uid = _a.get("user_id")
{i3}if _uid in _owner_ids or _uid == _bot_id:
{i4}continue
{i3}_info = _members_info.get(_uid, {{}})
{i3}_fname = _info.get("first_name") or _a.get("name") or "?"
{i3}_uname = _info.get("username")
{i3}_uname_str = f" (@{{_uname}})" if _uname else ""
{i3}_lines.append(f"🛡️ {{_fname}}{{_uname_str}} — ادمین")

{i2}_owner_count = len(_owner_ids)
{i2}_admin_count = sum(1 for _l in _lines if "🛡️" in _l or "🤖" in _l)
{i2}_details = "\\n".join(_lines) if _lines else "─ لیست خالیه ─"
{i2}_now = _dt.now().strftime("%Y-%m-%d %H:%M:%S")

{i2}_text = (
{i3}"⚙️ پیکربندی گروه\\n" +
{i3}"━━━━━━━━━━━━━━━\\n" +
{i3}f"👥 گروه: {{chat.title or '?'}}\\n" +
{i3}f"👑 مالکین: {{_owner_count}}\\n" +
{i3}f"🛡️ ادمین‌ها: {{_admin_count}}\\n" +
{i3}"\\n" +
{i3}"📋 لیست اعضا:\\n" +
{i3}_details + "\\n" +
{i3}"\\n" +
{i3}f"⏱️ {{_now}}"
{i2})

{i2}_msg = await query.message.reply_text(_text)

{i2}try:
{i3}await query.message.delete()
{i2}except Exception:
{i3}pass

{i2}async def _auto_close():
{i3}await _aio.sleep(15)
{i3}try:
{i4}await _msg.delete()
{i3}except Exception:
{i4}pass
{i2}_aio.create_task(_auto_close())

{i1}except Exception as e:
{i2}print(f"[ADMIN PERMS ERR] {{e}}")
{i2}import traceback
{i2}traceback.print_exc()
{i1}return

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
    cp "$ST.bak_indent_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
