#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══════════════════════════════════════════════════"
echo "🔍 کد pm_toggle"
echo "═══════════════════════════════════════════════════"
echo ""

LINE=$(grep -n 'if action.startswith("pm_toggle_")' "$ST" | head -1 | cut -d: -f1)
echo "خط pm_toggle: $LINE"
echo ""

sed -n "${LINE},$((LINE+25))p" "$ST" | cat -n
echo ""

echo "═══════════════════════════════════════════════════"
echo "🔍 کد PROMOTE_WAIT (توی reply.py یا admin.py)"
echo "═══════════════════════════════════════════════════"
echo ""

grep -n 'PROMOTE_WAIT\[' modules/reply.py modules/admin.py modules/start.py 2>/dev/null | head -20
echo ""

echo "─── پیدا کردن جایی که PROMOTE_WAIT پر می‌شه ───"
grep -n 'PROMOTE_WAIT\[user.id\]\|PROMOTE_WAIT\[uid\]\s*=' modules/*.py
echo ""

echo "═══════════════════════════════════════════════════"
