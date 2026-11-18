#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ acc_back و خط 309"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. خطوط دقیق acc_back (توی دکمه‌ها) ═══"
grep -n 'callback_data="acc_back' "$AC"
echo ""

echo "═══ ۲. خطوط دقیق acc_back (توی handler) ═══"
grep -n 'action == "acc_back"' "$AC"
echo ""

echo "═══ ۳. خط ۳۰۰ تا ۳۲۰ (اطراف خط 309) ═══"
sed -n '295,325p' "$AC" | cat -n
echo ""

echo "═══ ۴. توی build_access_menu — همه دکمه‌ها (خط 85-160) ═══"
sed -n '85,160p' "$AC" | grep -n "InlineKeyboardButton\|callback_data"
echo ""

echo "═══ ۵. توی build_access_menu — خطوط دکمه‌های بازگشت ═══"
sed -n '85,160p' "$AC" | grep -n "بازگشت"
echo ""

echo "═══ ۶. تعداد acc_back (توی دکمه‌ها) ═══"
grep -c "callback_data=\"acc_back" "$AC"
echo ""

echo "═══ ۷. توی build_access_menu — دکمه‌های بازگشت دقیقاً چطورن ═══"
grep -n 'InlineKeyboardButton("🔙' "$AC"
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DBG_CONFIRM.txt

echo ""
echo "✅ فایل: ~/DBG_CONFIRM.txt"
