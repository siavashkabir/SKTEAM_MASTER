#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_names_$TS"
echo "✅ بک‌آپ: $ST.bak_names_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن `_admin_count = len(_db_admins) - _owner_count`
target = -1
for i, line in enumerate(lines):
    if '_admin_count = len(_db_admins) - _owner_count' in line:
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

# indent
indent = lines[target][:len(lines[target]) - len(lines[target].lstrip())]

# کد جدید — استفاده از members برای username
new_lines = [
    indent + "# ★ خوندن username از members\n",
    indent + "import sqlite3\n",
    indent + "from config import DATABASE_PATH\n",
    indent + "_members_info = {}\n",
    indent + "try:\n",
    indent + "    _conn = sqlite3.connect(DATABASE_PATH)\n",
    indent + "    _cur = _conn.cursor()\n",
    indent + '    _cur.execute("SELECT user_id, first_name, username FROM members WHERE chat_id=?", (chat.id,))\n',
    indent + "    for _row in _cur.fetchall():\n",
    indent + "        _members_info[_row[0]] = {\"first_name\": _row[1], \"username\": _row[2]}\n",
    indent + "    _conn.close()\n",
    indent + "except Exception as _e:\n",
    indent + '    print(f"[CFG MEMBERS ERR] {_e}")\n',
    "\n",
    indent + "lines = []\n",
    indent + "for _a in _db_admins:\n",
    indent + '    _uid = _a.get("user_id")\n',
    indent + '    _name = _a.get("name") or "?"\n',
    indent + '    _info = _members_info.get(_uid, {})\n',
    indent + '    _fname = _info.get("first_name") or _name\n',
    indent + '    _uname = _info.get("username")\n',
    indent + '    _uname_str = f" (@{_uname})" if _uname else ""\n',
    indent + '    _role = "👑 مالک" if _uid in _owner_ids else "🛡️ ادمین"\n',
    indent + '    lines.append(f"• {_fname}{_uname_str} — {_role}")\n',
    "\n",
    indent + "_owner_count = len(_owner_ids)\n",
    indent + "_admin_count = len(_db_admins) - _owner_count\n",
    indent + 'details = NL.join(lines) if lines else "─ هیچ ادمینی ثبت نشده ─"\n',
]

# حذف خطوط قدیمی تا _admin_count رو حذف کنه
# پیدا کردن انتهای بلاک فعلی
end = target
for j in range(target, target + 20):
    if 'details = NL.join' in lines[j]:
        end = j
        break

# جایگزینی خطوط از start (یعنی جایی که lines = [] شروع شده) تا end
# بذار از target - 20 شروع کنم و دنبال "lines = []" بگردم
start_replace = target
for j in range(target - 25, target):
    if j >= 0 and 'lines = []' in lines[j]:
        start_replace = j
        break

print(f"✅ بازه جایگزینی: خط {start_replace + 1} تا {end + 1}")

new_lines_full = lines[:start_replace] + new_lines + lines[end + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines_full)

print("✅ جایگزین شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_names_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک: خطوط جدید ═══"
LINE=$(grep -n "_members_info" "$ST" | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+20))p" "$ST"
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
