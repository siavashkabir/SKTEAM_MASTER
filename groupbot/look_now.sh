#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py

echo "═══════════════════════════════════════════════════"
echo "🔍 وضعیت فعلی access_cb_handler"
echo "═══════════════════════════════════════════════════"
echo ""

START=$(grep -n "async def access_cb_handler" "$AC" | head -1 | cut -d: -f1)
echo "شروع: خط $START"
echo ""

echo "─── خط ${START} تا $((START+120)) ───"
sed -n "${START},$((START+120))p" "$AC" | cat -n
echo ""

echo "═══════════════════════════════════════════════════"
echo "🔍 خطوط دقیق delete() و if های بی‌بلاک"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── delete() ها ───"
grep -n "query.message.delete()" "$AC"
echo ""

echo "─── خط 258 تا 268 (اطراف خط 261 که خطا داد) ───"
sed -n '258,268p' "$AC" | cat -n
echo ""

echo "═══════════════════════════════════════════════════"
