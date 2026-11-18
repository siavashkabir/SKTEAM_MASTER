#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_line1602_$TS"
echo "✅ بک‌آپ: $ST.bak_line1602_$TS"

source venv/bin/activate

python3 << 'PYEOF'
import re

ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# الگو: text = ("✅ پیکربندی انجام شد!" ... تا آخر بلوک )
# الگو‌های چندخطی — ما همه‌شون رو می‌گیریم

old_patterns = [
    # line 1602 - قدیمی
    r'text\s*=\s*\("✅ پیکربندی انجام شد!"[^)]*?"📋 لیست ادمین‌ها:"\s*\+\s*NL\s*\+\s*details\)',
    # الگوی احتمالی دیگه
    r'text\s*=\s*\("✅ پیکربندی انجام شد!"[^)]*?\+\s*details\)',
]

new_text = '''text = (
            "⚙️ پیکربندی گروه" + NL +
            "━━━━━━━━━━━━━━━" + NL +
            "👥 گروه: " + (chat.title or "?") + NL +
            "👑 مالکین: " + str(len(_owner_ids)) + NL +
            "🛡️ ادمین‌ها: " + str(len(_db_admins)) + NL +
            NL +
            "📋 لیست اعضا:" + NL +
            details + NL +
            NL +
            "🕐 " + now'''

count = 0
for pat in old_patterns:
    matches = re.findall(pat, content, re.DOTALL)
    if matches:
        for m in matches:
            content = content.replace(m, new_text, 1)
            count += 1
        print(f"✅ {len(matches)} جایگزینی با الگو")

if count == 0:
    print("❌ الگو پیدا نشد — دیاگ:")
    # پیدا کردن خط ۱۶۰۰ تا ۱۶۱۰
    lines = content.split('\n')
    for i, line in enumerate(lines[1595:1615], start=1596):
        print(f"  {i}: {line}")
    exit(1)

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ {count} جایگزینی انجام شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_line1602_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "پیکربندی انجام شد\|پیکربندی گروه" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
