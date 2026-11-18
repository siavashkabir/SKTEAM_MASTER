import os, shutil, time, subprocess

print("="*70)
print("🔒 نصب سیستم Lock File برای اجرای فقط یک نسخه از ربات")
print("="*70)

print("\n=== 1. کشتن نسخه‌های قبلی (فقط با pkill، بدون killall) ===")
patterns = ["main.py", "bot_watchdog.sh", "connection_monitor.py", "run_bot.sh", "start.sh"]
for p in patterns:
    try:
        result = subprocess.run(['pkill', '-9', '-f', p], capture_output=True, timeout=5)
        print(f"   ✅ الگوی '{p}' کشته شد.")
    except subprocess.TimeoutExpired:
        print(f"   ⚠️ تایم‌اوت در کشتن '{p}'")
    except Exception as e:
        print(f"   ⚠️ خطا در کشتن '{p}': {e}")
time.sleep(4)
print("✅ عملیات کشتن تمام شد.")

print("\n=== 2. بررسی اینکه پردازش ربات باقی نمانده باشد ===")
result = subprocess.run(['bash', '-c', 'ps aux | grep -E "main.py|bot_watchdog|run_bot" | grep -v grep'], capture_output=True, text=True, timeout=10)
if result.stdout.strip():
    print("⚠️ این پردازش‌ها هنوز زنده هستند:")
    print(result.stdout)
else:
    print("✅ تمام پردازش‌های ربات متوقف شدند.")

print("\n=== 3. ساخت فایل run_bot.sh با Lock File ===")
run_bot_content = '''#!/data/data/com.termux/files/usr/bin/bash
# run_bot.sh - اجرای ربات با قفل انحصاری

LOCK_FILE="/data/data/com.termux/files/home/groupbot/.bot.lock"
exec 9>"$LOCK_FILE"

if ! flock -n 9; then
    echo "[$(date '+%H:%M:%S')] [LOCK] ربات دیگری فعال است. خروج."
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
print("✅ run_bot.sh ساخته شد.")

print("\n=== 4. بازنویسی bot_watchdog.sh ===")
watchdog_content = '''#!/data/data/com.termux/files/usr/bin/bash
# bot_watchdog.sh - چک کردن و ری‌استارت ربات با Lock File

LOCK_FILE="/data/data/com.termux/files/home/groupbot/.bot.lock"
exec 9>"$LOCK_FILE"

if flock -n 9; then
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] ربات خاموش است. ری‌استارت..."
    cd /data/data/com.termux/files/home/groupbot
    flock -u 9
    exec 9>&-
    nohup bash /data/data/com.termux/files/home/groupbot/run_bot.sh > /data/data/com.termux/files/home/groupbot_watchdog.log 2>&1 &
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] ربات اجرا شد."
else
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] ربات فعال است."
fi
'''
with open('bot_watchdog.sh', 'w', encoding='utf-8') as f:
    f.write(watchdog_content)
os.chmod('bot_watchdog.sh', 0o755)
print("✅ bot_watchdog.sh بازنویسی شد.")

print("\n=== 5. تنظیم کرون‌جاب (هر 2 دقیقه watchdog) ===")
existing_cron = subprocess.run(['crontab', '-l'], capture_output=True, text=True, timeout=10).stdout
lines = [l for l in existing_cron.split('\n') if 'groupbot' not in l.lower() and 'bot_watchdog' not in l.lower() and l.strip()]
lines.append("*/2 * * * * /data/data/com.termux/files/home/groupbot/bot_watchdog.sh > /dev/null 2>&1")
cron_content = '\n'.join(lines) + '\n'
with open(os.path.expanduser('~/crontab_new.txt'), 'w') as f:
    f.write(cron_content)
subprocess.run(['crontab', os.path.expanduser('~/crontab_new.txt')], timeout=10)
print("✅ کرون‌جاب به‌روزرسانی شد:")
print(cron_content)

print("\n=== 6. اجرای اولیه ربات از طریق run_bot.sh ===")
subprocess.Popen(
    ['bash', '-c', 'cd ~/groupbot && nohup bash run_bot.sh > ~/groupbot_bot.log 2>&1 &'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
time.sleep(6)

print("\n=== 7. بررسی نهایی ===")
result = subprocess.run(['bash', '-c', 'ps aux | grep -E "main.py|run_bot.sh|bot_watchdog" | grep -v grep'], capture_output=True, text=True, timeout=10)
print("📊 پردازش‌های در حال اجرا:")
print(result.stdout if result.stdout.strip() else "❌ هیچ پردازشی نیست!")

count = 0
for line in result.stdout.split('\n'):
    if 'python3 -u main.py' in line and 'grep' not in line:
        count += 1
print(f"\n🎯 تعداد ربات‌های اصلی: {count}")
if count == 1:
    print("✅ عالی! فقط یک ربات در حال اجراست.")
elif count == 0:
    print("⚠️ ربات بالا نیامد. لاگ را ببینید.")
else:
    print(f"⚠️ {count} نسخه در حال اجراست!")

print("\n=== 8. 10 خط آخر لاگ ربات ===")
os.system('tail -n 10 ~/groupbot_bot.log')

print("\n=== 9. تنظیمات کرون‌جاب فعلی ===")
os.system('crontab -l')

print("\n" + "="*70)
print("✅ نصب سیستم Lock File کامل شد.")
print("="*70)
