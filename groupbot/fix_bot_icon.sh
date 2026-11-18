#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_boticon_$TS"
echo "✅ بک‌آپ: $ST.bak_boticon_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# حذف "ربات مدیریت گروه" از خط append
old1 = 'lines.append(f"🤖 ربات مدیریت گروه{_bot_uname_str} — ادمین")'
new1 = 'lines.append(f"🤖{_bot_uname_str} — ادمین")'

if old1 in content:
    content = content.replace(old1, new1)
    print("✅ 'ربات مدیریت گروه' حذف شد (1)")
else:
    print("⚠️ الگوی ۱ پیدا نشد")

# الگوی دوم (با فاصله)
old2 = 'lines.append(f"🤖 ربات مدیریت گروه{_bot_uname_str} — ادمین")'
if old2 in content:
    content = content.replace(old2, new1)
    print("✅ الگوی ۲ حذف شد")

# یه الگوی دیگه که تو کد قبلی بود
old3 = '_lines.append(f"🤖 ربات مدیریت گروه{_bot_uname_str} — ادمین")'
new3 = '_lines.append(f"🤖{_bot_uname_str} — ادمین")'
if old3 in content:
    content = content.replace(old3, new3)
    print("✅ الگوی ۳ حذف شد")

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_boticon_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "ربات مدیریت گروه" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
