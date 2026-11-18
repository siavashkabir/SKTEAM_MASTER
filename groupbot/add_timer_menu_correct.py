import os, shutil, py_compile, time

print("="*80)
print("🔧 اضافه کردن منوی تایمر با اسم صحیح توابع")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/owner_set_group.py.bak_tmenu_{ts}'
shutil.copy('modules/owner_set_group.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/owner_set_group.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ===== 1. اضافه کردن دکمه new_timer_menu به _build_menu =====
print("\n=== STEP 1: اضافه کردن دکمه به _build_menu ===")
try:
    # پیدا کردن خط دکمه owner_set_pt
    old_pt_line = '        [InlineKeyboardButton(f"⏳ انقضای پنل: {_fmt_sec(pt)}", callback_data=f"owner_set_pt:{uid}:{chat_id}")],\n'
    
    if old_pt_line not in content:
        # تلاش با فاصله‌های متفاوت
        import re
        pattern = r'(\s*)\[InlineKeyboardButton\(f"[^"]*[^"]*\{_fmt_sec\(pt\)\}"[^\]]*owner_set_pt[^\]]*\)\],'
        match = re.search(pattern, content)
        if match:
            old_pt_line = match.group(0)
            print(f"   ✅ خط پیدا شد (با regex)")
        else:
            print("   ❌ خط owner_set_pt پیدا نشد!")
            shutil.copy(bak, 'modules/owner_set_group.py')
            exit(1)
    
    # پیدا کردن دقیق‌تر: خطوطی که include می‌کنند owner_set_cd, owner_set_del, owner_set_pt, owner_set_ed
    # این 4 خط باید از منو حذف بشن و به جای همه، یک دکمه جدید بیاد
    
    lines_to_remove = []
    for kw in ['owner_set_cd:', 'owner_set_del:', 'owner_set_pt:', 'owner_set_ed:']:
        for line in content.split('\n'):
            if kw in line and 'InlineKeyboardButton' in line:
                if line not in lines_to_remove:
                    lines_to_remove.append(line)
    
    print(f"   📋 {len(lines_to_remove)} خط تایمر برای حذف پیدا شد.")
    
    # برای هر خط، حذف از content
    for line in lines_to_remove:
        content = content.replace(line + '\n', '')
        content = content.replace(line, '')
    
    print(f"   ✅ خطوط تایمر حذف شدند.")
    
    # اضافه کردن یک دکمه جدید به جای آنها
    # بهترین جا: قبل از دکمه owner_set_ai_on
    ai_anchor = '        [InlineKeyboardButton(f"🤖 پاسخ هوشمند:'
    if ai_anchor not in content:
        # تلاش با regex
        import re
        ai_match = re.search(r'(\s*)\[InlineKeyboardButton\(f"🤖[^\]]*owner_set_ai_on[^\]]*\)\],', content)
        if ai_match:
            ai_anchor = ai_match.group(0)
        else:
            # از دکمه Anti-Raid استفاده کن
            ai_anchor = '        [InlineKeyboardButton("🛡 Anti-Raid"'
            if ai_anchor not in content:
                print("   ⚠️ نقطه درج پیدا نشد. اضافه نمی‌کنم.")
                ai_anchor = None
    
    if ai_anchor:
        indent = ' ' * (len(ai_anchor) - len(ai_anchor.lstrip()))
        new_button = f'{indent}[InlineKeyboardButton("⏱ تنظیمات تایمر", callback_data=f"timer_menu:{{uid}}:{{chat_id}}")],\n'
        content = content.replace(ai_anchor, new_button + ai_anchor, 1)
        print("   ✅ دکمه جدید اضافه شد.")
    
    print("✅ STEP 1 تمام شد.")
    
except Exception as e:
    print(f"❌ خطا: {e}")
    import traceback
    traceback.print_exc()
    shutil.copy(bak, 'modules/owner_set_group.py')
    exit(1)

# ===== 2. اضافه کردن تابع _build_timer_menu قبل از _build_menu =====
print("\n=== STEP 2: اضافه کردن تابع _build_timer_menu ===")
try:
    timer_func = '''
def _build_timer_menu(uid, chat_id):
    """منوی متمرکز تنظیمات تایمر"""
    cd = get_chat_cooldown(chat_id)
    pd = get_chat_panel_delete(chat_id)
    pt = get_chat_panel_timeout(chat_id)
    ed = get_chat_expire_delete(chat_id)
    try:
        from database import get_chat_panel_warning
        warn = get_chat_panel_warning(chat_id)
    except Exception:
        warn = 0
    warn_icon = "✅" if warn == 1 else "❌"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⏰ Cooldown: {_fmt_sec(cd)}", callback_data=f"owner_set_cd:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🗑 حذف پنل: {_fmt_sec(pd)}", callback_data=f"owner_set_del:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⏳ انقضای پنل: {_fmt_sec(pt)}", callback_data=f"owner_set_pt:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"💬 حذف پیام expire: {_fmt_sec(ed)}", callback_data=f"owner_set_ed:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🔔 هشدار بسته شدن: {warn_icon}", callback_data=f"owner_set_warn:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"timer_back:{uid}:{chat_id}")],
    ])


'''
    anchor = 'def _build_menu(uid, chat_id):'
    if anchor in content:
        content = content.replace(anchor, timer_func + anchor, 1)
        print("   ✅ تابع _build_timer_menu اضافه شد.")
    else:
        print("   ❌ anchor _build_menu پیدا نشد!")
        shutil.copy(bak, 'modules/owner_set_group.py')
        exit(1)
    print("✅ STEP 2 تمام شد.")
except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak, 'modules/owner_set_group.py')
    exit(1)

