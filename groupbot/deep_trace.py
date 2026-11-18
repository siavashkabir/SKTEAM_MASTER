import os, re, glob
from collections import defaultdict

print("="*80)
print("🔍 ردیاب عمیق منوها (شاخه به شاخه)")
print("="*80)

# ============================================================
# 1. جمع‌آوری همه فایل‌ها
# ============================================================
all_files = {}
for f in ['modules/start.py', 'modules/owner_set_group.py', 'modules/system_management.py',
          'modules/anti_raid.py', 'modules/anti_bot.py', 'modules/no_photo_cleanup.py',
          'modules/vague_name_cleanup.py', 'modules/locks.py', 'modules/media.py',
          'modules/modes.py', 'modules/welcome.py', 'modules/nsfw.py', 'modules/warn.py',
          'modules/purge.py', 'modules/link.py', 'modules/owner_guide.py',
          'modules/subs_menu.py', 'modules/remote_groups.py', 'modules/force_join.py',
          'modules/games_menu.py', 'modules/system_info.py', 'modules/ai_management.py',
          'modules/notifications.py', 'modules/user_contacts.py',
          'modules/owner_panel_trigger.py', 'modules/pv_main.py']:
    if os.path.exists(f):
        try:
            with open(f, 'r', encoding='utf-8') as file:
                all_files[f] = file.readlines()
        except:
            pass

# ============================================================
# 2. استخراج توابع منو
# ============================================================
MENU_FUNCS = {}  # func_name -> (file, start_line)

for fname, lines in all_files.items():
    for i, line in enumerate(lines):
        # تابع‌هایی که menu یا panel یا _kb توشه
        m = re.match(r'^def\s+(\w*(?:menu|panel|_kb|_keyboard)\w*)\s*\(', line)
        if m:
            func_name = m.group(1)
            if func_name not in MENU_FUNCS:
                MENU_FUNCS[func_name] = (fname, i+1)

print(f"📊 {len(MENU_FUNCS)} تابع منو پیدا شد")

# ============================================================
# 3. استخراج دکمه‌های یک تابع
# ============================================================
def get_buttons(lines, start):
    """استخراج دکمه‌ها با (label, callback, line_num)"""
    buttons = []
    # پیدا کردن انتهای تابع
    end = len(lines)
    for j in range(start+1, len(lines)):
        if lines[j].startswith('def ') or lines[j].startswith('async def '):
            end = j
            break
    
    for k in range(start, end):
        line = lines[k]
        if 'InlineKeyboardButton' not in line:
            continue
        
        label = '?'
        cb = None
        
        # label
        m1 = re.search(r'InlineKeyboardButton\(["\']([^"\']+)["\']', line)
        if m1:
            label = m1.group(1)[:40]
        
        # callback
        m2 = re.search(r'callback_data=["\']([^"\']+)["\']', line)
        if m2:
            cb = m2.group(1)
        else:
            m3 = re.search(r'callback_data=f["\']([^"\']+)["\']', line)
            if m3:
                cb = m3.group(1)
        
        # اگه چند خطی بود، شاید تو خط بعد
        if not cb:
            for k2 in range(k, min(k+3, end)):
                m = re.search(r'callback_data=["\']([^"\']+)["\']', lines[k2])
                if m:
                    cb = m.group(1)
                    break
        
        if cb:
            cb_norm = cb.split(':')[0] if ':' in cb else cb
            buttons.append((label, cb_norm, cb, k+1))
    
    return buttons, end

# ============================================================
# 4. استخراج handlerها
# ============================================================
HANDLERS = defaultdict(list)  # action -> [(file, line, reply_markup_func, button_label)]

for fname, lines in all_files.items():
    for i, line in enumerate(lines):
        m = re.match(r'\s*if action == ["\']([^"\']+)["\']', line)
        if not m:
            continue
        
        action = m.group(1)
        
        # پیدا کردن انتهای handler
        end = len(lines)
        for j in range(i+1, len(lines)):
            if re.match(r'\s*if action', lines[j]) or lines[j].startswith('def ') or lines[j].startswith('async def '):
                end = j
                break
        
        # استخراج reply_markup
        reply_markup = None
        text = None
        for k in range(i, end):
            m2 = re.search(r'reply_markup=(\w+)\s*\(', lines[k])
            if m2 and not reply_markup:
                reply_markup = m2.group(1)
            
            # متن پیام
            if not text:
                m3 = re.search(r'["\']([^"\']{5,50})["\']', lines[k])
                if m3 and 'بازگشت' not in m3.group(1) and 'بستن' not in m3.group(1):
                    text = m3.group(1)
        
        HANDLERS[action].append({
            'file': fname,
            'line': i+1,
            'end': end,
            'reply_markup': reply_markup,
            'text': text[:40] if text else '?'
        })

