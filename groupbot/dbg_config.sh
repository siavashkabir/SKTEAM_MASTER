#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

{
echo "═══ ۱. line 'if action == menu_admin_perms' ═══"
grep -n 'if action == "menu_admin_perms"' "$ST"
echo ""

echo "═══ ۲. line 'پیکربندی انجام شد' (کد قدیمی) ═══"
grep -n "پیکربندی انجام شد" "$ST"
echo ""

echo "═══ ۳. line 'پیکربندی گروه' (کد جدید من) ═══"
grep -n "پیکربندی گروه" "$ST"
echo ""

echo "═══ ۴. line '_auto_close' ═══"
grep -n "_auto_close" "$ST"
echo ""

echo "═══ ۵. خط ۲۱۴۰ تا ۲۱۸۰ با شماره ═══"
sed -n '2140,2180p' "$ST" | cat -n
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DBG_CONFIG.txt

echo ""
echo "✅ فایل: ~/DBG_CONFIG.txt"