# ===== 3. اضافه کردن ۳ هندلر جدید قبل از owner_set_pt =====
print("\n=== STEP 3: اضافه کردن هندلرهای جدید ===")
try:
    new_handlers = '''    if action == "timer_menu":
        try:
            await _safe_edit(query, "⏱ تنظیمات تایمر\\n\\nتایمر بر اساس عدم فعالیت است.", reply_markup=_build_timer_menu(uid, chat_id))
        except Exception as e:
            print("[TIMER MENU ERR] " + str(e))
        return

    if action == "timer_back":
        try:
            await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))
        except Exception as e:
            print("[TIMER BACK ERR] " + str(e))
        return

    if action == "owner_set_warn":
        try:
            from database import get_chat_panel_warning, set_chat_panel_warning
            cur = get_chat_panel_warning(chat_id)
            new = 0 if cur == 1 else 1
            set_chat_panel_warning(chat_id, new)
            try:
                await _safe_edit(query, "⏱ تنظیمات تایمر", reply_markup=_build_timer_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer("🔔 هشدار " + ("فعال" if new == 1 else "غیرفعال"))
        except Exception as e:
            print("[WARN ERR] " + str(e))
        return

'''
    anchor = '    if action == "owner_set_pt":'
    if anchor in content:
        content = content.replace(anchor, new_handlers + anchor, 1)
        print("   ✅ ۳ هندلر جدید اضافه شد.")
    else:
        print("   ❌ anchor owner_set_pt پیدا نشد!")
        shutil.copy(bak, 'modules/owner_set_group.py')
        exit(1)
    print("✅ STEP 3 تمام شد.")
except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak, 'modules/owner_set_group.py')
    exit(1)

# ===== 4. نوشتن فایل و کامپایل =====
print("\n=== STEP 4: نوشتن و کامپایل ===")
try:
    with open('modules/owner_set_group.py', 'w', encoding='utf-8') as f:
        f.write(content)
    py_compile.compile('modules/owner_set_group.py', doraise=True)
    print("✅ فایل ذخیره و کامپایل شد.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/owner_set_group.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ===== 5. اضافه کردن توابع DB (اگر گم شده باشند) =====
print("\n=== STEP 5: بررسی توابع DB ===")
try:
    with open('database.py', 'r', encoding='utf-8') as f:
        db_content = f.read()
    
    if 'def get_chat_panel_warning' not in db_content:
        db_new = '''


def get_chat_panel_warning(chat_id):
    try:
        v = get_setting(chat_id, "panel_warning_enabled", None)
        if v is None:
            return int(get_setting(0, "panel_warning_enabled", "0") or 0)
        return int(v)
    except Exception:
        return 0


def set_chat_panel_warning(chat_id, enabled):
    try:
        set_setting(chat_id, "panel_warning_enabled", str(int(enabled)))
        return True
    except Exception:
        return False
'''
        with open('database.py', 'a', encoding='utf-8') as f:
            f.write(db_new)
        print("   ✅ توابع هشدار به database.py اضافه شدند.")
    else:
        print("   ⚠️ توابع از قبل وجود دارند.")
    
    py_compile.compile('database.py', doraise=True)
    print("✅ database.py کامپایل شد.")
except Exception as e:
    print(f"❌ خطا: {e}")

# ===== 6. به‌روزرسانی الگوی هندلر در start.py =====
print("\n=== STEP 6: به‌روزرسانی الگوی هندلر در start.py ===")
try:
    with open('modules/start.py', 'r', encoding='utf-8') as f:
        scontent = f.read()
    
    if 'timer_menu' not in scontent:
        # پیدا کردن الگوی owner_set_cd
        old_pat = 'owner_set_cd|owner_set_del'
        if old_pat in scontent:
            scontent = scontent.replace(old_pat, 'timer_menu|timer_back|owner_set_warn|owner_set_cd|owner_set_del', 1)
            with open('modules/start.py', 'w', encoding='utf-8') as f:
                f.write(scontent)
            print("   ✅ الگوی هندلر به‌روزرسانی شد.")
        else:
            print("   ⚠️ الگوی owner_set_cd|owner_set_del پیدا نشد.")
    else:
        print("   ⚠️ timer_menu از قبل وجود دارد.")
    
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ start.py کامپایل شد.")
except Exception as e:
    print(f"⚠️ خطا: {e}")

# ===== 7. ری‌استارت =====
print("\n=== STEP 7: ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(5)
print("✅ ربات ری‌استارت شد.")

os.system('tail -n 15 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ کار تمام شد! الان برو به «تنظیمات این گروه» و «⏱ تنظیمات تایمر» را بزن.")
print("="*80)
