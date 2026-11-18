#!/data/data/com.termux/files/usr/bin/bash

MW=modules/middleware.py

echo "═══════════════════════════════════════════════════"
echo "🔍 چک کد فعلی middleware"
echo "═══════════════════════════════════════════════════"
echo ""

START=$(grep -n "async def check_group_active_message" "$MW" | head -1 | cut -d: -f1)
END=$(grep -n "^async def \|^def " "$MW" | awk -F: -v s=$START '$1 > s {print $1; exit}')

echo "تابع check_group_active_message خط $START تا $END"
echo ""
sed -n "${START},${END}p" "$MW"
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ پایان"
