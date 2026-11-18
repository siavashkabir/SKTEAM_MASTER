#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_msg_$TS"
echo "✅ بک‌آپ: $AC.bak_msg_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    content = f.read()

# جایگزینی متن‌ها
replacements = [
    ('"✅ تغییرات با موفقیت اعمال شد."', '"✅ دسترسی‌ها با موفقیت به‌روزرسانی شد."'),
    ('"✅ تغییرات اعمال شد."', '"✅ دسترسی‌ها با موفقیت به‌روزرسانی شد."'),
    ('"✅ تغییرات با موفقیت ذخیره شد."', '"✅ دسترسی‌ها با موفقیت به‌روزرسانی شد."'),
    ('"ℹ️ تغییری اعمال نشد."', '"ℹ️ هیچ تغییری ثبت نشد."'),
    ('"ℹ️ تغییر اعمال نشد."', '"ℹ️ هیچ تغییری ثبت نشد."'),
]

count = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"✅ «{old}» → «{new}»")

if count == 0:
    print("⚠️ هیچ متنی پیدا نشد — متن فعلی:") 
    import re
    for m in re.finditer(r'text="[^"]*[تت]غییر[^"]*"', content):
        print(f"  {m.group(0)}")
    for m in re.finditer(r'text="[^"]*[ا]عمال[^"]*"', content):
        print(f"  {m.group(0)}")
else:
    print(f"✅ {count} تا متن تغییر کرد")

with open(AC, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$AC.bak_msg_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── متن‌های جدید ───"
grep -n "دسترسی‌ها با موفقیت\|هیچ تغییری" "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
