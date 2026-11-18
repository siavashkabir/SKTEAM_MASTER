# 🚨 راهنمای اضطراری Sk.Team
# برای وقتی ربات کرش کرده یا کار نمی‌کنه

═══════════════════════════════════════════════════════════════
🎯 قدم اول: تشخیص سریع (کجا باید بری)
═══════════════════════════════════════════════════════════════

cd ~/groupbot && source venv/bin/activate

═══════════════════════════════════════════════════════════════
📊 ۱. وضعیت ربات
═══════════════════════════════════════════════════════════════

# ربات در حال اجراست؟
ps aux | grep main.py | grep -v grep

# نسخه‌ی ساده‌تر
pgrep -f main.py

# چند تا پروسه هست؟
pgrep -fc main.py


═══════════════════════════════════════════════════════════════
🔄 ۲. ری‌استارت سریع (اگر کرش کرده)
═══════════════════════════════════════════════════════════════

# روش ۱: ری‌استارت کامل با watchdog
cd ~/groupbot && pkill -9 -f "main.py" ; sleep 3 && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 & sleep 15 && tail -n 10 ~/groupbot_bot.log

# روش ۲: ری‌استارت ساده بدون watchdog
cd ~/groupbot && pkill -9 -f "main.py" ; sleep 3 && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 12 && tail -n 20 ~/groupbot_bot.log

# روش ۳: اگر watchdog خرابه، فقط ربات رو بالا بیار
cd ~/groupbot && source venv/bin/activate && pkill -9 -f main.py ; sleep 3 && nohup bash run_bot.sh > ~/groupbot_bot.log 2>&1 &


═══════════════════════════════════════════════════════════════
📄 ۳. دیدن لاگ (مهم‌ترین کار)
═══════════════════════════════════════════════════════════════

# ۵۰ خط آخر لاگ (سریع)
tail -n 50 ~/groupbot_bot.log

# ۱۰۰ خط آخر
tail -n 100 ~/groupbot_bot.log

# لاگ زنده (Ctrl+C برای خروج)
tail -F ~/groupbot_bot.log

# فقط خطاها
tail -n 200 ~/groupbot_bot.log | grep -E "ERR|Traceback|Exception|CRITICAL" | tail -20

# خالی کردن لاگ (اگه خیلی بزرگ شده)
> ~/groupbot_bot.log


═══════════════════════════════════════════════════════════════
🩺 ۴. دیاگنوستیک خودکار
═══════════════════════════════════════════════════════════════

# اجرای دیاگنوستیک کامل
cd ~/groupbot && python3 ~/diag.py

# دیدن گزارش
cat ~/diag_report.txt

# ارسال گزارش به تلگرام
cd ~/groupbot && python3 ~/diag_send.py


═══════════════════════════════════════════════════════════════
🌐 ۵. چک اتصال و VPN
═══════════════════════════════════════════════════════════════

# اتصال به تلگرام
curl -s -m 5 -o /dev/null -w "Telegram: %{http_code}\n" https://api.telegram.org

# اتصال به گوگل
curl -s -m 5 -o /dev/null -w "Google: %{http_code}\n" https://google.com

# اگه قطع بود: VPN رو خاموش/روشن کن (JumpJump)
# بعد ربات رو ری‌استارت کن


═══════════════════════════════════════════════════════════════
🗄 ۶. چک دیتابیس
═══════════════════════════════════════════════════════════════

# سلامت دیتابیس
cd ~/groupbot && python3 -c "
import sqlite3
from config import DATABASE_PATH
c = sqlite3.connect(DATABASE_PATH)
cur = c.cursor()
cur.execute('PRAGMA integrity_check')
print('Integrity:', cur.fetchone()[0])
cur.execute('SELECT COUNT(*) FROM sqlite_master WHERE type=\"table\"')
print('Tables:', cur.fetchone()[0])
c.close()
"

# حجم دیتابیس
ls -lh ~/groupbot/data/groupbot.db


═══════════════════════════════════════════════════════════════
💾 ۷. بکاپ گرفتن
═══════════════════════════════════════════════════════════════

# بکاپ سریع دیتابیس
cp ~/groupbot/data/groupbot.db ~/groupbot_db.bak_$(date +%Y%m%d_%H%M%S)

# بکاپ کامل با اسکریپت
cd ~/groupbot && python3 create_full_backup.py

# دیدن بکاپ‌ها
ls -lht ~/backups/ | head -5


═══════════════════════════════════════════════════════════════
🔧 ۸. رفع مشکلات رایج
═══════════════════════════════════════════════════════════════

# ❌ ربات بالا نمیاد: "ImportError" یا "ModuleNotFoundError"
cd ~/groupbot && source venv/bin/activate
python3 -c "import telegram; print(telegram.__version__)"

# ❌ ربات بالا نمیاد: "Conflict: terminated by other getUpdates"
# یعنی دو نسخه ربات در حال اجراست
pkill -9 -f main.py ; sleep 5
pgrep -fc main.py    # باید 0 باشه
# بعد ری‌استارت کن

