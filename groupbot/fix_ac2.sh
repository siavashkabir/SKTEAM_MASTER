#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_ac2_$TS"
echo "✅ بک‌آپ: $AC.bak_ac2_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# اگه تعریف شده، skip
if "ACCESS_CHANGED = {}" in content:
    print("⚠️ ACCESS_CHANGED از قبل تعریف شده")
    exit(0)

# پیدا کردن NL = chr(10)
if "NL = chr(10)" in content:
    content = content.replace(
        "NL = chr(10)",
        "NL = chr(10)\nACCESS_CHANGED = {}  # state موقت برای دکمه تایید\n",
        1
    )
    print("✅ ACCESS_CHANGED بعد از NL اضافه شد")
else:
    # اگه NL نبود، بعد از from config import OWNER_ID اضافه کن
    if "from config import OWNER_ID" in content:
        content = content.replace(
            "from config import OWNER_ID",
            "from config import OWNER_ID\n\nACCESS_CHANGED = {}  # state موقت برای دکمه تایید\n",
            1
        )
        print("✅ ACCESS_CHANGED بعد از import config اضافه شد")
    else:
        # آخرین راه: بعد از اولین import
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                continue
            # اولین خط غیر import
            lines.insert(i, 'ACCESS_CHANGED = {}  # state موقت برای دکمه تایید\n')
            break
        content = '\n'.join(lines)
        print("✅ ACCESS_CHANGED بعد از import ها اضافه شد")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_ac2_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک: ACCESS_CHANGED تعریف شده؟ ───"
grep -n "ACCESS_CHANGED = {}" "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
