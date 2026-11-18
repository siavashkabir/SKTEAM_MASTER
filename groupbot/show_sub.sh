#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ check_active توی subscription.py"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── ۱. تابع check_active ───"
grep -n "def check_active" ~/groupbot/modules/subscription.py
LINE=$(grep -n "def check_active" ~/groupbot/modules/subscription.py | head -1 | cut -d: -f1)
echo "خط: $LINE"
echo ""
sed -n "${LINE},$((LINE+40))p" ~/groupbot/modules/subscription.py
echo ""

echo "─── ۲. تست مستقیم ───"
source venv/bin/activate
python3 << 'PYEOF'
from modules.subscription import check_active

for chat_id in [-1004349813270, -100191141484]:
    try:
        r = check_active(chat_id)
        print(f"chat {chat_id}: {r}")
    except Exception as e:
        print(f"chat {chat_id}: ERROR: {e}")
        import traceback
        traceback.print_exc()
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ پایان"
echo "═══════════════════════════════════════════════════"
