#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══ خطای اخیر ═══"
tail -n 30 ~/groupbot_bot.log | grep -A 10 "chat_id" | head -30
echo ""

echo "═══ chat_id کجاها تعریف شده ═══"
grep -n "chat_id = \|chat_id=" "$ST" | head -20
echo ""

echo "═══ chat_id توی do_refresh ═══"
sed -n '1520,1620p' "$ST" | grep -n "chat_id" | head -20
echo ""

echo "═══ خط ۱۵۳۰ تا ۱۵۶۰ ═══"
sed -n '1530,1560p' "$ST" | cat -n
echo ""

