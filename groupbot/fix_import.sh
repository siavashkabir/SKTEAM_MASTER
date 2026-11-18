#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$AC" "$AC.bak_imp_$TS"
echo "✅ بک‌آپ: $AC.bak_imp_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
AC = "/data/data/com.termux/files/home/groupbot/modules/access.py"

with open(AC, "r", encoding="utf-8") as f:
    lines = f.readlines()

# پیدا کردن خط is_bot_admin
for i, line in enumerate(lines):
    if "is_bot_admin, is_group_owner" in line and "is_admin" not in line:
        # اضافه کردن is_admin به خط
        lines[i] = line.replace(
            "is_bot_admin, is_group_owner",
            "is_bot_admin, is_admin, is_group_owner"
        )
        print(f"✅ خط {i+1}: is_admin اضافه شد")
        break

with open(AC, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ ذخیره شد")
PYEOF

echo ""

# چک کامپایل
if python3 -m py_compile "$AC" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا:"
    python3 -m py_compile "$AC" 2>&1 | head -5
    echo ""
    echo "rollback..."
    cp "$AC.bak_imp_$TS" "$AC"
    exit 1
fi
echo ""

echo "─── خط ۱ تا ۱۰ ───"
sed -n '1,10p' "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
