#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_revert_$TS"
echo "✅ بک‌آپ: $ST.bak_revert_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    lines = f.readlines()

# فقط توی do_refresh (خط 1520-1650)، chat_id رو به chat.id برگردون
count = 0
for i in range(1520, min(1650, len(lines))):
    if 'chat_id' in lines[i] and 'chat.id' not in lines[i]:
        # جایگزین chat_id → chat.id
        lines[i] = lines[i].replace('chat_id', 'chat.id')
        count += 1
        print(f"✅ خط {i+1}: chat_id → chat.id")

with open(ST, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"✅ {count} خط اصلاح شد (فقط توی do_refresh)")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_revert_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک: chat.id توی do_refresh ═══"
sed -n '1535,1560p' "$ST" | grep -n "chat.id\|chat_id"
echo ""

echo "═══ چک: chat_id توی callback handler ═══"
sed -n '2235,2250p' "$ST" | grep -n "chat_id\|chat.id"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
