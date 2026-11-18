#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py

echo "─── خطوط delete ───"
grep -n "query.message.delete()" "$AC"
echo ""

echo "─── محتوای اطراف هر delete (۱۰ خط قبل) ───"
for LINE in $(grep -n "query.message.delete()" "$AC" | cut -d: -f1); do
    echo "════ خط $LINE ════"
    sed -n "$((LINE-10)),$((LINE+3))p" "$AC"
    echo ""
done
