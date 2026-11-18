#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "📄 نمایش کامل access.py"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. access_handler — خط 159 تا 238 ═══"
sed -n '159,238p' modules/access.py
echo ""

echo "═══ ۲. access_cb_handler — خط 238 تا 335 ═══"
sed -n '238,335p' modules/access.py
echo ""

echo "═══ ۳. owner_guide.py — guide_access — خط 400 تا 430 ═══"
sed -n '400,430p' modules/owner_guide.py
echo ""

echo "═══ ۴. start.py — callback pattern (خط 6890 تا 6895) ═══"
sed -n '6890,6895p' modules/start.py
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/SHOW_ACCESS.txt

echo ""
echo "✅ فایل: ~/SHOW_ACCESS.txt"
echo "📏 خطوط: $(wc -l < ~/SHOW_ACCESS.txt)"
