#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, shutil, py_compile, time, re

TARGET = "modules/start.py"
ts = time.strftime("%H%M%S")
bak = f"{TARGET}.bak_rmdbg_{ts}"

print("="*70)
print("🧹 حذف debug owner_section_back")
print("="*70)

shutil.copy(TARGET, bak)
print(f"✅ بکاپ: {bak}")

with open(TARGET, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# پیدا کردن خط debug
removed = 0
new_lines = []
for i, l in enumerate(lines):
    if '[DBG-BACK] ENTER' in l and l.strip().startswith('print('):
        print(f"🗑 حذف خط {i+1}: {l.rstrip()[:80]}")
        removed += 1
        continue
    new_lines.append(l)

if removed == 0:
    print("ℹ️ خط debug پیدا نشد (شاید قبلاً حذف شده)")
    exit(0)

with open(TARGET, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"\n✅ {removed} خط حذف شد")

print("\n🔍 py_compile...")
try:
    py_compile.compile(TARGET, doraise=True)
    print("✅ کامپایل OK")
except Exception as e:
    print(f"❌ {e}")
    shutil.copy(bak, TARGET)
    print("🔄 rollback")
    exit(1)

for root, dirs, files in os.walk('.'):
    if 'venv' in root: continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

print("\n🔄 ری‌استارت...")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(12)

print("\n" + "="*70)
print("✅ پاک‌سازی تمام شد")
print("="*70)
print(f"""
📌 حالا کد تمیزه. `[HANDLER DEBUG]` برای باگ‌های بعدی کافیه.

🔙 برگرداندن اگه لازم شد:
   cp {bak} {TARGET}
   pkill -9 -f main.py && sleep 3
   nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &

📄 لاگ زنده:
""")
os.system('tail -F ~/groupbot_bot.log')
