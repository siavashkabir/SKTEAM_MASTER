import os, shutil, py_compile, time, subprocess

print("="*80)
print("🔧 نصب کامل Auto-Start + Auto-Reconnect (نسخه نهایی)")
print("="*80)

# ==== 1. بکاپ ====
ts = time.strftime("%H%M%S")
for f in ['bot_watchdog.sh', 'run_bot.sh']:
    if os.path.exists(f):
        shutil.copy(f, f'{f}.bak_final_{ts}')
shutil.copy(os.path.expanduser('~/.bashrc'), os.path.expanduser(f'~/.bashrc.bak_final_{ts}'))
print(f"✅ بکاپ‌ها ساخته شدند.")

# ==== 2. ساخت run_monitor.sh ====
print("\n=== 1. ساخت run_monitor.sh ===")
monitor_sh = '''#!/data/data/com.termux/files/usr/bin/bash
# run_monitor.sh - اجرای connection_monitor با Lock File
LOCK_FILE="/data/data/com.termux/files/home/groupbot/.monitor.lock"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "[$(date '+%H:%M:%S')] [MONITOR LOCK] Already running. Exit."
    exit 0
fi
cd /data/data/com.termux/files/home/groupbot
source venv/bin/activate
exec python3 -u connection_monitor.py
'''
with open('run_monitor.sh', 'w') as f:
    f.write(monitor_sh)
os.chmod('run_monitor.sh', 0o755)
print("✅ run_monitor.sh ساخته شد.")

# ==== 3. بازنویسی run_bot.sh ====
print("\n=== 2. بازنویسی run_bot.sh ===")
run_bot_sh = '''#!/data/data/com.termux/files/usr/bin/bash
# run_bot.sh - اجرای ربات با Lock File
LOCK_FILE="/data/data/com.termux/files/home/groupbot/.bot.lock"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "[$(date '+%H:%M:%S')] [BOT LOCK] Already running. Exit."
    exit 0
fi
cd /data/data/com.termux/files/home/groupbot
source venv/bin/activate
exec python3 -u main.py
'''
with open('run_bot.sh', 'w') as f:
    f.write(run_bot_sh)
os.chmod('run_bot.sh', 0o755)
print("✅ run_bot.sh بازنویسی شد.")

# ==== 4. بازنویسی bot_watchdog.sh (چک هر دو) ====
print("\n=== 3. بازنویسی bot_watchdog.sh (چک ربات + مونیتور) ===")
watchdog = '''#!/data/data/com.termux/files/usr/bin/bash
# bot_watchdog.sh - چک کردن ربات + connection_monitor

cd /data/data/com.termux/files/home/groupbot

# --- چک ربات ---
if ! pgrep -f "python3 -u main.py" > /dev/null 2>&1; then
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Bot is DOWN. Starting..."
    nohup bash /data/data/com.termux/files/home/groupbot/run_bot.sh > /data/data/com.termux/files/home/groupbot_watchdog.log 2>&1 &
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Bot started."
else
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Bot is running."
fi

# --- چک connection_monitor ---
if ! pgrep -f "python3 -u connection_monitor.py" > /dev/null 2>&1; then
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Monitor is DOWN. Starting..."
    nohup bash /data/data/com.termux/files/home/groupbot/run_monitor.sh > /data/data/com.termux/files/home/groupbot_monitor_runner.log 2>&1 &
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Monitor started."
else
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Monitor is running."
fi
'''
with open('bot_watchdog.sh', 'w') as f:
    f.write(watchdog)
os.chmod('bot_watchdog.sh', 0o755)
print("✅ bot_watchdog.sh بازنویسی شد.")

# ==== 5. اصلاح .bashrc ====
print("\n=== 4. اصلاح .bashrc ===")
bashrc = os.path.expanduser('~/.bashrc')
with open(bashrc, 'r') as f:
    content = f.read()

# حذف خطوط قدیمی groupbot
lines = content.split('\n')
new_lines = []
skip_next = 0
for i, line in enumerate(lines):
    if skip_next > 0:
        skip_next -= 1
        continue
    if 'GROUPBOT' in line or ('groupbot' in line.lower() and ('bash' in line or 'nohup' in line)):
        # پاک کردن این خط و 5 خط بعدی (بلاک)
        skip_next = 5
        continue
    new_lines.append(line)

