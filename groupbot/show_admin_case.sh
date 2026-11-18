#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py

echo "═══════════════════════════════════════════════════"
echo "🔍 کد فعلی admin case توی build_access_menu"
echo "═══════════════════════════════════════════════════"
echo ""

# پیدا کردن build_access_menu
START=$(grep -n "def build_access_menu" "$AC" | head -1 | cut -d: -f1)
END=$(grep -n "^def \|^async def " "$AC" | awk -F: -v s=$START '$1 > s {print $1; exit}')
echo "build_access_menu: خط $START تا $END"
echo ""

sed -n "${START},${END}p" "$AC" | cat -n
echo ""

echo "═══════════════════════════════════════════════════"
