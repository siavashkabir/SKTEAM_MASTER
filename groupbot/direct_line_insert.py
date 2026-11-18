import os, shutil, py_compile, time

print("="*80)
print("🔧 درج مستقیم بعد از خط 476")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/reply.py.bak_direct_{ts}'
shutil.copy('modules/reply.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/reply.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === پیدا کردن reset_timer (خط 476) ===
reset_idx = None
for i, line in enumerate(lines):
    if 'reset_timer(context, sent.chat.id, sent.message_id)' in line:
        reset_idx = i
        break

if reset_idx is None:
    print("❌ reset_timer پیدا نشد!")
    exit(1)

print(f"📍 reset_timer در خط {reset_idx+1}: {repr(lines[reset_idx])}")

# indent خط
indent = len(lines[reset_idx]) - len(lines[reset_idx].lstrip())
i_p = ' ' * indent
i_b = ' ' * (indent + 4)

print(f"📌 indent تشخیص داده شده: {indent}")

# === ساخت بلوک Register ===
reg_block = [
    f'{i_p}# [PER-USER PANEL GUARD] Register\n',
    f'{i_p}try:\n',
    f'{i_b}from modules.start import ACTIVE_PANELS\n',
    f'{i_b}ACTIVE_PANELS[(user.id, chat.id)] = sent.message_id\n',
    f'{i_b}print(f"[PANEL GUARD] Registered msg={{sent.message_id}}")\n',
    f'{i_p}except Exception as _re:\n',
    f'{i_b}print("[PANEL GUARD REG ERR] " + str(_re))\n',
]

# درج بعد از خط reset_timer
lines = lines[:reset_idx+1] + reg_block + lines[reset_idx+1:]

with open('modules/reply.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"✅ بلوک Register ({len(reg_block)} خط) درج شد.")

# === نمایش نهایی ===
print("\n=== ناحیه نهایی ===")
with open('modules/reply.py', 'r', encoding='utf-8') as f:
    new_lines = f.readlines()

for i, line in enumerate(new_lines):
    if 'PANEL GUARD] Registered' in line:
        for j in range(max(0, i-5), min(len(new_lines), i+5)):
            marker = " ←" if j == i else ""
            print(f"   {j+1}: {new_lines[j].rstrip()}{marker}")
        break

# === کامپایل ===
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/reply.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/reply.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# === ری‌استارت ===
print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ حالا کامل شد! تست کن.")
print("="*80)
