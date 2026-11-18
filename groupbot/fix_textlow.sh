#!/usr/bin/env bash

source venv/bin/activate

python3 << 'PYEOF'
RP = "modules/reply.py"

with open(RP, "r", encoding="utf-8") as f:
    content = f.read()

# جایگزینی
count = content.count("text_low.strip()")
if count > 0:
    content = content.replace("text_low.strip()", "t_low.strip()")
    print(f"✅ {count} تا text_low → t_low")

with open(RP, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile modules/reply.py 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

echo "─── ری‌استارت ربات ───"
pkill -9 -f 'python3 -u main.py'; sleep 3
rm -f .bot.lock
nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &
sleep 10

echo ""
echo "─── چک ───"
pgrep -af "python3 -u main.py"
echo ""
echo "─── لاگ ───"
tail -n 5 ~/groupbot_bot.log