print(f"📊 {len(HANDLERS)} handler پیدا شد")

# ============================================================
# 5. ردیابی بازگشتی
# ============================================================
visited_globally = set()
trace_output = []

def trace_menu(menu_name, depth=0, parent_cb=None):
    """ردیابی بازگشتی یک منو"""
    indent = '  ' * depth
    line_prefix = '│  ' * depth
    
    if menu_name in visited_globally:
        return
    
    if menu_name not in MENU_FUNCS:
        return
    
    visited_globally.add(menu_name)
    
    fname, start_line = MENU_FUNCS[menu_name]
    lines = all_files[fname]
    buttons, end = get_buttons(lines, start_line - 1)
    
    # شمارش دکمه‌های back و close
    back_btns = [(l, cb) for l, cb, orig, ln in buttons if 'بازگشت' in l or 'back' in cb.lower()]
    close_btns = [(l, cb) for l, cb, orig, ln in buttons if 'بستن' in l or 'close' in cb.lower()]
    other_btns = [(l, cb, orig, ln) for l, cb, orig, ln in buttons if (l, cb) not in back_btns and (l, cb) not in close_btns]
    
    print(f"\n{line_prefix}┌─ 🪟 {menu_name}")
    print(f"{line_prefix}│  📄 {fname}:{start_line}")
    print(f"{line_prefix}│  🔘 {len(buttons)} دکمه (بازگشت: {len(back_btns)} | بستن: {len(close_btns)} | دیگر: {len(other_btns)})")
    
    # اطلاعات بازگشت
    if back_btns:
        for lbl, cb in back_btns:
            # کجا می‌ره؟
            if cb in HANDLERS:
                h = HANDLERS[cb][0]
                dest = h['reply_markup'] if h['reply_markup'] else '?'
                print(f"{line_prefix}│  🔙 بازگشت ({cb}) → {dest} [{h['file']}:{h['line']}]")
            else:
                print(f"{line_prefix}│  🔙 بازگشت ({cb}) → ❌ handler نداره!")
    else:
        print(f"{line_prefix}│  ⚠️ بازگشت نداره!")
    
    # اطلاعات بستن
    if close_btns:
        for lbl, cb in close_btns:
            print(f"{line_prefix}│  ❌ بستن ({cb})")
    else:
        print(f"{line_prefix}│  ⚠️ بستن نداره!")
    
    # زیرمنوها
    if other_btns and depth < 2:
        print(f"{line_prefix}│")
        for lbl, cb, orig, ln in other_btns[:10]:  # حداکثر ۱۰ تا
            # چک: آیا به یه منو می‌ره؟
            if cb in HANDLERS:
                h = HANDLERS[cb][0]
                dest = h['reply_markup'] if h['reply_markup'] else None
                
                if dest and dest in MENU_FUNCS:
                    # این یه زیرمنو هست
                    print(f"{line_prefix}│  🔘 {lbl}")
                    print(f"{line_prefix}│     → {dest} [{h['file']}:{h['line']}]")
                    if dest not in visited_globally:
                        trace_menu(dest, depth+1, cb)
                else:
                    # عملیات مستقیم
                    dest_str = dest if dest else h['text']
                    print(f"{line_prefix}│  🔘 {lbl} → {dest_str}")
            else:
                print(f"{line_prefix}│  🔘 {lbl} ({cb}) → ❌ handler نداره!")
    
    print(f"{line_prefix}└─")

# ============================================================
# 6. شروع از منوی اصلی سازنده
# ============================================================
print("\n" + "="*80)
print("🎯 شروع از منوی اصلی سازنده (sudo_panel_menu)")
print("="*80)

visited_globally.clear()
if 'sudo_panel_menu' in MENU_FUNCS:
    trace_menu('sudo_panel_menu', 0)

# ============================================================
# 7. منوی مالک گروه
# ============================================================
print("\n" + "="*80)
print("🎯 منوی مالک گروه (group_owner_panel_menu)")
print("="*80)

visited_globally.clear()
if 'group_owner_panel_menu' in MENU_FUNCS:
    trace_menu('group_owner_panel_menu', 0)

print("\n" + "="*80)
print("✅ ردیابی کامل شد (بدون تغییر)")
print("="*80)
