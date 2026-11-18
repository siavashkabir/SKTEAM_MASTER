import os, shutil, time, subprocess

print("="*70)
print("🔒 نصب سیستم Lock File برای اجرای فقط یک نسخه از ربات")
print("="*70)

print("\n=== 1. بکاپ از فایل‌های موجود ===")
timestamp = time.strftime("%H%M%S")
try:
    if os.path.exists('bot_watchdog.sh'):
        shutil.copy('bot_watchdog.sh', f'bot_watchdog.sh.bak_{timestamp}')
    if os.path.exists(os.path.expanduser('~/.bashrc')):
        shutil.copy(os.path.expanduser('~/.bashrc'), os.path.expanduser(f'~/.bashrc.bak_{timestamp}'))
    print(f"✅ بکاپ‌های امنیتی با تاریخ {timestamp} ایجاد شدند.")
except Exception as e:
    print(f"⚠️ خطای جزئی در بکاپ: {e}")

print("\n=== 2. کشتن تمام نسخه‌های قبلی ربات ===")
for p in ["main.py", "bot_watchdog.sh", "connection_monitor.py", "run_bot.sh"]:
    os.system(f'pkill -9 -f "{p}" 2>/dev/null')
time.sleep(3)
os.system('killall -9 python3 2>/dev/null')
time.sleep(2)
print("✅ تمام پردازش‌های قبلی متوقف شدند.")

print("\n=== 3. ساخت فایل run_bot.sh (اجرای ربات با Lock File) ===")
run_bot_content = '''#!/data/data/com.termux/files/usr/bin/bash
# run_bot.sh - اجرای ربات با قفل انحصاری (فقط یک نسخه می‌تواند اجرا شود)

LOCK_FILE="/data/data/com.termux/files/home/groupbot/.bot.lock"

# باز کردن قفل فایل
exec 9>"$LOCK_FILE"

# تلاش برای گرفتن قفل انحصاری (non-blocking)
if ! flock -n 9; then
    echo "[$(date '+%H:%M:%S')] [LOCK] ربات دیگری در حال اجراست. این نمونه خارج می‌شود."
    exit 0
fi

echo "[$(date '+%H:%M:%S')] [LOCK] قفل گرفته شد. اجرای ربات..."
cd /data/data/com.termux/files/home/groupbot
source venv/bin/activate
exec python3 -u main.py
'''
with open('run_bot.sh', 'w', encoding='utf-8') as f:
    f.write(run_bot_content)
os.chmod('run_bot.sh', 0o755)
print("✅ فایل run_bot.sh با مکانیزم Lock File ساخته شد.")

print("\n=== 4. بازنویسی bot_watchdog.sh (استفاده از Lock File) ===")
watchdog_content = '''#!/data/data/com.termux/files/usr/bin/bash
# bot_watchdog.sh - بررسی و ری‌استارت ربات با مکانیزم Lock File

LOCK_FILE="/data/data/com.termux/files/home/groupbot/.bot.lock"

# باز کردن قفل فایل
exec 9>"$LOCK_FILE"

# تلاش برای گرفتن قفل
if flock -n 9; then
    # قفل آزاد است یعنی ربات خاموش است
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] ربات خاموش است. در حال ری‌استارت..."
    cd /data/data/com.termux/files/home/groupbot
    source venv/bin/activate
    # رها کردن قفل قبل از اجرای ربات جدید (چون run_bot.sh خودش قفل می‌گیرد)
    flock -u 9
    exec 9>&-
    # اجرای ربات از طریق run_bot.sh
    nohup bash /data/data/com.termux/files/home/groupbot/run_bot.sh > /data/data/com.termux/files/home/groupbot_watchdog.log 2>&1 &
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] ربات با موفقیت اجرا شد."
else
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] ربات در حال اجراست (قفل فعال)."
fi
'''
with open('bot_watchdog.sh', 'w', encoding='utf-8') as f:
    f.write(watchdog_content)
os.chmod('bot_watchdog.sh', 0o755)
print("✅ فایل bot_watchdog.sh بازنویسی شد.")

print("\n=== 5. تنظیم کرون‌جاب برای اجرای watchdog هر 2 دقیقه ===")
cron_line = "*/2 * * * * /data/data/com.termux/files/home/groupbot/bot_watchdog.sh > /dev/null 2>&1"
# خواندن کرون‌جاب فعلی
existing_cron = subprocess.run(['crontab', '-l'], capture_output=True, text=True).stdout
# حذف خطوط قبلی مربوط به گروه‌بات
lines = [l for l in existing_cron.split('\n') if 'groupbot' not in l.lower() and 'bot_watchdog' not in l.lower() and l.strip()]
# اضافه کردن خط جدید
lines.append(cron_line)
# نوشتن کرون‌جاب جدید
cron_content = '\n'.join(lines) + '\n'
with open(os.path.expanduser('~/crontab_new.txt'), 'w') as f:
    f.write(cron_content)
os.system('crontab ~/crontab_new.txt')
print("✅ کرون‌جاب به‌روزرسانی شد.")

print("\n=== 6. اجرای اولیه ربات با run_bot.sh ===")
os.system('cd ~/groupbot && nohup bash run_bot.sh > ~/groupbot_bot.log 2>&1 &')
time.sleep(5)

print("\n=== 7. بررسی نهایی وضعیت ===")
result = subprocess.run(['bash', '-c', 'ps aux | grep -E "main.py|run_bot.sh|bot_watchdog" | grep -v grep'], capture_output=True, text=True)
print("📊 پردازش‌های در حال اجرا:")
print(result.stdout if result.stdout.strip() else "❌ هیچ پردازشی پیدا نشد!")

# شمارش دقیق ربات‌های اصلی
count = 0
for line in result.stdout.split('\n'):
    if 'python3 -u main.py' in line and 'grep' not in line:
        count += 1
print(f"\n🎯 تعداد ربات‌های اصلی (main.py): {count}")
if count == 1:
    print("✅ عالی! فقط یک ربات در حال اجراست.")
elif count == 0:
    print("⚠️ ربات بالا نیامد. لاگ را بررسی کنید.")
else:
    print(f"⚠️ هنوز {count} نسخه از ربات در حال اجراست!")

print("\n=== 8. 10 خط آخر لاگ ربات ===")
os.system('tail -n 10 ~/groupbot_bot.log')

print("\n=== 9. تنظیمات کرون‌جاب فعلی ===")
os.system('crontab -l')

print("\n" + "="*70)
print("✅ نصب سیستم تک‌نسخه‌ای کامل شد.")
print("="*70)
