import os, shutil, py_compile, time

print("="*80)
print("🔧 افزودن تایمر 10 ثانیه‌ای به پیام «زمان استفاده...»")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_autodel_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === پیدا کردن خط edit_message_text با متن "زمان استفاده" ===
target_idx = None
for i, line in enumerate(lines):
    if 'زمان استفاده' in line and 'text=' in line:
        target_idx = i
        break

if target_idx is None:
    print("❌ خط پیدا نشد!")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

print(f"📍 خط هدف (text=زمان استفاده...): {target_idx+1}")
print(f"   {repr(lines[target_idx])}")

# === پیدا کردن خط "if _expire_del > 0:" که بعد از edit هست ===
expire_idx = None
for j in range(target_idx, min(target_idx + 20, len(lines))):
    if 'if _expire_del' in lines[j]:
        expire_idx = j
        break

if expire_idx is None:
    print("❌ خط 'if _expire_del' پیدا نشد!")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

print(f"📍 خط 'if _expire_del > 0:' در: {expire_idx+1}")

# indent خط if _expire_del
indent_e = len(lines[expire_idx]) - len(lines[expire_idx].lstrip())
i_e = ' ' * indent_e
i_eb = ' ' * (indent_e + 4)

# === بلوک تایمر جدید ===
autodel_block = [
    f'{i_e}# [TIMEOUT AUTODELETE] حذف پیام بعد از 10 ثانیه (در هر شرایطی)\n',
    f'{i_e}try:\n',
    f'{i_eb}context.job_queue.run_once(\n',
    f'{i_eb}    _delete_expired_msg, 10,\n',
    f'{i_eb}    chat_id=job.chat_id, data=_msg_id,\n',
    f'{i_eb}    name="autodel_timeout_" + str(_msg_id)\n',
    f'{i_eb})\n',
    f'{i_e}except Exception as _ade:\n',
    f'{i_eb}print("[TIMEOUT AUTODEL ERR] " + str(_ade))\n',
]

# درج قبل از if _expire_del
lines = lines[:expire_idx] + autodel_block + lines[expire_idx:]
print(f"✅ بلوک تایمر 10 ثانیه‌ای درج شد ({len(autodel_block)} خط).")

# === نمایش ناحیه تغییر ===
print("\n=== ناحیه نهایی ===")
with open('modules/start.py', 'r', encoding='utf-8') as f:
    nl = f.readlines()

for i, line in enumerate(nl):
    if 'زمان استفاده' in line and 'text=' in line:
        for j in range(max(0, i-2), min(len(nl), i+18)):
            marker = " ⬅" if 'autodel_timeout_' in nl[j] else ""
            print(f"   {j+1}: {nl[j].rstrip()}{marker}")
        break

# === نوشتن ===
with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# === کامپایل ===
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# === ری‌استارت ===
print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 5 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تایمر 10 ثانیه‌ای اضافه شد!")
print("="*80)
print("\n📌 حالا پیام «زمان استفاده از پنل به پایان رسید» بعد از 10 ثانیه خودکار پاک می‌شود.")
print("📌 در هر شرایطی: گروه، پیوی، هر کاربری")