content = '\n'.join(new_lines)

# اضافه کردن بلاک جدید
autostart_block = '''
# ===== GROUPBOT AUTOSTART =====
if ! pgrep -f "bot_watchdog.sh" > /dev/null 2>&1; then
    bash /data/data/com.termux/files/home/groupbot/bot_watchdog.sh > /dev/null 2>&1 &
fi
# ================================
'''

if '# ===== GROUPBOT AUTOSTART =====' not in content:
    content = content.rstrip() + '\n' + autostart_block
    with open(bashrc, 'w') as f:
        f.write(content)
    print("✅ بلاک autostart به .bashrc اضافه شد.")
else:
    print("⚠️ از قبل وجود دارد.")

# ==== 6. تنظیم crontab ====
print("\n=== 5. تنظیم crontab ===")
# خواندن فعلی
existing = subprocess.run(['crontab', '-l'], capture_output=True, text=True).stdout
# حذف خطوط groupbot قبلی
keep = [l for l in existing.split('\n') if 'groupbot' not in l.lower() and l.strip()]
# اضافه کردن خط جدید
keep.append('*/2 * * * * /data/data/com.termux/files/home/groupbot/bot_watchdog.sh > /dev/null 2>&1')
new_cron = '\n'.join(keep) + '\n'
with open(os.path.expanduser('~/crontab_new.txt'), 'w') as f:
    f.write(new_cron)
subprocess.run(['crontab', os.path.expanduser('~/crontab_new.txt')], timeout=10)
print("✅ crontab تنظیم شد:")
print(new_cron)

# ==== 7. کشتن همه چیز و راه‌اندازی تازه ====
print("\n=== 6. راه‌اندازی مجدد همه چیز ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
os.system('pkill -9 -f "bot_watchdog.sh"')
time.sleep(3)

# راه‌اندازی watchdog (که خودش همه رو بالا می‌آره)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)

# ==== 8. بررسی نهایی ====
print("\n=== 7. بررسی نهایی ===")
result = subprocess.run(['bash', '-c', 'ps aux | grep -E "main.py|connection_monitor|bot_watchdog" | grep -v grep'],
                       capture_output=True, text=True)
print("📊 پردازش‌های در حال اجرا:")
print(result.stdout if result.stdout.strip() else "❌ هیچی نیست!")

# شمارش
main_count = len([l for l in result.stdout.split('\n') if 'python3 -u main.py' in l and 'grep' not in l])
mon_count = len([l for l in result.stdout.split('\n') if 'connection_monitor.py' in l and 'grep' not in l])
print(f"\n🎯 تعداد ربات: {main_count}")
print(f"🎯 تعداد monitor: {mon_count}")

if main_count == 1 and mon_count == 1:
    print("✅ همه چیز درست راه‌اندازی شد!")
elif main_count == 0 or mon_count == 0:
    print("⚠️ یکی از سرویس‌ها بالا نیامد!")
else:
    print(f"⚠️ تعداد زیاد! main={main_count} monitor={mon_count}")

print("\n=== 8. لاگ ربات ===")
os.system('tail -n 6 ~/groupbot_bot.log 2>/dev/null')
print("\n=== 9. لاگ watchdog ===")
os.system('tail -n 10 ~/groupbot_watchdog.log 2>/dev/null')

print("\n" + "="*80)
print("✅ نصب کامل شد!")
print("="*80)
print("""
📌 قابلیت‌ها:
   ✅ Auto-Start در Termux (باز شدن خودکار)
   ✅ Auto-Reconnect (ری‌کانکت VPN)
   ✅ Watchdog هر 2 دقیقه
   ✅ Lock File (فقط یک نسخه)
   ✅ چک هم‌زمان ربات + monitor

📌 تست:
   1. ترموکس رو ببند
   2. دوباره باز کن
   3. باید همه چیز خودکار بالا بیاد
   4. فقط یک نسخه از هر کدام
""")
