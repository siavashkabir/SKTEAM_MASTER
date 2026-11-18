#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "📺 لاگ زنده — Ctrl+C برای خروج"
echo "═══════════════════════════════════════════════════"
echo ""
echo "🎯 حالا توی تلگرام:"
echo "   1. «دسترسی» رو بزن"
echo "   2. دکمه «✅ تایید و بستن» رو بزن"
echo "   3. لاگ رو ببین"
echo ""

tail -f ~/groupbot_bot.log | grep --line-buffered -E "ACCESS|acc_|confirm|ERROR|Traceback|IndentationError"
