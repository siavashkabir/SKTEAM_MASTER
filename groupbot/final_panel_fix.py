import os, shutil, py_compile, time

print("="*80)
print("🔧 اصلاح نهایی پنل تکراری (Guard + Register)")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/reply.py.bak_finalfix_{ts}'
shutil.copy('modules/reply.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/reply.py', 'r', encoding='utf-8') as f:
    content = f.read()

# === 1. اصلاح Guard: اضافه کردن return ===
old_guard = '''        if _old_panel:
            print(f"[PANEL GUARD] User {user.id} already has active panel msg={_old_panel}. Skipping.")
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=_old_panel)
            except Exception:
                pass
            try:
                del ACTIVE_PANELS[_key]
            except Exception:
                pass
    except Exception as _e:
        print("[PANEL GUARD ERR] " + str(_e))'''

new_guard = '''        if _old_panel:
            print(f"[PANEL GUARD] User {user.id} already has active panel msg={_old_panel}. Ignoring new request.")
            # کاربر پنل باز داره → فقط پیام "پنل" کاربر رو پاک کن و خارج شو
            try:
                await msg.delete()
            except Exception:
                pass
            return
    except Exception as _e:
        print("[PANEL GUARD ERR] " + str(_e))'''

if old_guard in content:
    content = content.replace(old_guard, new_guard)
    print("✅ Guard اصلاح شد (حالا return می‌ده).")
else:
    print("❌ Guard پیدا نشد!")
    shutil.copy(bak, 'modules/reply.py')
    exit(1)

# === 2. اضافه کردن Register بعد از reset_timer ===
old_reg = '''            reset_timer(context, sent.chat.id, sent.message_id)
        except Exception as e:
            print("[PANEL ERR] " + str(e))
            return'''

new_reg = '''            reset_timer(context, sent.chat.id, sent.message_id)
            # [PER-USER PANEL GUARD] ثبت پنل باز شده
            try:
                from modules.start import ACTIVE_PANELS
                ACTIVE_PANELS[(user.id, chat.id)] = sent.message_id
                print(f"[PANEL GUARD] Registered msg={sent.message_id} for user={user.id} chat={chat.id}")
            except Exception as _re:
                print("[PANEL GUARD REG ERR] " + str(_re))
        except Exception as e:
            print("[PANEL ERR] " + str(e))
            return'''

if old_reg in content:
    content = content.replace(old_reg, new_reg, 1)
    print("✅ Register اضافه شد.")
else:
    print("❌ محل reset_timer پیدا نشد!")
    shutil.copy(bak, 'modules/reply.py')
    exit(1)

with open('modules/reply.py', 'w', encoding='utf-8') as f:
    f.write(content)

# === نمایش ناحیه تغییر ===
print("\n=== ناحیه تغییر ===")
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'PANEL GUARD' in line and 'Ignore' in line:
        for j in range(max(0, i-2), min(len(lines), i+12)):
            print(f"   {j+1}: {lines[j]}")
        break

print("\n---")
for i, line in enumerate(lines):
    if 'PANEL GUARD] Registered' in line:
        for j in range(max(0, i-5), min(len(lines), i+5)):
            print(f"   {j+1}: {lines[j]}")
        break

# === کامپایل ===
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/reply.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/reply.py')
    exit(1)

# === ری‌استارت ===
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 8 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ اصلاح شد!")
print("="*80)
