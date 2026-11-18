#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_ownerlist_$TS"
echo "✅ بک‌آپ: $ST.bak_ownerlist_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط `lines = []` توی do_refresh (خط ~۱۵۶۸)
target = -1
for i, line in enumerate(lines):
    if 1560 <= i <= 1575 and line.strip() == "lines = []":
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

indent = lines[target][:len(lines[target]) - len(lines[target].lstrip())]

# اضافه کردن مالک‌ها قبل از ادمین‌ها
new_code = [
    "\n",
    indent + "# ★ اول مالک‌ها\n",
    indent + "for _oa in _tg_admins:\n",
    indent + '    if _oa.status != "creator":\n',
    indent + "        continue\n",
    indent + "    _oid = _oa.user.id\n",
    indent + "    _info = _members_info.get(_oid, {})\n",
    indent + '    _fname = _info.get("first_name") or _oa.user.first_name or "?"\n',
    indent + '    _uname = _info.get("username") or _oa.user.username\n',
    indent + '    _uname_str = f" (@{_uname})" if _uname else ""\n',
    indent + '    lines.append(f"👑 {_fname}{_uname_str} — مالک")\n',
]

lines = lines[:target + 1] + new_code + lines[target + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ مالک‌ها به لیست اضافه شدن")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_ownerlist_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n 'lines.append.*مالک\|for _oa in _tg_admins' "$ST" | head -5
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
