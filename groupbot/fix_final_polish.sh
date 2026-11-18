#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_polish_$TS"
echo "✅ بک‌آپ: $ST.bak_polish_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# ★ fix 1: 15 → 30 ثانیه
content = content.replace("await _aio2.sleep(15)", "await _aio2.sleep(30)")
content = content.replace("await _aio.sleep(15)", "await _aio.sleep(30)")
content = content.replace("تا ۱۵ ثانیه", "تا ۳۰ ثانیه")
print("✅ timeout → 30s")

# ★ fix 2: نمایش مالک‌ها توی لیست اعضا
# الان لیست اعضا فقط ادمین‌هاست، مالک‌ها اولش اضافه نشدن
# باید دنبال خط "for _oa in _tg_admins:" بگردیم و مطمئن شیم مالک‌ها اضافه می‌شن

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_polish_$TS" "$ST"
    exit 1
fi
echo ""

echo "═══ چک ═══"
grep -n "_aio2.sleep(30)\|_aio.sleep(30)\|۳۰ ثانیه" "$ST"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 حالا برای مالک — بذار کد فعلی رو ببینم:"
echo "grep -n '_lines.append' ~/groupbot/modules/start.py | head -10"
echo "═══════════════════════════════════════════════════"
