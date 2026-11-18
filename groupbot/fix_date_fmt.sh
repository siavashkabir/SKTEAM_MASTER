#!/data/data/com.termux/files/usr/bin/bash

SUB=~/groupbot/modules/subscription.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$SUB" "$SUB.bak_datefmt_$TS"
echo "✅ بک‌آپ: $SUB.bak_datefmt_$TS"
echo ""

echo "─── خط DATE_FMT فعلی ───"
grep -n "DATE_FMT" "$SUB"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
SUB = "/data/data/com.termux/files/home/groupbot/modules/subscription.py"

with open(SUB, "r", encoding="utf-8") as f:
    content = f.read()

import re

# پیدا کردن خط DATE_FMT
for line in content.split('\n'):
    if 'DATE_FMT' in line and '=' in line and 'strptime' not in line and 'strftime' not in line:
        print(f"خط فعلی: {line}")

# جایگزینی DATE_FMT با مقدار درست
# الگو: DATE_FMT = ... (هر چی)
old_pattern = r"DATE_FMT\s*=\s*[^\n]+"
new_pattern = "DATE_FMT = '%Y-%m-%d %H:%M:%S'"

if re.search(old_pattern, content):
    content = re.sub(old_pattern, new_pattern, content, count=1)
    print(f"✅ DATE_FMT اصلاح شد به: {new_pattern}")
else:
    print("❌ DATE_FMT پیدا نشد")
    exit(1)

# چک نهایی
for line in content.split('\n'):
    if 'DATE_FMT' in line and '=' in line and 'strptime' not in line and 'strftime' not in line:
        print(f"خط بعد از fix: {line}")

with open(SUB, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$SUB" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$SUB.bak_datefmt_$TS" "$SUB"
    exit 1
fi
echo ""

echo "─── تست جدید ───"
python3 << 'PYEOF'
import importlib
import modules.subscription
importlib.reload(modules.subscription)
from modules.subscription import check_active, get_expire, DATE_FMT

print(f"DATE_FMT: {DATE_FMT}")
for chat_id in [-1004349813270, -100191141484]:
    print(f"chat {chat_id}: {check_active(chat_id)}")
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f ~/groupbot/.bot.lock; cd ~/groupbot && source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
