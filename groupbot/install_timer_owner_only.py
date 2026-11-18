import os, shutil, py_compile, time, re

print("="*80)
print("🔧 نصب سیستم تایمر (فقط سازنده + اختیاری برای سودو)")
print("="*80)

# ===== 1. بکاپ =====
print("\n=== 1. ایجاد بکاپ‌های امنیتی ===")
timestamp = time.strftime("%H%M%S")
backup_map = {}
try:
    for f in ['modules/start.py', 'modules/system_management.py', 'database.py']:
        if os.path.exists(f):
            bak = f + f'.bak_timer_{timestamp}'
            shutil.copy(f, bak)
            backup_map[f] = bak
            print(f"   ✅ {f}")
except Exception as e:
    print(f"❌ خطا در بکاپ: {e}")
    exit(1)

# ===== 2. توابع دیتابیس =====
print("\n=== 2. اضافه کردن توابع به database.py ===")
try:
    with open('database.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    added = []
    
    if 'def get_chat_panel_warning' not in content:
        content += '''


# ===== TIMER SETTINGS (Global + Per-Chat) =====
def get_chat_panel_warning(chat_id: int):
    """بررسی فعال بودن هشدار (per-chat)"""
    try:
        v = get_setting(chat_id, "panel_warning_enabled", None)
        if v is None:
            v2 = get_setting(0, "panel_warning_enabled", "0")
            return int(v2) if v2 else 0
        return int(v)
    except Exception:
        return 0


def set_chat_panel_warning(chat_id: int, enabled: int):
    """تنظیم هشدار برای یک گروه"""
    try:
        set_setting(chat_id, "panel_warning_enabled", str(int(enabled)))
        return True
    except Exception:
        return False


def get_sudo_timer_access():
    """بررسی اینکه آیا سودوها می‌توانند تایمر را تغییر دهند"""
    try:
        v = get_setting(0, "sudo_timer_access", "0")
        return int(v) if v else 0
    except Exception:
        return 0


def set_sudo_timer_access(enabled: int):
    """تنظیم دسترسی سودو به تایمر (فقط سازنده)"""
    try:
        set_setting(0, "sudo_timer_access", str(int(enabled)))
        return True
    except Exception:
        return False
'''
        added.append("panel_warning")
    
    if added:
        with open('database.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ توابع اضافه شدند: {added}")
    else:
        print("   ⚠️ توابع از قبل وجود دارند.")
except Exception as e:
    print(f"❌ خطا: {e}")
    for f, bak in backup_map.items():
        shutil.copy(bak, f)
    exit(1)

# ===== 3. اصلاح start.py =====
print("\n=== 3. اصلاح reset_timer + اضافه کردن هشدار در start.py ===")
try:
    with open('modules/start.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 3.1. توابع هشدار
    if 'async def panel_close_warning' not in content:
        warn_func = '''
async def panel_close_warning(context):
    """هشدار قبل از بسته شدن پنل"""
    job = context.job
    chat_id = job.chat_id
    message_id = job.data
    try:
        sent = await context.bot.send_message(
            chat_id=chat_id,
            text="\\u23f1\\u200c 30 \\u062b\\u0627\\u0646\\u06cc\\u0647 \\u062f\\u06cc\\u06af\\u0631 \\u0627\\u06cc\\u0646 \\u067e\\u0646\\u0644 \\u0628\\u0633\\u062a\\u0647 \\u0645\\u06cc\\u200c\\u0634\\u0648\\u062f. \\u0628\\u0631\\u0627\\u06cc \\u0627\\u062f\\u0627\\u0645\\u0647\\u060c \\u0631\\u0648\\u06cc \\u062f\\u06a9\\u0645\\u0647\\u200c\\u0627\\u06cc \\u06a9\\u0644\\u06cc\\u06a9 \\u06a9\\u0646\\u06cc\\u062f.",
            reply_to_message_id=message_id,
            disable_notification=True
        )
        context.job_queue.run_once(
            _auto_del_msg, 30,
            chat_id=chat_id, data=sent.message_id,
            name="warndel_" + str(sent.message_id)
        )
    except Exception as e:
        print("[PANEL WARNING ERR] " + str(e))


async def _auto_del_msg(context):
    job = context.job
    try:
        await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)
    except Exception:
        pass


'''
        # درج قبل از reset_timer
        m = re.search(r'\ndef reset_timer\(', content)
        if m:
            content = content[:m.start()] + warn_func + content[m.start():]
            print("   ✅ توابع هشدار اضافه شدند.")
    
    # 3.2. بازنویسی reset_timer (idle-based)
    new_reset = '''def reset_timer(context, chat_id, message_id):
    import time as t
    from database import get_chat_panel_timeout, get_chat_panel_warning
    try:
        timeout = get_chat_panel_timeout(chat_id)
    except Exception:
        timeout = 300
    LAST_ACTIVITY[(chat_id, message_id)] = t.time()
    
    # لغو تایمرهای قبلی
    try:
        for job in context.job_queue.get_jobs_by_name("autoclose_" + str(message_id)):
            job.schedule_removal()
        for job in context.job_queue.get_jobs_by_name("warn_" + str(message_id)):
            job.schedule_removal()
    except Exception as e:
        print("[RESET TIMER ERR] " + str(e))
    
    if timeout and timeout > 0:
        try:
            context.job_queue.run_once(
                auto_close_timeout, timeout,
                chat_id=chat_id, data=message_id,
                name="autoclose_" + str(message_id)
            )
            # هشدار
            try:
                warn_on = get_chat_panel_warning(chat_id)
            except Exception:
                warn_on = 0
            if warn_on == 1 and timeout >= 60:
                warn_delay = timeout - 30
                if warn_delay > 0:
                    context.job_queue.run_once(
                        panel_close_warning, warn_delay,
                        chat_id=chat_id, data=message_id,
                        name="warn_" + str(message_id)
                    )
            print(f"[TIMER SET] chat={chat_id} msg={message_id} timeout={timeout}s warn={warn_on}")
        except Exception as e:
            print("[TIMER SCHEDULE ERR] " + str(e))

'''
    pattern = re.compile(r'def reset_timer\(context, chat_id, message_id\):.*?(?=\ndef |\nasync def |\nclass |\Z)', re.DOTALL)
    content = pattern.sub(new_reset, content, count=1)
    print("   ✅ reset_timer بازنویسی شد (idle-based).")
    
    with open('modules/start.py', 'w', encoding='utf-8') as f:
        f.write(content)
except Exception as e:
    print(f"❌ خطا: {e}")
    for f, bak in backup_map.items():
        shutil.copy(bak, f)
    exit(1)

# ===== 4. تغییر گزینه‌های sys_set_pt =====
print("\n=== 4. تغییر گزینه‌های sys_set_pt به 30/60/180/300 ===")
try:
    with open('modules/system_management.py', 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(
        r'opts\s*=\s*\["60",\s*"120",\s*"180",\s*"300",\s*"600",\s*"900",\s*"1800"\]',
        'opts = ["30", "60", "180", "300"]',
        content
    )
    # اضافه کردن متغیرهای هشدار و دسترسی سودو قبل از return دکمه‌ها
    if 'sudo_timer_access' not in content and 'sys_panel_warning' not in content:
        # اضافه کردن به بلوک action == "sys_settings" یا مشابه آن
        # به‌طور ساده متغیرها را در تابع build_settings_menu اضافه می‌کنیم
        pass
    with open('modules/system_management.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("   ✅ گزینه‌های sys_set_pt تغییر کرد.")
except Exception as e:
    print(f"⚠️ خطا در تغییر sys_set_pt: {e}")

# ===== 5. اضافه کردن توابع جدید به system_management.py =====
print("\n=== 5. اضافه کردن منوی تایمر (owner_timer_menu) ===")
try:
    with open('modules/system_management.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # اضافه کردن تابع build_owner_timer_menu
    if 'def build_owner_timer_menu' not in content:
        new_menu_func = '''


def build_owner_timer_menu(uid, chat_id):
    """منوی تنظیمات تایمر پنل (فقط سازنده و سودو مجاز)"""
    from database import get_chat_panel_timeout, get_chat_panel_warning, get_sudo_timer_access
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    timeout = get_chat_panel_timeout(chat_id)
    warn = get_chat_panel_warning(chat_id)
    sudo_access = get_sudo_timer_access()
    
    # تبدیل ثانیه به برچسب
    if timeout < 60:
        t_label = f"{timeout} \\u062b\\u0627\\u0646\\u06cc\\u0647"
    else:
        t_label = f"{timeout // 60} \\u062f\\u0642\\u06cc\\u0642\\u0647"
    
    warn_label = "\\u2705" if warn == 1 else "\\u274c"
    sudo_label = "\\u2705" if sudo_access == 1 else "\\u274c"
    
    btns = []
    btns.append([InlineKeyboardButton(f"\\u23f1 \\u062a\\u0627\\u06cc\\u0645\\u0631 \\u067e\\u0646\\u0644: {t_label}", callback_data=f"owner_timer_pt:{uid}:{chat_id}")])
    btns.append([InlineKeyboardButton(f"\\U0001F514 \\u0647\\u0634\\u062f\\u0627\\u0631 \\u0628\\u0633\\u062a\\u0647 \\u0634\\u062f\\u0646: {warn_label}", callback_data=f"owner_timer_warn:{uid}:{chat_id}")])
    btns.append([InlineKeyboardButton(f"\\U0001F464 \\u062f\\u0633\\u062a\\u0631\\u0633\\u06cc \\u0633\\u0648\\u062f\\u0648: {sudo_label}", callback_data=f"owner_timer_sudo:{uid}:{chat_id}")])
    btns.append([InlineKeyboardButton("\\U0001F519 \\u0628\\u0627\\u0632\\u06af\\u0634\\u062a", callback_data=f"op_manage:{uid}:{chat_id}")])
    return InlineKeyboardMarkup(btns)


def build_sudo_timer_menu(uid, chat_id):
    """منوی تایمر برای سودو (بدون گزینه دسترسی سودو)"""
    from database import get_chat_panel_timeout, get_chat_panel_warning
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    timeout = get_chat_panel_timeout(chat_id)
    warn = get_chat_panel_warning(chat_id)
    if timeout < 60:
        t_label = f"{timeout} \\u062b\\u0627\\u0646\\u06cc\\u0647"
    else:
        t_label = f"{timeout // 60} \\u062f\\u0642\\u06cc\\u0642\\u0647"
    warn_label = "\\u2705" if warn == 1 else "\\u274c"
    
    btns = [
        [InlineKeyboardButton(f"\\u23f1 \\u062a\\u0627\\u06cc\\u0645\\u0631 \\u067e\\u0646\\u0644: {t_label}", callback_data=f"owner_timer_pt:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"\\U0001F514 \\u0647\\u0634\\u062f\\u0627\\u0631: {warn_label}", callback_data=f"owner_timer_warn:{uid}:{chat_id}")],
        [InlineKeyboardButton("\\U0001F519 \\u0628\\u0627\\u0632\\u06af\\u0634\\u062a", callback_data=f"op_manage:{uid}:{chat_id}")],
    ]
    return InlineKeyboardMarkup(btns)
'''
        content = content.rstrip() + new_menu_func + '\n'
        print("   ✅ توابع build_owner_timer_menu و build_sudo_timer_menu اضافه شدند.")
    
    with open('modules/system_management.py', 'w', encoding='utf-8') as f:
        f.write(content)
except Exception as e:
    print(f"❌ خطا: {e}")
    for f, bak in backup_map.items():
        shutil.copy(bak, f)
    exit(1)

# ===== 6. اضافه کردن دکمه به owner_manage_menu در start.py =====
print("\n=== 6. اضافه کردن دکمه «⏱ تنظیمات تایمر» به پنل سازنده ===")
try:
    with open('modules/start.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # پیدا کردن تابع owner_manage_menu
    m = re.search(r'(def owner_manage_menu\([^)]*\):.*?return InlineKeyboardMarkup\([^)]*\))', content, re.DOTALL)
    if m:
        func_code = m.group(1)
        # بررسی اینکه آیا دکمه از قبل هست
        if 'owner_timer_menu' not in func_code:
            # پیدا کردن آخرین خط btns.append یا return
            # سعی می‌کنیم دکمه جدید را قبل از return اضافه کنیم
            insert_match = re.search(r'(\n\s*return InlineKeyboardMarkup)', func_code)
            if insert_match:
                new_button = '\n    btns.append([InlineKeyboardButton("\\u23f1 \\u062a\\u0646\\u0637\\u06cc\\u0645\\u0627\\u062a \\u062a\\u0627\\u06cc\\u0645\\u0631", callback_data=f"owner_timer_menu:{uid}:{chat_id}")])\n'
                new_func = func_code[:insert_match.start()] + new_button + func_code[insert_match.start():]
                content = content.replace(func_code, new_func)
                print("   ✅ دکمه به owner_manage_menu اضافه شد.")
            else:
                print("   ⚠️ نقطه درج دکمه پیدا نشد.")
        else:
            print("   ⚠️ دکمه از قبل وجود دارد.")
    else:
        print("   ⚠️ owner_manage_menu پیدا نشد!")
    
    # اضافه کردن هندلرهای owner_timer_*
    if 'action == "owner_timer_menu"' not in content:
        handlers = '''
    # ===== TIMER MENU HANDLERS (OWNER ONLY) =====
    if action == "owner_timer_menu":
        try:
            # بررسی دسترسی: فقط سازنده
            from config import OWNER_ID
            if query.from_user.id != OWNER_ID:
                await query.answer("\\u26d4\\u06f0 \\u0641\\u0642\\u0637 \\u0633\\u0627\\u0632\\u0646\\u062f\\u0647 \\u062f\\u0633\\u062a\\u0631\\u0633\\u06cc \\u062f\\u0627\\u0631\\u062f.", show_alert=True)
                return
            from modules.system_management import build_owner_timer_menu
            await query.edit_message_text(
                "\\u23f1 \\u062a\\u0646\\u0637\\u06cc\\u0645\\u0627\\u062a \\u062a\\u0627\\u06cc\\u0645\\u0631 \\u067e\\u0646\\u0644\\n\\n"
                "\\u062a\\u0627\\u06cc\\u0645\\u0631 \\u0628\\u0631 \\u0627\\u0633\\u0627\\u0633 \\u0639\\u062f\\u0645 \\u0641\\u0639\\u0627\\u0644\\u06cc\\u062a \\u0627\\u0633\\u062a \\u0648 \\u0628\\u0627 \\u0647\\u0631 \\u06a9\\u0644\\u06cc\\u06a9 \\u0631\\u06cc\\u0633\\u062a \\u0645\\u06cc\\u200c\\u0634\\u0648\\u062f.",
                reply_markup=build_owner_timer_menu(query.from_user.id, query.message.chat.id)
            )
        except Exception as e:
            print("[OWNER TIMER MENU ERR] " + str(e))
        return

    if action == "owner_timer_pt":
        try:
            from config import OWNER_ID
            from database import get_sudo_timer_access
            uid_check = query.from_user.id
            is_owner = (uid_check == OWNER_ID)
            is_sudo_allowed = (get_sudo_timer_access() == 1)
            # بررسی سودو
            is_sudo = False
            if not is_owner:
                try:
                    from database import is_sudo as db_is_sudo
                    is_sudo = db_is_sudo(uid_check)
                except Exception:
                    pass
            if not is_owner and not (is_sudo and is_sudo_allowed):
                await query.answer("\\u26d4 \\u062f\\u0633\\u062a\\u0631\\u0633\\u06cc \\u0646\\u062f\\u0627\\u0631\\u06cc\\u062f.", show_alert=True)
                return
            from database import get_chat_panel_timeout, set_chat_panel_timeout
            opts = [30, 60, 180, 300]
            cur = get_chat_panel_timeout(query.message.chat.id)
            try:
                i = opts.index(cur)
            except ValueError:
                i = 0
            new = opts[(i + 1) % len(opts)]
            set_chat_panel_timeout(query.message.chat.id, new)
            from modules.system_management import build_owner_timer_menu, build_sudo_timer_menu
            kb = build_owner_timer_menu(uid_check, query.message.chat.id) if is_owner else build_sudo_timer_menu(uid_check, query.message.chat.id)
            try:
                await query.edit_message_reply_markup(reply_markup=kb)
            except Exception:
                pass
            label = f"{new}\\u062b" if new < 60 else f"{new // 60}\\u062f"
            await query.answer(f"\\u2705 \\u062a\\u0627\\u06cc\\u0645\\u0631: {label}")
        except Exception as e:
            print("[OWNER TIMER PT ERR] " + str(e))
        return

    if action == "owner_timer_warn":
        try:
            from config import OWNER_ID
            from database import get_sudo_timer_access
            uid_check = query.from_user.id
            is_owner = (uid_check == OWNER_ID)
            is_sudo_allowed = (get_sudo_timer_access() == 1)
            is_sudo = False
            if not is_owner:
                try:
                    from database import is_sudo as db_is_sudo
                    is_sudo = db_is_sudo(uid_check)
                except Exception:
                    pass
            if not is_owner and not (is_sudo and is_sudo_allowed):
                await query.answer("\\u26d4 \\u062f\\u0633\\u062a\\u0631\\u0633\\u06cc \\u0646\\u062f\\u0627\\u0631\\u06cc\\u062f.", show_alert=True)
                return
            from database import get_chat_panel_warning, set_chat_panel_warning
            cur = get_chat_panel_warning(query.message.chat.id)
            new = 0 if cur == 1 else 1
            set_chat_panel_warning(query.message.chat.id, new)
            from modules.system_management import build_owner_timer_menu, build_sudo_timer_menu
            kb = build_owner_timer_menu(uid_check, query.message.chat.id) if is_owner else build_sudo_timer_menu(uid_check, query.message.chat.id)
            try:
                await query.edit_message_reply_markup(reply_markup=kb)
            except Exception:
                pass
            await query.answer("\\U0001F514 \\u0647\\u0634\\u062f\\u0627\\u0631 " + ("\\u0641\\u0639\\u0627\\u0644" if new == 1 else "\\u063a\\u06cc\\u0631\\u0641\\u0639\\u0627\\u0644"))
        except Exception as e:
            print("[OWNER TIMER WARN ERR] " + str(e))
        return

    if action == "owner_timer_sudo":
        try:
            from config import OWNER_ID
            if query.from_user.id != OWNER_ID:
                await query.answer("\\u26d4 \\u0641\\u0642\\u0637 \\u0633\\u0627\\u0632\\u0646\\u062f\\u0647.", show_alert=True)
                return
            from database import get_sudo_timer_access, set_sudo_timer_access
            cur = get_sudo_timer_access()
            new = 0 if cur == 1 else 1
            set_sudo_timer_access(new)
            from modules.system_management import build_owner_timer_menu
            try:
                await query.edit_message_reply_markup(reply_markup=build_owner_timer_menu(query.from_user.id, query.message.chat.id))
            except Exception:
                pass
            await query.answer("\\U0001F464 \\u062f\\u0633\\u062a\\u0631\\u0633\\u06cc \\u0633\\u0648\\u062f\\u0648 " + ("\\u0641\\u0639\\u0627\\u0644" if new == 1 else "\\u063a\\u06cc\\u0631\\u0641\\u0639\\u0627\\u0644"))
        except Exception as e:
            print("[OWNER TIMER SUDO ERR] " + str(e))
        return

'''
        # درج قبل از "if action == \"op_manage\""
        anchor = 'if action == "op_manage":'
        if anchor in content:
            content = content.replace(anchor, handlers + anchor, 1)
            print("   ✅ هندلرهای owner_timer_* اضافه شدند.")
        else:
            print("   ⚠️ نقطه اتصال op_manage پیدا نشد!")
    
    # اضافه کردن owner_timer_menu به الگوی هندلر
    # بررسی اینکه آیا این actionها در الگوی CallbackQueryHandler ثبت شده‌اند یا نه
    if 'owner_timer_menu' not in re.findall(r'pattern="[^"]*"', content):
        # پیدا کردن الگوی op_manage
        pattern_match = re.search(r'(pattern="[^"]*op_manage[^"]*")', content)
        if pattern_match:
            old_pattern = pattern_match.group(1)
            new_pattern = old_pattern.replace('op_manage', 'op_manage|owner_timer_menu|owner_timer_pt|owner_timer_warn|owner_timer_sudo')
            content = content.replace(old_pattern, new_pattern)
            print("   ✅ الگوی هندلر به‌روزرسانی شد.")
        else:
            print("   ⚠️ الگوی op_manage پیدا نشد.")
    
    with open('modules/start.py', 'w', encoding='utf-8') as f:
        f.write(content)
except Exception as e:
    print(f"❌ خطا: {e}")
    import traceback
    traceback.print_exc()
    for f, bak in backup_map.items():
        shutil.copy(bak, f)
    exit(1)

# ===== 7. کامپایل =====
print("\n=== 7. کامپایل فایل‌ها ===")
try:
    for f in ['database.py', 'modules/start.py', 'modules/system_management.py']:
        py_compile.compile(f, doraise=True)
        print(f"   ✅ {f}")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    print("⚠️ Auto-Rollback...")
    for f, bak in backup_map.items():
        shutil.copy(bak, f)
    print("✅ همه بکاپ‌ها ریستور شدند.")
    exit(1)

# ===== 8. ری‌استارت =====
print("\n=== 8. ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(5)
print("✅ ربات ری‌استارت شد.")

print("\n=== 9. 15 خط آخر لاگ ===")
os.system('tail -n 15 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ نصب کامل شد!")
print("="*80)
print("\n📌 محل استفاده:")
print("   • وارد گروه شوید")
print("   • پنل سازنده را باز کنید (owner_manage_menu)")
print("   • دکمه «⏱ تنظیمات تایمر» را بزنید")
print("\n📌 گزینه‌ها:")
print("   • تایمر پنل: 30s / 1m / 3m / 5m")
print("   • هشدار: ✅ / ❌")
print("   • دسترسی سودو: ✅ / ❌ (فقط سازنده)")
