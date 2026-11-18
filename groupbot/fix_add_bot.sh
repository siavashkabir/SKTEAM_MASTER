#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_addbot_$TS"
echo "✅ بک‌آپ: $ST.bak_addbot_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط `_admin_count = sum(1 for _l in lines if ...)`
target = -1
for i, line in enumerate(lines):
    if '_admin_count = sum(1 for _l in lines if "🛡️" in _l or "🤖" in _l)' in line:
        target = i
        break

if target == -1:
    print("❌ پیدا نشد")
    exit(1)

print(f"✅ خط {target + 1}")

indent = lines[target][:len(lines[target]) - len(lines[target].lstrip())]

# اضافه کردن append ربات قبل از _admin_count
new_code = [
    "\n",
    indent + "# ★ اضافه کردن ربات خودش\n",
    indent + "_bot_uname = context.bot.username\n",
    indent + '_bot_uname_str = f" (@{_bot_uname})" if _bot_uname else ""\n',
    indent + 'lines.append(f"🤖{_bot_uname_str} — ادمین")\n',
    "\n",
]

new_lines = lines[:target] + new_code + lines[target:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("✅ ربات به لیست اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_addbot_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "_bot_uname_str\|lines.append.*🤖" "$ST" | head -5
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
