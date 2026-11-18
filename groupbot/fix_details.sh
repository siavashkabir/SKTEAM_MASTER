#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_details_$TS"
echo "✅ بک‌آپ: $ST.bak_details_$TS"

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

# اضافه کردن `details = NL.join(lines)` بعد از _admin_count
new_lines = [
    indent + "# ★ ساخت details\n",
    indent + "details = NL.join(lines) if lines else \"─ هیچ ادمینی ثبت نشده ─\"\n",
]

lines = lines[:target + 1] + new_lines + lines[target + 1:]

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ details اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_details_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
LINE=$(grep -n "details = NL.join" "$ST" | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "$((LINE-5)),$((LINE+3))p" "$ST"
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
