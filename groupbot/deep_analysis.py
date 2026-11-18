import os, re

print("="*80)
print("📊 تحلیل عمیق: کالبک‌های گمشده در کدام فایل هستن؟")
print("="*80)

# ============================================================
# 1. لیست کالبک‌های گمشده (از تحلیل قبلی)
# ============================================================
missing_callbacks = {
    # منوی تنظیمات گروه (owner_settings_menu)
    'menu_locks': '🔒 قفل‌های اصلی',
    'menu_media': '📸 قفل رسانه',
    'menu_modes': '🔄 حالت گروه',
    'welcome_menu': '👋 خوش‌آمدگویی',
    'nsfw_menu': '⑱ NSFW',
    'warnset_menu': '⚠️ تنظیمات اخطار',
    'purge_menu': '🧹 پاکسازی گروه',
    'link_menu': '🔗 لینک گروه',
    'nphoto_panel': '📸 کیک بدون عکس',
    'vague_panel': '❓ کیک اسم مبهم',
    # منوی اصلی مالک گروه
    'owner_readme': '📖 راهنمای کامل',
    'owner_set_group': '⚙️ تنظیمات این گروه',
    'sys_menu': '🖥 مدیریت سیستم',
    # منوی سازنده
    'owner_section_back': '🔙 بازگشت (بخش سازنده)',
    'owner_section_menu': '🔧 بخش سازنده',
    'op_botadmins': '👤 مدیریت ادمین‌های ربات',
    'rmt_groups': '🌐 مدیریت گروه‌ها',
    's_fj_menu': '🔒 جوین اجباری',
    's_op_sudo_stats': '📊 آمار سودوها',
    's_op_group_stats': '📈 آمار گروه‌ها',
}

# ============================================================
# 2. اسکن تمام فایل‌ها
# ============================================================
print("\n" + "="*80)
print("🔍 اسکن تمام فایل‌های modules و فایل‌های اصلی")
print("="*80)

# لیست فایل‌ها
files_to_scan = []

# main files
for f in ['main.py', 'config.py', 'database.py']:
    if os.path.exists(f):
        files_to_scan.append(f)

# modules
for f in os.listdir('modules'):
    if f.endswith('.py') and '.bak' not in f:
        files_to_scan.append(f'modules/{f}')

# ============================================================
# 3. برای هر callback گمشده، جستجو کن
# ============================================================
print("\n" + "="*80)
print("📋 گزارش تفصیلی: هر callback در کدام فایل‌ها پیدا شد؟")
print("="*80)

for cb, label in missing_callbacks.items():
    print(f"\n┌─ {label} ({cb})")
    
    found_in = []
    for fpath in files_to_scan:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except:
            continue
        
        for i, line in enumerate(lines):
            # handler
            if f'action == "{cb}"' in line:
                found_in.append((fpath, i+1, 'HANDLER', line.strip()[:90]))
            # در pattern
            if f'pattern=' in line and f'"{cb}' in line:
                found_in.append((fpath, i+1, 'PATTERN', line.strip()[:90]))
            # تعریف دکمه
            if f'callback_data="{cb}:' in line or f'callback_data="{cb}"' in line or f'callback_data=f"{cb}' in line:
                found_in.append((fpath, i+1, 'BUTTON', line.strip()[:90]))
    
    if not found_in:
        print(f"│  ❌ هیچ جا پیدا نشد!")
    else:
        for fpath, line_num, kind, code in found_in:
            emoji = '✅' if kind == 'HANDLER' else ('📍' if kind == 'PATTERN' else '🔘')
            print(f"│  {emoji} [{kind}] {fpath}:{line_num}")
            print(f"│     {code}")

# ============================================================
# 4. اسکن: چه کالبک‌هایی در owner_set_group.py هستن؟
# ============================================================
print("\n" + "="*80)
print("🔍 handlerهایی که در owner_set_group.py هستن")
print("="*80)

