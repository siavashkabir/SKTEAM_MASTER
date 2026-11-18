#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══════════════════════════════════════════════════"
echo "🔍 محل pm_confirm"
echo "═══════════════════════════════════════════════════"
echo ""

LINE=$(grep -n 'if action == "pm_confirm":' "$ST" | head -1 | cut -d: -f1)
echo "شروع pm_confirm: خط $LINE"
echo ""

echo "─── خط $LINE تا $((LINE+50)) ───"
sed -n "${LINE},$((LINE+50))p" "$ST" | cat -n
echo ""

echo "═══════════════════════════════════════════════════"
