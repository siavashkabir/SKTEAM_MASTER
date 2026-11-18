#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_ac_$TS"
echo "✅ بک‌آپ: $AC.bak_ac_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# چک کن هست یا نه
if "ACCESS_CHANGED" in content:
    print("⚠️ ACCESS_CHANGED از قبل هست — skip")
    # فقط چک کن تعریف شده یا نه
    if "ACCESS_CHANGED = {}" in content:
        print("✅ تعریف شده")
    else:
        print("❌ تعریف نشده — باید اضافه کنم")
else:
    print("❌ ACCESS_CHANGED وجود نداره")

# اگه تعریف نشده، اضافه کن
if "ACCESS_CHANGED = {}" not in content:
    if "HL = chr(10)" in content:
        content = content.replace(
            "HL = chr(10)",
            "HL = chr(10)\nACCESS_CHANGED = {}  # (chat_id, target_id) -> bool",
            1
        )
        print("✅ ACCESS_CHANGED = {} اضافه شد")
    else:
        print("❌ HL = chr(10) پیدا نشد")
        exit(1)

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_ac_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک نهایی ───"
echo "ACCESS_CHANGED: $(grep -c 'ACCESS_CHANGED' "$AC")"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
