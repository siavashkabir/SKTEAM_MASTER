#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_linebots_$TS"
echo "✅ بک‌آپ: $ST.bak_linebots_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# ★ fix 1: خط فاصله ۲۰ تا رو ۱۶ تا کن
old_line = '"━━━━━━━━━━━━━━━━━━━━"'
new_line = '"━━━━━━━━━━━━━━"'

count = content.count(old_line)
if count > 0:
    content = content.replace(old_line, new_line)
    print(f"✅ خط فاصله کوتاه شد ({count} جا)")

# ★ fix 2: اضافه کردن تعداد ربات‌ها زیر ادمین‌ها
old_count = '''"└ 🛡️ ادمین‌ها: " + str(sum(1 for _l in lines if "🛡️" in _l or "🤖" in _l)) + NL'''

new_count = '''"├ 🛡️ ادمین‌ها: " + str(sum(1 for _l in lines if "🛡️" in _l)) + NL +
            "└ 🤖 ربات‌ها: " + str(sum(1 for _l in lines if "🤖" in _l)) + NL'''

if old_count in content:
    content = content.replace(old_count, new_count, 1)
    print("✅ تعداد ربات‌ها اضافه شد")
else:
    print("⚠️ الگوی ادمین‌ها پیدا نشد")
    idx = content.find('ادمین‌ها: "')
    if idx > 0:
        print("context:")
        print(content[idx-100:idx+200])

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_linebots_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "ربات‌ها:" "$ST"
grep -c '"━━━━━━━━━━━━━━"' "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
