import os, shutil, glob, py_compile, time

print("="*80)
print("🔄 بازگردانی همه فایل‌ها به حالت قبل از ادغام")
print("="*80)

# پیدا کردن بکاپ‌های merge
merge_baks = glob.glob('modules/*.bak_merge_*')
nac_baks = glob.glob('modules/*.bak_nac_*')

print(f"📊 بکاپ‌های merge: {len(merge_baks)}")
print(f"📊 بکاپ‌های nac: {len(nac_baks)}")

# برای هر فایل modules، آخرین بکاپ merge رو پیدا کن
restored = 0
for f in glob.glob('modules/*.py'):
    if '.bak' in f:
        continue
    
    basename = os.path.basename(f)
    # جدیدترین بکاپ merge برای این فایل
    candidates = sorted(
        [b for b in merge_baks if os.path.basename(b).startswith(basename + '.bak_merge_')],
        reverse=True
    )
    
    if not candidates:
        print(f"  ⚠️ {f}: بکاپ merge پیدا نشد")
        continue
    
    try:
        shutil.copy(candidates[0], f)
        restored += 1
    except Exception as e:
        print(f"  ❌ {f}: {e}")

print(f"\n✅ {restored} فایل بازگردانی شد")

# کامپایل همه
print("\n=== کامپایل ===")
failed = []
for f in glob.glob('modules/*.py'):
    if '.bak' in f:
        continue
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        failed.append(f)
        print(f"  ❌ {f}: {e}")

if not failed:
    print("✅ همه فایل‌ها سالم")
else:
    print(f"\n⚠️ {len(failed)} فایل هنوز خراب")

# کش
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

# ری‌استارت
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 5 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ فایل‌ها به حالت قبل از ادغام برگشتن (بازگشت و بستن جدا)")
print("="*80)
