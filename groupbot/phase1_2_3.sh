#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_style_$TS"
echo "✅ بک‌آپ: $AC.bak_style_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# تغییر نشانگرها
old1 = 'mark = "[X]" if en else "[ ]"'
new1 = 'mark = "✅" if en else "❌"'

count = content.count(old1)
if count > 0:
    content = content.replace(old1, new1)
    print(f"✅ نشانگرها عوض شد ({count} جا)")

# حذف جداکننده «───────» (اگه هست)
content = content.replace(
    'keyboard.append([InlineKeyboardButton("───────────────", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])\n    ',
    ''
)
content = content.replace(
    'keyboard.append([InlineKeyboardButton("───────────────", callback_data="acc_noop:" + str(uid) + ":" + str(chat_id))])',
    ''
)

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_style_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── چک: mark ───"
grep -n 'mark = ' "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
