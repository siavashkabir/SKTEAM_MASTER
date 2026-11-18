#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "📺 لاگ زنده — بعد از تست Ctrl+C بزن"
echo "═══════════════════════════════════════════════════"
echo ""
echo "🎯 الان توی تلگرام این کارا رو بکن:"
echo "  ۱. روی کاربر «8401175719» ریپلای کن"
echo "  ۲. بنویس: افزودن مدیر"
echo "  ۳. سه تا تیک بزن"
echo "  ۴. تایید و بستن"
echo "  ۵. بعد: پیکربندی"
echo "  ۶. بعد: دسترسی روی همون کاربر"
echo ""
echo "بعد Ctrl+C بزن و خروجی رو بفرست"
echo "═══════════════════════════════════════════════════"
echo ""

tail -f ~/groupbot_bot.log | grep --line-buffered -E "PM_|pm_|PROMOTE|HANDLER DEBUG|CALLBACK|acc_|Traceback|ERROR|Error"
