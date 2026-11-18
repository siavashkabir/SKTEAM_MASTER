#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_ownbot_$TS"
echo "✅ بک‌آپ: $ST.bak_ownbot_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط `lines = []` توی بلاک پیکربندی
target_start = -1
for i, line in enumerate(lines):
    if line.strip() == "lines = []" and 1530 < i < 1560:
        # چک کن قبلی‌اش `_bot_id` باشه
        if any('_bot_id' in lines[j] for j in range(max(0, i-5), i)):
            target_start = i
            break

if target_start == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط شروع lines: {target_start + 1}")

# پیدا کردن `details = NL.join` بعدش
target_end = -1
for i in range(target_start, target_start + 40):
    if 'details = NL.join' in lines[i]:
        target_end = i
        break

if target_end == -1:
    print("❌ انتها پیدا نشد")
    exit(1)

print(f"✅ خط پایان details: {target_end + 1}")

indent = lines[target_start][:len(lines[target_start]) - len(lines[target_start].lstrip())]

# کد جدید
new_block = [
    indent + "lines = []\n",
    "\n",
    indent + "# ★ مالکین گروه (از تلگرام)\n",
    indent + "for _ta in _tg_admins:\n",
    indent + '    if _ta.status != "creator":\n',
    indent + "        continue\n",
    indent + "    _info = _members_info.get(_ta.user.id, {})\n",
    indent + '    _fname = _info.get("first_name") or _ta.user.first_name or "?"\n',
    indent + '    _uname = _info.get("username") or _ta.user.username\n',
    indent + '    _uname_str = f" (@{_uname})" if _uname else ""\n',
    indent + '    lines.append(f"👑 {_fname}{_uname_str} — مالک")\n',
    "\n",
    indent + "# ★ ربات مدیریت گروه\n",
    indent + '_bot_uname = context.bot.username\n',
    indent + '_bot_uname_str = f" (@{_bot_uname})" if _bot_uname else ""\n',
    indent + 'lines.append(f"🤖 ربات مدیریت گروه{_bot_uname_str} — ادمین")\n',
    "\n",
    indent + "# ★ بقیه ادمین‌ها (از دیتابیس)\n",
    indent + "for _a in _db_admins:\n",
    indent + '    _uid = _a.get("user_id")\n',
    indent + "    if _uid in _owner_ids or _uid == _bot_id:\n",
    indent + "        continue\n",
    indent + '    _info = _members_info.get(_uid, {})\n',
    indent + '    _fname = _info.get("first_name") or _a.get("name") or "?"\n',
    indent + '    _uname = _info.get("username")\n',
    indent + '    _uname_str = f" (@{_uname})" if _uname else ""\n',
    indent + '    lines.append(f"🛡️ {_fname}{_uname_str} — ادمین")\n',
    "\n",
    indent + "_owner_count = len(_owner_ids)\n",
    indent + "if _owner_count == 0:\n",
    indent + "    _owner_count = sum(1 for _l in lines if '👑' in _l)\n",
    indent + "_admin_count = sum(1 for _l in lines if '🛡️' in _l or '🤖' in _l)\n",
    indent + 'details = NL.join(lines) if lines else "─ هیچ ادمینی ثبت نشده ─"\n',
]

new_lines = lines[:target_start] + new_block + lines[target_end + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ جایگزین شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_ownbot_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک ───"
grep -n "ربات مدیریت گروه\|_admin_count = sum" "$ST" | head -5
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
