#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_chatid_$TS"
echo "✅ بک‌آپ: $ST.bak_chatid_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# ★ پیدا کردن chat.id و جایگزینی با chat_id
replacements = [
    # get_chat_administrators(chat.id) → chat_id
    ("await context.bot.get_chat_administrators(chat.id)", "await context.bot.get_chat_administrators(chat_id)"),
    # get_group_admins(chat.id) → chat_id
    ("get_group_admins(chat.id)", "get_group_admins(chat_id)"),
    # members: WHERE chat_id=? (, (chat.id,)) → chat_id
    ("FROM members WHERE chat_id=?", "FROM members WHERE chat_id=?"),
    ("(chat.id,)", "(chat_id,)"),
    # (chat.title or "?") → گروه فعلی
]

count = 0
for old, new in replacements:
    if old in content and old != new:
        c = content.count(old)
        content = content.replace(old, new)
        count += c
        print(f"✅ '{old}' → '{new}' ({c} جا)")

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ {count} جایگزینی")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_chatid_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
LINE=$(grep -n "get_chat_administrators" "$ST" | grep -v "^.*#" | head -3)
echo "$LINE"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
