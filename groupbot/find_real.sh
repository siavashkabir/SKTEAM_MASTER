#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

{
echo "═══════════════════════════════════════════════════"
echo "🔍 نقطه دقیق pm_toggle و pm_confirm"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. محل PROMOTE_WAIT — کجا ذخیره/خونده می‌شه ═══"
grep -n "PROMOTE_WAIT" "$ST"
echo ""

echo "═══ ۲. خط ۴۰۵۳ تا ۴۱۰۰ (pm_toggle) ═══"
sed -n '4053,4100p' "$ST" | cat -n
echo ""

echo "═══ ۳. خط ۴۱۵۵ تا ۴۱۷۰ (PROMOTE_WAIT pop) ═══"
grep -n "del PROMOTE_WAIT\|PROMOTE_WAIT.pop\|PROMOTE_WAIT\[uid\]" "$ST"
echo ""

echo "═══ ۴. import PROMOTE_WAIT ═══"
grep -n "import PROMOTE_WAIT\|from.*import.*PROMOTE" "$ST"
echo ""

echo "═══ ۵. admin.py — PROMOTE_WAIT چطور استفاده می‌شه ═══"
grep -n "PROMOTE_WAIT" modules/admin.py
echo ""

echo "═══ ۶. admin.py — خط ۱۰۵ تا ۱۳۰ ═══"
sed -n '105,130p' modules/admin.py | cat -n
echo ""

echo "═══ ۷. shared_state.py ═══"
cat modules/shared_state.py
echo ""

echo "═══ ۸. بررسی: چند جا PROMOTE_WAIT = {} تعریف شده؟ ═══"
grep -rn "PROMOTE_WAIT\s*=\s*{}" modules/*.py
echo ""

echo "═══ ۹. بررسی: چند جا PROMOTE_WAIT import شده؟ ═══"
grep -rn "import.*PROMOTE_WAIT\|PROMOTE_WAIT," modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۱۰. توی start.py — کد کامل pm_toggle (خط ۴۰۵۳ تا ۴۱۱۰) ═══"
sed -n '4053,4110p' "$ST" | cat -n
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/FIND_REAL.txt

echo ""
echo "✅ فایل: ~/FIND_REAL.txt"
echo "📏 خطوط: $(wc -l < ~/FIND_REAL.txt)"