if os.path.exists('modules/owner_set_group.py'):
    with open('modules/owner_set_group.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        m = re.search(r'action == ["\']([^"\']+)["\']', line)
        if m:
            print(f"   ✅ خط {i+1}: {m.group(1)}")
    
    # pattern
    for i, line in enumerate(lines):
        if 'pattern=' in line and ('owner_set_' in line or 'menu_' in line or 'timer_' in line):
            print(f"\n   📍 PATTERN (خط {i+1}): {line.strip()[:140]}")

# ============================================================
# 5. اسکن: چه کالبک‌هایی در ماژول‌های جداگانه هستن؟
# ============================================================
print("\n" + "="*80)
print("🔍 handlerها در ماژول‌های مرتبط")
print("="*80)

module_targets = {
    'locks.py': ['menu_locks'],
    'media.py': ['menu_media'],
    'modes.py': ['menu_modes'],
    'welcome.py': ['welcome_menu'],
    'nsfw.py': ['nsfw_menu'],
    'warn.py': ['warnset_menu'],
    'purge.py': ['purge_menu'],
    'link.py': ['link_menu'],
    'no_photo_cleanup.py': ['nphoto_panel'],
    'vague_name_cleanup.py': ['vague_panel'],
    'system_management.py': ['sys_menu', 's_backup', 's_restart_bot'],
    'owner_set_group.py': ['owner_set_group'],
    'owner_guide.py': ['owner_readme', 'owner_section_back'],
    'subs_menu.py': ['sub_manage'],
    'remote_groups.py': ['rmt_groups'],
    'force_join.py': ['s_fj_menu'],
}

for mod_name, targets in module_targets.items():
    fpath = f'modules/{mod_name}'
    if not os.path.exists(fpath):
        continue
    
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    found = []
    for i, line in enumerate(lines):
        for t in targets:
            if f'action == "{t}"' in line:
                found.append((t, i+1))
    
    if found:
        print(f"\n   📄 {mod_name}:")
        for t, ln in found:
            print(f"      ✅ {t} (خط {ln})")
    
    # pattern
    for i, line in enumerate(lines):
        if 'pattern=' in line:
            # استخراج
            m = re.search(r'pattern=["\']([^"\']+)["\']', line)
            if m:
                pat = m.group(1)
                for t in targets:
                    if t in pat or t.split('_')[0] in pat:
                        print(f"      📍 PATTERN (خط {i+1}): {pat[:120]}")
                        break

# ============================================================
# 6. دستور نهایی: کدوم فایل باید اصلاح بشه؟
# ============================================================
print("\n" + "="*80)
print("🎯 خلاصه نهایی: کجاها باید اصلاح بشه؟")
print("="*80)

files_to_fix = set()
for cb in missing_callbacks:
    for fpath in files_to_scan:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue
        if f'"{cb}"' in content or f"'{cb}'" in content:
            files_to_fix.add(fpath)

print(f"\n📁 فایل‌هایی که این کالبک‌ها رو دارن (باید چک بشن):")
for f in sorted(files_to_fix):
    print(f"   • {f}")

# ============================================================
# 7. اسکن pattern‌های موجود در start.py
# ============================================================
print("\n" + "="*80)
print("🎯 تمام pattern‌های ثبت‌شده در start.py")
print("="*80)

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'add_handler' in line and 'pattern=' in line:
        m = re.search(r'pattern=["\']([^"\']+)["\']', line)
        if m:
            pat = m.group(1)
            print(f"\n   📍 خط {i+1}:")
            # شمارش تعداد کالبک در pattern
            parts = pat.replace('^(', '').replace(')$', '').split('|')
            print(f"      {len(parts)} کالبک")
            # چک: چه چیزهای گمشده‌ای اینجا هستن
            for cb in missing_callbacks:
                if cb in parts:
                    print(f"      ✅ {cb}")
