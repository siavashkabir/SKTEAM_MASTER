#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py

{
echo "═══════════════════════════════════════════════════"
echo "🔍 چک handler فعلی"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── ACCESS_CHANGED کجاها هست؟ ───"
grep -n "ACCESS_CHANGED\|access_changed" "$AC"
echo ""

echo "─── خط ۲۵۵ تا ۳۱۰ ───"
sed -n '255,310p' "$AC" | cat -n
echo ""

echo "─── خطوط toggle ───"
grep -n "toggle_deputy_perm\|toggle_user_perm" "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/CHECK_H.txt

echo ""
echo "✅ فایل: ~/CHECK_H.txt"