# ❌ خطای "Session" یا VPN
# VPN رو ری‌استارت کن، بعد:
cd ~/groupbot && pkill -9 -f main.py ; sleep 3 && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &

# ❌ دیتابیس قفل شده
pkill -9 -f main.py ; sleep 5
rm -f ~/groupbot/data/groupbot.db-journal ~/groupbot/data/groupbot.db-wal
cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &


═══════════════════════════════════════════════════════════════
🔍 ۹. رفع کرش بعد از یه تغییر
═══════════════════════════════════════════════════════════════

# ۱. ببین کدوم فایل آخر تغییر کرده
ls -lht ~/groupbot/modules/*.py | head -5

# ۲. بکاپ‌های موجود فایل رو ببین
ls -lht ~/groupbot/modules/file.py.bak_* 2>/dev/null | head -5

# ۳. برگردون به آخرین بکاپ
cp ~/groupbot/modules/file.py.bak_YYYYMMDD_HHMMSS ~/groupbot/modules/file.py

# ۴. کامپایل چک
python3 -m py_compile ~/groupbot/modules/file.py

# ۵. ری‌استارت
cd ~/groupbot && pkill -9 -f main.py ; sleep 3 && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &


═══════════════════════════════════════════════════════════════
📁 ۱۰. ساختار فایل‌های مهم
═══════════════════════════════════════════════════════════════

~/groupbot/
├── main.py                 ← فایل اصلی
├── config.py               ← تنظیمات (OWNER_ID, BOT_TOKEN)
├── database.py             ← توابع دیتابیس
├── modules/                ← ۲۸۰+ ماژول
│   ├── start.py            ← هسته اصلی (~6900 خط)
│   ├── reply.py            ← هندلر پیام‌ها
│   ├── moderation.py       ← بن/سکوت
│   ├── owner_panel_trigger.py
│   ├── system_management.py
│   ├── logger.py
│   ├── force_join.py
│   └── ...
├── data/
│   └── groupbot.db         ← دیتابیس
├── backups/                ← بکاپ‌ها
└── venv/                   ← محیط پایتون

~/groupbot_bot.log         ← لاگ اصلی
~/groupbot_watchdog.log    ← لاگ watchdog
~/diag_report.txt          ← گزارش دیاگنوستیک


═══════════════════════════════════════════════════════════════
⚙️ ۱۱. دستورات Cron (خودکار)
═══════════════════════════════════════════════════════════════

# دیدن cron jobs
crontab -l

# cron ها:
# هر ۲ دقیقه: bot_watchdog.sh
# هر ساعت: ~/diag.py
# هر ۶ ساعت: ~/diag_send.py


═══════════════════════════════════════════════════════════════
🆔 ۱۲. اطلاعات کلیدی
═══════════════════════════════════════════════════════════════

سازنده (OWNER_ID): 7955185125
یوزرنیم: @Siavashska
گروه تست: -100191141484
ربات: @sk_team_manager_bot
کانال لاگ: @skteamlogchannell

DB Path: ~/groupbot/data/groupbot.db
Log: ~/groupbot_bot.log


═══════════════════════════════════════════════════════════════
🚨 ۱۳. پروتکل اضطراری (چک‌لیست ۵ مرحله‌ای)
═══════════════════════════════════════════════════════════════

اگه ربات کرش کرد، این ۵ مرحله رو به ترتیب بزن:

□ ۱. چک کن ربات در حال اجراست:
   pgrep -fc main.py

□ ۲. اگه ۰ بود، ربات متوقفه. لاگ رو ببین:
   tail -n 50 ~/groupbot_bot.log

□ ۳. اگه خطای VPN بود، VPN رو ری‌استارت کن.
   اگه خطای کد بود، بکاپ‌ها رو ببین.

□ ۴. ربات رو ری‌استارت کن:
   cd ~/groupbot && pkill -9 -f main.py ; sleep 3 && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 & sleep 15 && tail -n 10 ~/groupbot_bot.log

□ ۵. ۱۲ ثانیه صبر کن، اگه دیدی "Bot is starting polling..." یعنی درست شد.

اگه بعد از اینا هنوز خراب بود → دیاگنوستیک بزن:
   cd ~/groupbot && python3 ~/diag.py


═══════════════════════════════════════════════════════════════
💡 ۱۴. نکات مهم
═══════════════════════════════════════════════════════════════

⚠️ ۱. هرگز چند نسخه main.py رو با هم اجرا نکن
⚠️ ۲. قبل از هر تغییر، بکاپ بگیر
⚠️ ۳. VPN ناپایداره — اگه خطا دیدی، اول VPN رو چک کن
⚠️ ۴. اگه لاگ خیلی بزرگ شد، پاکش کن (> ~/groupbot_bot.log)
⚠️ ۵. اگه یه فایل رو تغییر دادی و خراب شد، از .bak استفاده کن

═══════════════════════════════════════════════════════════════
✅ پایان راهنما — این فایل رو روی گوشی ذخیره کن
═══════════════════════════════════════════════════════════════
