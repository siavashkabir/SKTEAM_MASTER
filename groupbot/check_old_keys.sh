#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 کجا از key های پاک‌شده استفاده می‌شه"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. get_admin_perm کجاها صدا زده می‌شه ═══"
grep -rn "get_admin_perm\|has_admin_perm" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۲. set_admin_perm کجاها صدا زده می‌شه ═══"
grep -rn "set_admin_perm" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۳. can_delete_messages ═══"
grep -rn "can_delete_messages" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۴. can_restrict_members ═══"
grep -rn "can_restrict_members" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۵. can_pin_messages ═══"
grep -rn "can_pin_messages" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۶. can_invite_users ═══"
grep -rn "can_invite_users" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۷. can_manage_video_chats ═══"
grep -rn "can_manage_video_chats" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۸. can_change_info ═══"
grep -rn "can_change_info" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۹. 'config' key ═══"
grep -rn '"config"\|get_admin_perm.*config\|get_deputy_perm.*config' modules/*.py | grep -v ".bak" | head -10
echo ""

echo "═══ ۱۰. 'locks' key ═══"
grep -rn 'get_admin_perm.*locks\|get_deputy_perm.*locks\|"locks"' modules/*.py | grep -v ".bak" | head -10
echo ""

echo "═══ ۱۱. 'nickname' key ═══"
grep -rn 'get_deputy_perm.*nickname\|"nickname"' modules/*.py | grep -v ".bak" | head -5
echo ""

echo "═══ ۱۲. 'nsfw' key (access) ═══"
grep -rn 'get_deputy_perm.*nsfw' modules/*.py | grep -v ".bak" | head -5
echo ""

echo "═══ ۱۳. admin_permissions کجاها SELECT می‌شه ═══"
grep -rn "FROM admin_permissions\|admin_permissions WHERE" modules/*.py database.py | grep -v ".bak"
echo ""

echo "═══ ۱۴. ban/mute — کجا چک perms می‌کنه ═══"
grep -rn "def ban_\|def mute_\|def kick_" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۱۵. deprecated keys — کجا هنوز استفاده می‌شن ═══"
for key in "config" "media" "locks_main" "locks_media" "nickname"; do
    echo "── $key ──"
    grep -rn "\"$key\"" modules/*.py | grep -v ".bak" | grep -i "perm\|access" | head -3
done
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/CHECK_OLD_KEYS.txt

echo ""
echo "✅ فایل: ~/CHECK_OLD_KEYS.txt"
echo "📏 خطوط: $(wc -l < ~/CHECK_OLD_KEYS.txt)"
