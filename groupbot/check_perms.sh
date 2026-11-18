#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py

{
echo "═══ VIP_PERMS ═══"
grep -A 10 "^VIP_PERMS" "$AC" | head -12
echo ""

echo "═══ ADMIN_PERMS ═══"
grep -A 15 "^ADMIN_PERMS" "$AC" | head -18
echo ""

echo "═══ DEPUTY_PERMS ═══"
grep -A 25 "^DEPUTY_PERMS" "$AC" | head -28
echo ""

echo "═══ دنبال VIP_PERMS با regex بگرد ═══"
grep -n "VIP_PERMS" "$AC" | head -5
echo ""

echo "═══ دنبال ADMIN_PERMS ═══"
grep -n "ADMIN_PERMS" "$AC" | head -5
echo ""

echo "═══ دنبال DEPUTY_PERMS ═══"
grep -n "DEPUTY_PERMS" "$AC" | head -5
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/CHECK_PERMS.txt

echo ""
echo "✅ فایل: ~/CHECK_PERMS.txt"
