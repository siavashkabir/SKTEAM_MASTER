#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══ کد 'پیکربندی انجام شد!' (قدیمی) ═══"
grep -n "پیکربندی انجام شد" "$ST"
echo ""

echo "═══ کد 'پیکربندی گروه' (جدید) ═══"
grep -n "پیکربندی گروه" "$ST"
echo ""

echo "═══ خط ۲۱۷۴ تا ۲۲۵۰ (کد action) ═══"
sed -n '2174,2250p' "$ST" | cat -n | head -80
echo ""

