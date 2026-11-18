#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ فاز ۱ — پنل دسترسی — $(date)"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. access.py — کل تابع build_access_menu (خط 85-160) ═══"
sed -n '85,160p' modules/access.py
echo ""

echo "═══ ۲. access.py — access_handler (خط 159-238) ═══"
sed -n '159,238p' modules/access.py
echo ""

echo "═══ ۳. access.py — access_cb_handler (خط 238-335) ═══"
sed -n '238,335p' modules/access.py
echo ""

echo "═══ ۴. access.py — register ═══"
sed -n '330,345p' modules/access.py
echo ""

echo "═══ ۵. access.py — ADMIN_PERMS و DEPUTY_PERMS و VIP_PERMS ═══"
sed -n '1,15p' modules/access.py
echo ""

echo "═══ ۶. database.py — توابع perms ═══"
grep -n "^def.*perm" database.py
echo ""

echo "═══ ۷. کجاها «دسترسی» توی start.py هست ═══"
grep -n "دسترسی" modules/start.py | head -20
echo ""

echo "═══ ۸. توی منوی مالک گروه — خط 400-500 ═══"
grep -n "تنظیمات گروه\|group_settings\|g_setting\|g_op" modules/start.py | head -20
echo ""

echo "═══ ۹. database — جدول user_perms ═══"
source venv/bin/activate
python3 -c "
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute('PRAGMA table_info(user_perms)')
print('user_perms:')
for r in c.fetchall(): print(f'  {r}')
print()
c.execute('SELECT * FROM user_perms LIMIT 10')
print('نمونه:')
for r in c.fetchall(): print(f'  {r}')
print()
c.execute('PRAGMA table_info(deputy_perms)')
print('deputy_perms:')
for r in c.fetchall(): print(f'  {r}')
print()
c.execute('PRAGMA table_info(admin_permissions)')
print('admin_permissions:')
for r in c.fetchall(): print(f'  {r}')
conn.close()
"
echo ""

echo "═══ ۱۰. توی owner_panel_trigger.py — کجا منوی مالک باز می‌شه ═══"
grep -n "افزودن مدیر\|تنظیمات گروه\|افزودن ادمین" modules/owner_panel_trigger.py modules/start.py | head -20
echo ""

echo "═══ ۱۱. توی start.py — منوی مالک گروه (group_owner_panel_menu) ═══"
grep -n "def group_owner_panel_menu\|def owner_section_menu\|def sudo_panel_menu\|def owner_botadmins_menu" modules/start.py
echo ""

echo "═══ ۱۲. owner_guide.py — راهنمای دسترسی ═══"
grep -n "guide_access\|guide_manage\|guide_owner" modules/owner_guide.py | head -20
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/PHASE1_DIAG.txt

echo ""
echo "✅ فایل: ~/PHASE1_DIAG.txt"
echo "📏 خطوط: $(wc -l < ~/PHASE1_DIAG.txt)"
