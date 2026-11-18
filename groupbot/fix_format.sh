#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_format_$TS"
echo "✅ بک‌آپ: $ST.bak_format_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# پیدا کردن text = توی پیکربندی (با هر شکل و indent)
import re

# الگو: text = ("✅ پیکربندی انجام شد!" ... تا بسته شدن
patterns = [
    # الگوی قدیمی
    r'text\s*=\s*\("✅ پیکربندی انجام شد!"[^)]*?\)',
    # الگو با متغیرهای دیگه
    r'text\s*=\s*\(".*?پیکربندی.*?"[^)]*?\)',
]

new_text = '''text = (
            "⚙️ پیکربندی گروه" + NL +
            "━━━━━━━━━━━━━━━" + NL +
            "👥 گروه: " + (chat.title or "?") + NL +
            "👑 مالکین: " + str(_owner_count) + NL +
            "🛡️ ادمین‌ها: " + str(_admin_count) + NL +
            NL +
            "📋 لیست اعضا:" + NL +
            details + NL +
            NL +
            "⏱️ " + now
        )'''

found = False
for pat in patterns:
    match = re.search(pat, content, re.DOTALL)
    if match:
        content = content.replace(match.group(0), new_text, 1)
        print(f"✅ الگو پیدا شد و جایگزین شد")
        found = True
        break

if not found:
    print("❌ الگو پیدا نشد")
    # دیاگ
    idx = content.find("پیکربندی انجام شد")
    if idx > 0:
        print("context:")
        print(content[idx-100:idx+500])
    exit(1)

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_format_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک ───"
grep -n "پیکربندی گروه" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
