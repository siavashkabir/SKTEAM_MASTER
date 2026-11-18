import os, shutil, py_compile, time

print("="*80)
print("🔧 حذف دقیق ۵ دکمه قدیمی از owner_manage_menu")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_removeold_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ==== 1. پیدا کردن def owner_manage_menu ====
func_start = None
for i, line in enumerate(lines):
    if line.startswith('def owner_manage_menu('):
        func_start = i
        break

if func_start is None:
    print("❌ owner_manage_menu پیدا نشد!")
    exit(1)
print(f"📍 owner_manage_menu در خط {func_start+1}")

# ==== 2. پیدا کردن انتهای تابع ====
func_end = len(lines)
for j in range(func_start + 1, len(lines)):
    if lines[j].startswith('def ') or lines[j].startswith('async def '):
        func_end = j
        break
print(f"📍 انتهای تابع در خط {func_end}")

# ==== 3. چک محتوای تابع ====
print("\n=== محتوای owner_manage_menu ===")
for i in range(func_start, min(func_end, func_start + 30)):
    print(f"   {i+1}: {lines[i].rstrip()[:120]}")

# ==== 4. حذف دکمه‌های قدیمی (فقط در این تابع) ====
print("\n=== حذف دکمه‌ها ===")
targets = ['menu_owners:', 'menu_admins:', 'menu_vip:', 'menu_deputies:', 'menu_admin_perms:']

to_remove = []
for i in range(func_start, func_end):
    line = lines[i]
    if 'InlineKeyboardButton' not in line:
        continue
    for t in targets:
        if f'callback_data="{t}' in line:
            to_remove.append(i)
            print(f"🗑 حذف خط {i+1}: {line.strip()[:100]}")
            break

if not to_remove:
    print("⚠️ هیچ دکمه‌ای برای حذف پیدا نشد (ممکنه قبلاً حذف شده باشه).")
    exit(0)

# حذف از آخر به اول
new_lines = [l for i, l in enumerate(lines) if i not in to_remove]
print(f"\n✅ {len(to_remove)} خط حذف شد.")

# ==== 5. نوشتن ====
with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# ==== 6. نمایش تابع جدید ====
print("\n=== owner_manage_menu بعد از حذف ===")
with open('modules/start.py', 'r', encoding='utf-8') as f:
    nl = f.readlines()

for i, line in enumerate(nl):
    if line.startswith('def owner_manage_menu('):
        for j in range(i, min(i+25, len(nl))):
            print(f"   {j+1}: {nl[j].rstrip()[:120]}")
        break

# ==== 7. کامپایل ====
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ==== 8. ری‌استارت ====
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 5 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد!")
print("="*80)
