import os, shutil, py_compile, time, re

print("="*80)
print("🔧 حذف کامل وابستگی به RAM در سیستم تمدید")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_noram_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

# === 1. تغییر کالبک دکمه‌های تأیید و رد ===
old_confirm_btn = 'callback_data=f"osub_confirm:0:{req_id}"'
new_confirm_btn = 'callback_data=f"osub_confirm:0:{uid}:{req_chat_id}:{sub_type}:{dur}:{price}"'

old_reject_btn = 'callback_data=f"osub_reject:0:{req_id}"'
new_reject_btn = 'callback_data=f"osub_reject:0:{uid}:{req_chat_id}"'

if old_confirm_btn in content:
    content = content.replace(old_confirm_btn, new_confirm_btn)
    print("✅ دکمه تأیید اصلاح شد.")
else:
    print("⚠️ دکمه تأیید پیدا نشد، جستجو با regex...")
    content = re.sub(
        r'callback_data=f"osub_confirm:0:\{req_id\}"',
        'callback_data=f"osub_confirm:0:{uid}:{req_chat_id}:{sub_type}:{dur}:{price}"',
        content
    )

if old_reject_btn in content:
    content = content.replace(old_reject_btn, new_reject_btn)
    print("✅ دکمه رد اصلاح شد.")

# === 2. حذف بخش PENDING_RENEWALS از osub_inv_dur ===
# پیدا کردن و حذف خطوطی که PENDING_RENEWALS[req_id] = {...} را می‌سازند
old_pending_block = '''        req_id = f"{uid}_{int(_t.time())}"
        PENDING_RENEWALS[req_id] = {
            "requester": uid,
            "requester_name": query.from_user.full_name,
            "requester_username": query.from_user.username or "-",
            "chat_id": req_chat_id,
            "sub_type": sub_type,
            "days": dur,
            "price": price,
        }'''

new_pending_block = '''        req_id = f"{uid}_{int(_t.time())}"'''

if old_pending_block in content:
    content = content.replace(old_pending_block, new_pending_block)
    print("✅ ذخیره در RAM حذف شد.")
else:
    print("⚠️ بلوک PENDING_RENEWALS پیدا نشد، جستجو با regex...")
    content = re.sub(
        r'PENDING_RENEWALS\[req_id\] = \{.*?\}',
        '# (RAM storage removed)',
        content, count=1, flags=re.DOTALL
    )
    print("✅ با regex حذف شد.")

# === 3. بازنویسی هندلر osub_confirm ===
print("\n=== بازنویسی هندلر تأیید ===")
start_idx = None
for i, line in enumerate(content.split('\n')):
    if 'if action.startswith("osub_confirm:")' in line:
        start_idx = i
        break

if start_idx is None:
    print("❌ هندلر osub_confirm پیدا نشد!")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

lines = content.split('\n')

# پیدا کردن انتهای هندلر (اولین if action یا # ==== در سطح 4 فاصله)
end_idx = None
for j in range(start_idx + 1, len(lines)):
    if lines[j].startswith('    if action') or lines[j].startswith('    if action.startswith') or lines[j].startswith('    # ====='):
        end_idx = j
        break

if end_idx is None:
    end_idx = start_idx + 50

print(f"📍 هندلر از خط {start_idx+1} تا {end_idx}")

new_handler = '''    if action.startswith("osub_confirm:"):
        try:
            if len(parts) < 7:
                await query.answer("❌ اطلاعات دکمه ناقص است.", show_alert=True)
                return
            req_uid = int(parts[2])
            req_chat_id = int(parts[3])
            sub_type = parts[4]
            days = int(parts[5])
            price = int(parts[6])
        except Exception as e:
            print("[CONFIRM PARSE ERR] " + str(e))
            await query.answer("❌ خطا در خواندن اطلاعات.", show_alert=True)
            return
        
        try:
            from database import extend_subscription
            new_exp, total_days, was_active = extend_subscription(req_chat_id, sub_type, days)
            print(f"[RENEW OK] {sub_type} +{days}d for chat {req_chat_id} => {new_exp}")
        except Exception as e:
            print("[CONFIRM ERR] " + str(e))
            try:
                await query.answer("❌ خطا در تمدید اشتراک", show_alert=True)
            except Exception:
                pass
            return
        
        type_fa = {"manager": "مدیر", "nsfw": "NSFW", "vcall": "ویس‌کال", "music": "موزیک"}.get(sub_type, sub_type)
        
        # ارسال پیام تأیید به پیوی مالک گروه
        try:
            await context.bot.send_message(
                chat_id=req_uid,
                text=(
                    f"✅ درخواست تمدید شما تأیید شد!\\n\\n"
                    f"📌 نوع: {type_fa}\\n"
                    f"📅 مدت افزوده شده: {days} روز\\n"
                    f"⏰ انقضای جدید: {new_exp}"
                )
            )
            print(f"[NOTIFY SENT] to user {req_uid}")
        except Exception as e:
            print("[NOTIFY REQ ERR] " + str(e))
        
        try:
            await query.edit_message_text(
                f"✅ درخواست تأیید شد.\\n\\n"
                f"📌 نوع: {type_fa}\\n"
                f"📅 {days} روز اضافه شد.\\n"
                f"⏰ انقضای جدید: {new_exp}"
            )
        except Exception:
            pass
        return

    if action.startswith("osub_reject:"):
        try:
            if len(parts) < 4:
                await query.answer("❌ خطا", show_alert=True)
                return
            req_uid = int(parts[2])
            req_chat_id = int(parts[3])
        except Exception:
            await query.answer("❌ خطا", show_alert=True)
            return
        
        try:
            await context.bot.send_message(
                chat_id=req_uid,
                text="❌ درخواست تمدید شما توسط سازنده رد شد."
            )
        except Exception:
            pass
        
        await query.edit_message_text("❌ درخواست رد شد.")
        return

'''

new_lines = lines[:start_idx] + [new_handler] + lines[end_idx:]

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("✅ هندلر تأیید بازنویسی شد.")

# === 4. کامپایل ===
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 8 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ وابستگی به RAM حذف شد! حالا اطلاعات در خود دکمه ذخیره می‌شود.")
print("="*80)
