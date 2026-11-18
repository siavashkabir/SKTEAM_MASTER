#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "📺 لاگ کامل — Ctrl+C برای خروج"
echo "═══════════════════════════════════════════════════"
echo ""
echo "🎯 توی تلگرام این کارا رو بکن:"
echo ""
echo "  ۱. ربات رو ری‌استارت کن (قبل از لاگ)"
echo "  ۲. برو گروه"
echo "  ۳. یه پیام ریپلای روی کاربر بزن"
echo "  ۴. بنویس: افزودن مدیر"
echo "  ۵. تیک بزن (اولش)"
echo "  ۶. تیک دوم رو بزن"
echo "  ۷. تایید و بستن رو بزن"
echo ""
echo "بعد از اینا، لاگ رو کپی کن و بفرست."
echo ""
echo "═══════════════════════════════════════════════════"
echo ""

# همه چیز
tail -f ~/groupbot_bot.log | grep --line-buffered -E "PM_|pm_|PROMOTE|HANDLER DEBUG|CALLBACK|ERROR|Error|Traceback|set_admin_perm|add_admin|ADMIN"
