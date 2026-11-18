# جستجوی دقیق callback های پنل سازنده

تاریخ: 2026-10-05 02:43:25.358584

## بخش ۱: هر callback کجا تعریف و کجا handler شده

### `owner_section_menu`

**start.py** — 8 تطابق:
```
  161 | def sudo_panel_menu(uid, chat_id=0):
  162 |     return InlineKeyboardMarkup([
  163 |         [InlineKeyboardButton("💎 مدیریت اشتراک‌ها", callback_data="sub_manage:" + str(uid) + ":" + str(chat_id))],
  164 |         [InlineKeyboardButton("🔧 بخش سازنده", callback_data="owner_section_menu:" + str(uid) + ":" + str(chat_id))],
  165 |         [InlineKeyboardButton("🔗 ورود به پنل گروه", callback_data="s_panel_group:" + str(uid) + ":" + str(chat_id))],
  166 |         [InlineKeyboardButton("📖 راهنمای کامل", callback_data="owner_readme:" + str(uid) + ":" + str(chat_id))],
  167 |         [InlineKeyboardButton("⚙️ تنظیمات این گروه", callback_data="owner_set_group:" + str(uid) + ":" + str(chat_id))],
---
  256 | 
  257 | 
  258 | 
  259 | def owner_section_menu(uid, chat_id=0):
  260 |     return InlineKeyboardMarkup([
  261 |         [InlineKeyboardButton("👤 مدیریت ادمین‌های ربات", callback_data="op_botadmins:" + str(uid) + ":" + str(chat_id))],
  262 |         [InlineKeyboardButton("🌐 مدیریت گروه‌ها", callback_data="rmt_groups:" + str(uid) + ":" + str(chat_id))],
---
  272 | 
  273 |         [InlineKeyboardButton("💎 مدیریت اشتراک‌ها", callback_data="menu_status:" + str(uid))],
  274 | 
  275 |         [InlineKeyboardButton("🔧 بخش سازنده", callback_data="owner_section_menu:" + str(uid) + ":" + str(chat_id))],
  276 | 
  277 |         [InlineKeyboardButton("👥 ورود به پنل گروه", callback_data="g_back_panel:" + str(uid) + ":" + str(chat_id))],
  278 | 
---
  443 | 
  444 |         [InlineKeyboardButton("🔓 فعال/غیرفعال کردن گروه", callback_data="op_sub_off:" + str(uid) + ":" + str(chat_id))],
  445 | 
  446 |         [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_menu:" + str(uid) + ":" + str(chat_id))],
  447 | 
  448 | 
  449 |     ])
---
 6353 |             print("[GROUP STATS ERR] " + str(e))
 6354 |         return
 6355 | 
 6356 |     if action == "owner_section_menu":
 6357 |         # [SECURITY FIX] فقط سازنده/سودو
 6358 |         try:
 6359 |             from config import OWNER_ID
---
 6374 |         try:
 6375 |             await query.edit_message_text(
 6376 |                 "\U0001F527 \u0628\u062e\u0634 \u0633\u0627\u0632\u0646\u062f\u0647\n\n\u06af\u0632\u06cc\u0646\u0647 \u0645\u0648\u0631\u062f \u0646\u0638\u0631 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:",
 6377 |                 reply_markup=owner_section_menu(query.from_user.id, query.message.chat.id)
 6378 |             )
 6379 |         except Exception as e:
 6380 |             print("[SECTION MENU ERR] " + str(e))
---
 6400 |         try:
 6401 |             await query.edit_message_text(
 6402 |                 "\U0001F527 \u0628\u062e\u0634 \u0633\u0627\u0632\u0646\u062f\u0647\n\n\u06af\u0632\u06cc\u0646\u0647 \u0645\u0648\u0631\u062f \u0646\u0638\u0631 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:",
 6403 |                 reply_markup=owner_section_menu(query.from_user.id, query.message.chat.id)
 6404 |             )
 6405 |         except Exception as e:
 6406 |             print("[SECTION BACK ERR] " + str(e))
---
 6858 | 
 6859 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, persian_handler, block=False), group=7)
 6860 | 
 6861 |     app.add_handler(CallbackQueryHandler(handler, pattern="^(gowner_back|menu_back|menu_manage|menu_settings|menu_status|menu_owners|menu_admins|menu_vip|menu_deputies|menu_help|menu_close|menu_admin_perms|menu_deputy_perms|aperm|dperm|invite_unban_toggle|games_toggle|forces_|help_page_|set_lang_|pv_|pvc_|op_|sub_|vcall_|music_|purge_|nsfw_|nsub_|vsub_|msub_|rmt_|s_fj_|s_ba_|link_|s_panel_group|s_op_|s_backup|s_logs|s_restart_bot|s_sudo_stats|s_group_stats|osub_|rn_|greq_|gdur_|g_op_sub_|g_op_|pm_|g_back_panel|g_depset|g_ownerguide)|owner_section_menu|owner_section_back|sudo_panel_back|s_fj_menu|fj_toggle_sudo|fj_setlink_sudo|s_op_sudo_stats|s_op_group_stats|group_panel_back"), group=1)
 6862 | 
 6863 |     # Reports System
 6864 | 
---
```

**pv_main.py** — 3 تطابق:
```
  393 |         return
  394 | 
  395 |     # مدیریت گروه
  396 |     if action == "owner_section_menu":
  397 |         try:
  398 |             from modules.start import owner_section_menu
  399 |             await query.edit_message_text(
---
  395 |     # مدیریت گروه
  396 |     if action == "owner_section_menu":
  397 |         try:
  398 |             from modules.start import owner_section_menu
  399 |             await query.edit_message_text(
  400 |                 "🔧 بخش سازنده\n\nگزینه مورد نظر را انتخاب کنید:",
  401 |                 reply_markup=owner_section_menu(user.id, group_chat_id or 0)
---
  398 |             from modules.start import owner_section_menu
  399 |             await query.edit_message_text(
  400 |                 "🔧 بخش سازنده\n\nگزینه مورد نظر را انتخاب کنید:",
  401 |                 reply_markup=owner_section_menu(user.id, group_chat_id or 0)
  402 |             )
  403 |             _schedule_delete(context, chat.id)
  404 |         except Exception as e:
---
```

### `owner_section_back`

**start.py** — 14 تطابق:
```
  183 | 
  184 |         [InlineKeyboardButton("📖 راهنمای مالک", callback_data="g_op_ownerguide:" + str(uid) + ":" + str(chat_id))],
  185 | 
  186 |         [InlineKeyboardButton("🔙 بازگشت به پنل سازنده", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
  187 | 
  188 | 
  189 |     ])
---
  216 | 
  217 |         if is_bot_owner_or_sudo(uid):
  218 | 
  219 |             btns.append([InlineKeyboardButton("🔙 بازگشت به پنل سازنده", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
  220 | 
  221 |     except Exception:
  222 | 
---
  462 | 
  463 |         [InlineKeyboardButton("راهنما مدیریت ادمین", callback_data="op_ba_help:" + str(uid) + ":" + str(chat_id))],
  464 | 
  465 |         [InlineKeyboardButton("بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id) + ":" + str(chat_id))],
  466 | 
  467 | 
  468 |     ])
---
 2974 | 
 2975 |                 reply_markup=InlineKeyboardMarkup([
 2976 | 
 2977 |                     [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
 2978 | 
 2979 |                     [InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))]
 2980 | 
---
 3166 | 
 3167 |                 reply_markup=InlineKeyboardMarkup([
 3168 | 
 3169 |                     [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
 3170 | 
 3171 |                     [InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))]
 3172 | 
---
 3882 | 
 3883 |                 btns.append([InlineKeyboardButton("➕ تنظیم جوین اجباری", callback_data="s_fj_set:" + str(uid) + ":" + str(chat_id))])
 3884 | 
 3885 |             btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
 3886 | 
 3887 |             await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btns))
 3888 | 
---
 3966 | 
 3967 |                 btns.append([InlineKeyboardButton("➕ تنظیم جوین اجباری", callback_data="s_fj_set:" + str(uid) + ":" + str(chat_id))])
 3968 | 
 3969 |             btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
 3970 | 
 3971 |             await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btns))
 3972 | 
---
 4445 | 
 4446 |                 reply_markup=InlineKeyboardMarkup([
 4447 | 
 4448 |                     [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
 4449 | 
 4450 |                     [InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))]
 4451 | 
---
```

**remote_groups.py** — 1 تطابق:
```
   10 |     for cid, title in chats[:30]:
   11 |         t = (title or "بدون نام")[:30]
   12 |         btns.append([InlineKeyboardButton("👥 " + t, callback_data="rmt_g:" + str(uid) + ":" + str(cid))])
   13 |     btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
   14 |     btns.append([InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))])
   15 |     return InlineKeyboardMarkup(btns)
   16 | 
---
```

### `s_fj_menu`

**start.py** — 5 تطابق:
```
  260 |     return InlineKeyboardMarkup([
  261 |         [InlineKeyboardButton("👤 مدیریت ادمین‌های ربات", callback_data="op_botadmins:" + str(uid) + ":" + str(chat_id))],
  262 |         [InlineKeyboardButton("🌐 مدیریت گروه‌ها", callback_data="rmt_groups:" + str(uid) + ":" + str(chat_id))],
  263 |         [InlineKeyboardButton("🔒 جوین اجباری", callback_data="s_fj_menu:" + str(uid) + ":" + str(chat_id))],
  264 |         [InlineKeyboardButton("📊 آمار سودوها", callback_data="s_op_sudo_stats:" + str(uid) + ":" + str(chat_id))],
  265 |         [InlineKeyboardButton("📈 آمار گروه‌ها", callback_data="s_op_group_stats:" + str(uid) + ":" + str(chat_id))],
  266 |         [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_set_back:" + str(uid))],
---
 4010 | 
 4011 |             reply_markup=InlineKeyboardMarkup([
 4012 | 
 4013 |                 [InlineKeyboardButton("🔙 لغو", callback_data="s_fj_menu:" + str(uid) + ":" + str(chat_id))]
 4014 | 
 4015 |             ])
 4016 | 
---
 4042 | 
 4043 |                 reply_markup=InlineKeyboardMarkup([
 4044 | 
 4045 |                     [InlineKeyboardButton("🔙 بازگشت", callback_data="s_fj_menu:" + str(uid) + ":" + str(chat_id))]
 4046 | 
 4047 |                 ])
 4048 | 
---
 6243 | 
 6244 | 
 6245 | 
 6246 |     if action == "s_fj_menu":
 6247 |         try:
 6248 |             from config import OWNER_ID
 6249 |             from database import is_bot_admin
---
 6858 | 
 6859 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, persian_handler, block=False), group=7)
 6860 | 
 6861 |     app.add_handler(CallbackQueryHandler(handler, pattern="^(gowner_back|menu_back|menu_manage|menu_settings|menu_status|menu_owners|menu_admins|menu_vip|menu_deputies|menu_help|menu_close|menu_admin_perms|menu_deputy_perms|aperm|dperm|invite_unban_toggle|games_toggle|forces_|help_page_|set_lang_|pv_|pvc_|op_|sub_|vcall_|music_|purge_|nsfw_|nsub_|vsub_|msub_|rmt_|s_fj_|s_ba_|link_|s_panel_group|s_op_|s_backup|s_logs|s_restart_bot|s_sudo_stats|s_group_stats|osub_|rn_|greq_|gdur_|g_op_sub_|g_op_|pm_|g_back_panel|g_depset|g_ownerguide)|owner_section_menu|owner_section_back|sudo_panel_back|s_fj_menu|fj_toggle_sudo|fj_setlink_sudo|s_op_sudo_stats|s_op_group_stats|group_panel_back"), group=1)
 6862 | 
 6863 |     # Reports System
 6864 | 
---
```

### `s_fj_set`

**start.py** — 2 تطابق:
```
 3880 | 
 3881 |                 text += "❌ هنوز تنظیم نشده." + NL + NL
 3882 | 
 3883 |                 btns.append([InlineKeyboardButton("➕ تنظیم جوین اجباری", callback_data="s_fj_set:" + str(uid) + ":" + str(chat_id))])
 3884 | 
 3885 |             btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
 3886 | 
---
 3964 | 
 3965 |                 text += "❌ هنوز تنظیم نشده." + NL + NL
 3966 | 
 3967 |                 btns.append([InlineKeyboardButton("➕ تنظیم جوین اجباری", callback_data="s_fj_set:" + str(uid) + ":" + str(chat_id))])
 3968 | 
 3969 |             btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
 3970 | 
---
```

### `s_fj_toggle`

**start.py** — 4 تطابق:
```
 3868 | 
 3869 |                 if enabled:
 3870 | 
 3871 |                     btns.append([InlineKeyboardButton("🔴 خاموش کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3872 | 
 3873 |                 else:
 3874 | 
---
 3872 | 
 3873 |                 else:
 3874 | 
 3875 |                     btns.append([InlineKeyboardButton("🟢 روشن کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3876 | 
 3877 |                 btns.append([InlineKeyboardButton("🗑️ حذف کامل جوین اجباری", callback_data="s_fj_del:" + str(uid) + ":" + str(chat_id))])
 3878 | 
---
 3952 | 
 3953 |                 if enabled:
 3954 | 
 3955 |                     btns.append([InlineKeyboardButton("🔴 خاموش کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3956 | 
 3957 |                 else:
 3958 | 
---
 3956 | 
 3957 |                 else:
 3958 | 
 3959 |                     btns.append([InlineKeyboardButton("🟢 روشن کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3960 | 
 3961 |                 btns.append([InlineKeyboardButton("🗑️ حذف کامل جوین اجباری", callback_data="s_fj_del:" + str(uid) + ":" + str(chat_id))])
 3962 | 
---
```

### `s_fj_del`

**start.py** — 2 تطابق:
```
 3874 | 
 3875 |                     btns.append([InlineKeyboardButton("🟢 روشن کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3876 | 
 3877 |                 btns.append([InlineKeyboardButton("🗑️ حذف کامل جوین اجباری", callback_data="s_fj_del:" + str(uid) + ":" + str(chat_id))])
 3878 | 
 3879 |             else:
 3880 | 
---
 3958 | 
 3959 |                     btns.append([InlineKeyboardButton("🟢 روشن کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3960 | 
 3961 |                 btns.append([InlineKeyboardButton("🗑️ حذف کامل جوین اجباری", callback_data="s_fj_del:" + str(uid) + ":" + str(chat_id))])
 3962 | 
 3963 |             else:
 3964 | 
---
```

### `s_op_botadmins`

**start.py** — 3 تطابق:
```
 5494 | 
 5495 |             reply_markup=InlineKeyboardMarkup([
 5496 | 
 5497 |                 [InlineKeyboardButton("🔙 لغو", callback_data="s_op_botadmins:" + str(uid) + ":" + str(target_chat))]
 5498 | 
 5499 |             ])
 5500 | 
---
 5540 | 
 5541 |                 btns.append([InlineKeyboardButton(btn_text, callback_data="s_ba_perm:" + str(uid) + ":" + str(bid))])
 5542 | 
 5543 |         btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="s_op_botadmins:" + str(uid) + ":" + str(target_chat))])
 5544 | 
 5545 |         btns.append([InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))])
 5546 | 
---
 5812 | 
 5813 |                     btns.append([InlineKeyboardButton(btn_text, callback_data="s_ba_perm:" + str(uid) + ":" + str(bid))])
 5814 | 
 5815 |             btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="s_op_botadmins:" + str(uid) + ":" + str(chat_id))])
 5816 | 
 5817 |             btns.append([InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))])
 5818 | 
---
```

### `s_op_ba_list`

**start.py** — 2 تطابق:
```
 5598 | 
 5599 |                 [InlineKeyboardButton("🗑️ حذف ادمین ربات", callback_data="s_ba_del:" + str(uid) + ":" + str(_target_bid))],
 5600 | 
 5601 |                 [InlineKeyboardButton("🔙 بازگشت", callback_data="s_op_ba_list:" + str(uid) + ":" + str(chat_id))],
 5602 | 
 5603 |                 [InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))]
 5604 | 
---
 5666 | 
 5667 |                 [InlineKeyboardButton("🗑️ حذف ادمین ربات", callback_data="s_ba_del:" + str(uid) + ":" + str(_target_bid))],
 5668 | 
 5669 |                 [InlineKeyboardButton("🔙 بازگشت", callback_data="s_op_ba_list:" + str(uid) + ":" + str(chat_id))],
 5670 | 
 5671 |                 [InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))]
 5672 | 
---
```

### `s_op_sudo_stats`

**start.py** — 3 تطابق:
```
  261 |         [InlineKeyboardButton("👤 مدیریت ادمین‌های ربات", callback_data="op_botadmins:" + str(uid) + ":" + str(chat_id))],
  262 |         [InlineKeyboardButton("🌐 مدیریت گروه‌ها", callback_data="rmt_groups:" + str(uid) + ":" + str(chat_id))],
  263 |         [InlineKeyboardButton("🔒 جوین اجباری", callback_data="s_fj_menu:" + str(uid) + ":" + str(chat_id))],
  264 |         [InlineKeyboardButton("📊 آمار سودوها", callback_data="s_op_sudo_stats:" + str(uid) + ":" + str(chat_id))],
  265 |         [InlineKeyboardButton("📈 آمار گروه‌ها", callback_data="s_op_group_stats:" + str(uid) + ":" + str(chat_id))],
  266 |         [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_set_back:" + str(uid))],
  267 |     ])
---
 6298 |         )
 6299 |         return
 6300 | 
 6301 |     if action == "s_op_sudo_stats":
 6302 |         try:
 6303 |             from config import OWNER_ID, DATABASE_PATH
 6304 |             from database import is_bot_admin
---
 6858 | 
 6859 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, persian_handler, block=False), group=7)
 6860 | 
 6861 |     app.add_handler(CallbackQueryHandler(handler, pattern="^(gowner_back|menu_back|menu_manage|menu_settings|menu_status|menu_owners|menu_admins|menu_vip|menu_deputies|menu_help|menu_close|menu_admin_perms|menu_deputy_perms|aperm|dperm|invite_unban_toggle|games_toggle|forces_|help_page_|set_lang_|pv_|pvc_|op_|sub_|vcall_|music_|purge_|nsfw_|nsub_|vsub_|msub_|rmt_|s_fj_|s_ba_|link_|s_panel_group|s_op_|s_backup|s_logs|s_restart_bot|s_sudo_stats|s_group_stats|osub_|rn_|greq_|gdur_|g_op_sub_|g_op_|pm_|g_back_panel|g_depset|g_ownerguide)|owner_section_menu|owner_section_back|sudo_panel_back|s_fj_menu|fj_toggle_sudo|fj_setlink_sudo|s_op_sudo_stats|s_op_group_stats|group_panel_back"), group=1)
 6862 | 
 6863 |     # Reports System
 6864 | 
---
```

### `s_op_group_stats`

**start.py** — 3 تطابق:
```
  262 |         [InlineKeyboardButton("🌐 مدیریت گروه‌ها", callback_data="rmt_groups:" + str(uid) + ":" + str(chat_id))],
  263 |         [InlineKeyboardButton("🔒 جوین اجباری", callback_data="s_fj_menu:" + str(uid) + ":" + str(chat_id))],
  264 |         [InlineKeyboardButton("📊 آمار سودوها", callback_data="s_op_sudo_stats:" + str(uid) + ":" + str(chat_id))],
  265 |         [InlineKeyboardButton("📈 آمار گروه‌ها", callback_data="s_op_group_stats:" + str(uid) + ":" + str(chat_id))],
  266 |         [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_set_back:" + str(uid))],
  267 |     ])
  268 | 
---
 6325 |             print("[SUDO STATS ERR] " + str(e))
 6326 |         return
 6327 | 
 6328 |     if action == "s_op_group_stats":
 6329 |         try:
 6330 |             from config import OWNER_ID, DATABASE_PATH
 6331 |             from database import is_bot_admin
---
 6858 | 
 6859 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, persian_handler, block=False), group=7)
 6860 | 
 6861 |     app.add_handler(CallbackQueryHandler(handler, pattern="^(gowner_back|menu_back|menu_manage|menu_settings|menu_status|menu_owners|menu_admins|menu_vip|menu_deputies|menu_help|menu_close|menu_admin_perms|menu_deputy_perms|aperm|dperm|invite_unban_toggle|games_toggle|forces_|help_page_|set_lang_|pv_|pvc_|op_|sub_|vcall_|music_|purge_|nsfw_|nsub_|vsub_|msub_|rmt_|s_fj_|s_ba_|link_|s_panel_group|s_op_|s_backup|s_logs|s_restart_bot|s_sudo_stats|s_group_stats|osub_|rn_|greq_|gdur_|g_op_sub_|g_op_|pm_|g_back_panel|g_depset|g_ownerguide)|owner_section_menu|owner_section_back|sudo_panel_back|s_fj_menu|fj_toggle_sudo|fj_setlink_sudo|s_op_sudo_stats|s_op_group_stats|group_panel_back"), group=1)
 6862 | 
 6863 |     # Reports System
 6864 | 
---
```

### `s_ba_perm`

**start.py** — 3 تطابق:
```
 5538 | 
 5539 |                 btn_text = "👤 " + (first_name or "بدون نام") + " " + uname
 5540 | 
 5541 |                 btns.append([InlineKeyboardButton(btn_text, callback_data="s_ba_perm:" + str(uid) + ":" + str(bid))])
 5542 | 
 5543 |         btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="s_op_botadmins:" + str(uid) + ":" + str(target_chat))])
 5544 | 
---
 5736 | 
 5737 |                 [InlineKeyboardButton("✅ بله، حذف کن", callback_data="s_ba_del_confirm:" + str(uid) + ":" + str(_target_bid))],
 5738 | 
 5739 |                 [InlineKeyboardButton("❌ انصراف", callback_data="s_ba_perm:" + str(uid) + ":" + str(_target_bid))]
 5740 | 
 5741 |             ])
 5742 | 
---
 5810 | 
 5811 |                     btn_text = "👤 " + (first_name or "بدون نام") + " " + uname
 5812 | 
 5813 |                     btns.append([InlineKeyboardButton(btn_text, callback_data="s_ba_perm:" + str(uid) + ":" + str(bid))])
 5814 | 
 5815 |             btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="s_op_botadmins:" + str(uid) + ":" + str(chat_id))])
 5816 | 
---
```

### `s_ba_toggle_fj`

**start.py** — 2 تطابق:
```
 5594 | 
 5595 |             kb = InlineKeyboardMarkup([
 5596 | 
 5597 |                 [InlineKeyboardButton(_mark + " معاف از جوین اجباری", callback_data="s_ba_toggle_fj:" + str(uid) + ":" + str(_target_bid))],
 5598 | 
 5599 |                 [InlineKeyboardButton("🗑️ حذف ادمین ربات", callback_data="s_ba_del:" + str(uid) + ":" + str(_target_bid))],
 5600 | 
---
 5662 | 
 5663 |             kb = InlineKeyboardMarkup([
 5664 | 
 5665 |                 [InlineKeyboardButton(_mark + " معاف از جوین اجباری", callback_data="s_ba_toggle_fj:" + str(uid) + ":" + str(_target_bid))],
 5666 | 
 5667 |                 [InlineKeyboardButton("🗑️ حذف ادمین ربات", callback_data="s_ba_del:" + str(uid) + ":" + str(_target_bid))],
 5668 | 
---
```

### `s_ba_del`

**start.py** — 3 تطابق:
```
 5596 | 
 5597 |                 [InlineKeyboardButton(_mark + " معاف از جوین اجباری", callback_data="s_ba_toggle_fj:" + str(uid) + ":" + str(_target_bid))],
 5598 | 
 5599 |                 [InlineKeyboardButton("🗑️ حذف ادمین ربات", callback_data="s_ba_del:" + str(uid) + ":" + str(_target_bid))],
 5600 | 
 5601 |                 [InlineKeyboardButton("🔙 بازگشت", callback_data="s_op_ba_list:" + str(uid) + ":" + str(chat_id))],
 5602 | 
---
 5664 | 
 5665 |                 [InlineKeyboardButton(_mark + " معاف از جوین اجباری", callback_data="s_ba_toggle_fj:" + str(uid) + ":" + str(_target_bid))],
 5666 | 
 5667 |                 [InlineKeyboardButton("🗑️ حذف ادمین ربات", callback_data="s_ba_del:" + str(uid) + ":" + str(_target_bid))],
 5668 | 
 5669 |                 [InlineKeyboardButton("🔙 بازگشت", callback_data="s_op_ba_list:" + str(uid) + ":" + str(chat_id))],
 5670 | 
---
 5734 | 
 5735 |             kb = InlineKeyboardMarkup([
 5736 | 
 5737 |                 [InlineKeyboardButton("✅ بله، حذف کن", callback_data="s_ba_del_confirm:" + str(uid) + ":" + str(_target_bid))],
 5738 | 
 5739 |                 [InlineKeyboardButton("❌ انصراف", callback_data="s_ba_perm:" + str(uid) + ":" + str(_target_bid))]
 5740 | 
---
```

### `s_ba_del_confirm`

**start.py** — 1 تطابق:
```
 5734 | 
 5735 |             kb = InlineKeyboardMarkup([
 5736 | 
 5737 |                 [InlineKeyboardButton("✅ بله، حذف کن", callback_data="s_ba_del_confirm:" + str(uid) + ":" + str(_target_bid))],
 5738 | 
 5739 |                 [InlineKeyboardButton("❌ انصراف", callback_data="s_ba_perm:" + str(uid) + ":" + str(_target_bid))]
 5740 | 
---
```

### `s_panel_group`

**start.py** — 4 تطابق:
```
  162 |     return InlineKeyboardMarkup([
  163 |         [InlineKeyboardButton("💎 مدیریت اشتراک‌ها", callback_data="sub_manage:" + str(uid) + ":" + str(chat_id))],
  164 |         [InlineKeyboardButton("🔧 بخش سازنده", callback_data="owner_section_menu:" + str(uid) + ":" + str(chat_id))],
  165 |         [InlineKeyboardButton("🔗 ورود به پنل گروه", callback_data="s_panel_group:" + str(uid) + ":" + str(chat_id))],
  166 |         [InlineKeyboardButton("📖 راهنمای کامل", callback_data="owner_readme:" + str(uid) + ":" + str(chat_id))],
  167 |         [InlineKeyboardButton("⚙️ تنظیمات این گروه", callback_data="owner_set_group:" + str(uid) + ":" + str(chat_id))],
  168 |         [InlineKeyboardButton("🖥 مدیریت سیستم", callback_data="sys_menu:" + str(uid) + ":" + str(chat_id))],
---
 5884 | 
 5885 | 
 5886 | 
 5887 |     if action == "s_panel_group_back":
 5888 |         # [SECURITY FIX] مالک گروه نباید به پنل سازنده دسترسی داشته باشه
 5889 |         # این handler الان غیرفعاله - فقط منو رو می‌بنده
 5890 |         try:
---
 5893 |             pass
 5894 |         return
 5895 | 
 5896 |     if action == "s_panel_group":
 5897 |         # [FIX] ورود به پنل مالک گروه
 5898 |         try:
 5899 |             # چک دسترسی: باید مالک یه گروه باشه
---
 6858 | 
 6859 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, persian_handler, block=False), group=7)
 6860 | 
 6861 |     app.add_handler(CallbackQueryHandler(handler, pattern="^(gowner_back|menu_back|menu_manage|menu_settings|menu_status|menu_owners|menu_admins|menu_vip|menu_deputies|menu_help|menu_close|menu_admin_perms|menu_deputy_perms|aperm|dperm|invite_unban_toggle|games_toggle|forces_|help_page_|set_lang_|pv_|pvc_|op_|sub_|vcall_|music_|purge_|nsfw_|nsub_|vsub_|msub_|rmt_|s_fj_|s_ba_|link_|s_panel_group|s_op_|s_backup|s_logs|s_restart_bot|s_sudo_stats|s_group_stats|osub_|rn_|greq_|gdur_|g_op_sub_|g_op_|pm_|g_back_panel|g_depset|g_ownerguide)|owner_section_menu|owner_section_back|sudo_panel_back|s_fj_menu|fj_toggle_sudo|fj_setlink_sudo|s_op_sudo_stats|s_op_group_stats|group_panel_back"), group=1)
 6862 | 
 6863 |     # Reports System
 6864 | 
---
```

### `s_panel_group_back`

**start.py** — 1 تطابق:
```
 5884 | 
 5885 | 
 5886 | 
 5887 |     if action == "s_panel_group_back":
 5888 |         # [SECURITY FIX] مالک گروه نباید به پنل سازنده دسترسی داشته باشه
 5889 |         # این handler الان غیرفعاله - فقط منو رو می‌بنده
 5890 |         try:
---
```

### `sudo_panel_back`

**start.py** — 2 تطابق:
```
 2521 |             print("[GOWNER BACK ERR] " + str(e))
 2522 |         return
 2523 | 
 2524 |     if action == "sudo_panel_back":
 2525 |         try:
 2526 |             await query.edit_message_text(
 2527 |                 "👑 منوی اصلی - بخش مورد نظر:",
---
 6858 | 
 6859 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, persian_handler, block=False), group=7)
 6860 | 
 6861 |     app.add_handler(CallbackQueryHandler(handler, pattern="^(gowner_back|menu_back|menu_manage|menu_settings|menu_status|menu_owners|menu_admins|menu_vip|menu_deputies|menu_help|menu_close|menu_admin_perms|menu_deputy_perms|aperm|dperm|invite_unban_toggle|games_toggle|forces_|help_page_|set_lang_|pv_|pvc_|op_|sub_|vcall_|music_|purge_|nsfw_|nsub_|vsub_|msub_|rmt_|s_fj_|s_ba_|link_|s_panel_group|s_op_|s_backup|s_logs|s_restart_bot|s_sudo_stats|s_group_stats|osub_|rn_|greq_|gdur_|g_op_sub_|g_op_|pm_|g_back_panel|g_depset|g_ownerguide)|owner_section_menu|owner_section_back|sudo_panel_back|s_fj_menu|fj_toggle_sudo|fj_setlink_sudo|s_op_sudo_stats|s_op_group_stats|group_panel_back"), group=1)
 6862 | 
 6863 |     # Reports System
 6864 | 
---
```

**pv_main.py** — 1 تطابق:
```
  405 |             print("[PV SECTION ERR] " + str(e))
  406 |         return
  407 | 
  408 |     if action == "sudo_panel_back":
  409 |         try:
  410 |             from modules.start import sudo_panel_menu
  411 |             await query.edit_message_text(
---
```


## بخش ۲: هندلر اصلی callback (pattern های بزرگ)

**start.py:11**
```
    6 | 
    7 | from datetime import datetime, timedelta
    8 | 
    9 | from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
   10 | 
   11 | from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
   12 | 
   13 | from modules.admin_perms import admin_list_menu, deputy_list_menu, perms_menu, PERMS
   14 | 
   15 | from modules.subs_menu import sub_manage_menu, sub_status_menu, vcall_sub_menu, music_sub_menu
   16 | 
```

**start.py:6861**
```
 6856 | 
 6857 |     app.add_handler(CommandHandler("config", do_refresh))
 6858 | 
 6859 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, persian_handler, block=False), group=7)
 6860 | 
 6861 |     app.add_handler(CallbackQueryHandler(handler, pattern="^(gowner_back|menu_back|menu_manage|menu_settings|menu_status|menu_owners|menu_admins|menu_vip|menu_deputies|menu_help|menu_close|menu_admin_perms|menu_deputy_perms|aperm|dperm|invite_unban_toggle|games_toggle|forces_|help_page_|set_lang_|pv_|pvc_|op_|sub_|vcall_|music_|purge_|nsfw_|nsub_|vsub_|msub_|rmt_|s_fj_|s_ba_|link_|s_panel_group|s_op_|s_backup|s_logs|s_restart_bot|s_sudo_stats|s_group_stats|osub_|rn_|greq_|gdur_|g_op_sub_|g_op_|pm_|g_back_panel|g_depset|g_ownerguide)|owner_section_menu|owner_section_back|sudo_panel_back|s_fj_menu|fj_toggle_sudo|fj_setlink_sudo|s_op_sudo_stats|s_op_group_stats|group_panel_back"), group=1)
 6862 | 
 6863 |     # Reports System
 6864 | 
 6865 |     try:
 6866 | 
```

**pv_main.py:2**
```
    1 | from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    2 | from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, ApplicationHandlerStop
    3 | from config import OWNER_ID
    4 | 
    5 | NL = chr(10)
    6 | 
    7 | # قیمت‌ها (تومان)
```

**pv_main.py:193**
```
  188 |     _track_message(chat.id, sent.message_id)
  189 |     _schedule_delete(context, chat.id)
  190 |     return
  191 | 
  192 | 
  193 | async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  194 |     query = update.callback_query
  195 |     data = query.data
  196 |     user = query.from_user
  197 |     if not data.startswith("pv_"):
  198 |         return
```

**pv_main.py:558**
```
  553 |         return
  554 | 
  555 | 
  556 | def register(app):
  557 |     app.add_handler(CommandHandler("start", start_cmd), group=-10)
  558 |     app.add_handler(CallbackQueryHandler(callback_handler, pattern="^pv_"), group=-10)
  559 |     app.add_handler(CallbackQueryHandler(order_from_status_handler, pattern="^ord_"), group=-11)
  560 | # [DISABLED BY AI TO FIX CONFLICT] app.add_handler(CallbackQueryHandler(pv_owner_callbacks, pattern="^(op_back|op_manage|op_settings|op_ownerguide):"), group=-12)
  561 | 
  562 | 
  563 | def refresh_prices():
```

**pv_main.py:559**
```
  554 | 
  555 | 
  556 | def register(app):
  557 |     app.add_handler(CommandHandler("start", start_cmd), group=-10)
  558 |     app.add_handler(CallbackQueryHandler(callback_handler, pattern="^pv_"), group=-10)
  559 |     app.add_handler(CallbackQueryHandler(order_from_status_handler, pattern="^ord_"), group=-11)
  560 | # [DISABLED BY AI TO FIX CONFLICT] app.add_handler(CallbackQueryHandler(pv_owner_callbacks, pattern="^(op_back|op_manage|op_settings|op_ownerguide):"), group=-12)
  561 | 
  562 | 
  563 | def refresh_prices():
  564 |     """بارگذاری قیمت‌ها از دیتابیس روی PRICES"""
```

**pv_main.py:560**
```
  555 | 
  556 | def register(app):
  557 |     app.add_handler(CommandHandler("start", start_cmd), group=-10)
  558 |     app.add_handler(CallbackQueryHandler(callback_handler, pattern="^pv_"), group=-10)
  559 |     app.add_handler(CallbackQueryHandler(order_from_status_handler, pattern="^ord_"), group=-11)
  560 | # [DISABLED BY AI TO FIX CONFLICT] app.add_handler(CallbackQueryHandler(pv_owner_callbacks, pattern="^(op_back|op_manage|op_settings|op_ownerguide):"), group=-12)
  561 | 
  562 | 
  563 | def refresh_prices():
  564 |     """بارگذاری قیمت‌ها از دیتابیس روی PRICES"""
  565 |     global PRICES
```

**owner_set_group.py:3**
```
    1 | """تنظیمات per-group برای هر گروه - فقط Owner و Sudo"""
    2 | from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    3 | from telegram.ext import ContextTypes, CallbackQueryHandler
    4 | from config import OWNER_ID
    5 | from database import (
    6 |     get_ai_setting, set_ai_setting,
    7 |     get_ai_setting, set_ai_setting,
    8 |     get_chat_cooldown, set_chat_cooldown,
```

**owner_set_group.py:440**
```
  435 |     await query.answer()
  436 | 
  437 | 
  438 | def register(app):
  439 |     app.add_handler(
  440 |         CallbackQueryHandler(owner_set_cb, pattern=r"^(owner_set_|timer_menu|timer_back|ai_menu|ai_back|rep_settings_menu|rep_settings_back|owner_rep_dl|owner_rep_cd)"),
  441 |         group=-45
  442 |     )
  443 |     print("OK module owner_set_group loaded")
```

**system_management.py:8**
```
    3 | import time
    4 | import asyncio
    5 | import subprocess
    6 | import datetime
    7 | from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    8 | from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, ApplicationHandlerStop
    9 | from config import OWNER_ID, DATABASE_PATH
   10 | from database import (
   11 |     get_chat_panel_timeout, get_chat_expire_delete,
   12 |     get_setting, set_setting, get_all_bot_chats, check_active,
   13 |     vacuum_database, check_db_integrity, get_db_stats,
```

**system_management.py:832**
```
  827 |         pass
  828 |     raise ApplicationHandlerStop
  829 | 
  830 | 
  831 | def register(app):
  832 |     app.add_handler(CallbackQueryHandler(sys_cb, pattern=r"^sys_"), group=-40)
  833 |     app.add_handler(CallbackQueryHandler(sys_cb, pattern=r"^bio_"), group=-40)
  834 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, bio_text_handler), group=-40)
  835 |     print("OK module system_management loaded")
```

**system_management.py:833**
```
  828 |     raise ApplicationHandlerStop
  829 | 
  830 | 
  831 | def register(app):
  832 |     app.add_handler(CallbackQueryHandler(sys_cb, pattern=r"^sys_"), group=-40)
  833 |     app.add_handler(CallbackQueryHandler(sys_cb, pattern=r"^bio_"), group=-40)
  834 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, bio_text_handler), group=-40)
  835 |     print("OK module system_management loaded")
```

**force_join.py:11**
```
    6 | - دستور معاف کردن برای OWNER/SUDO
    7 | """
    8 | 
    9 | from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
   10 | from telegram.ext import (
   11 |     ContextTypes, MessageHandler, CallbackQueryHandler,
   12 |     ApplicationHandlerStop, filters
   13 | )
   14 | 
   15 | NL = chr(10)
   16 | FJ_WAIT = {}
```

**force_join.py:209**
```
  204 |         group=-1
  205 |     )
  206 | 
  207 |     # دکمه بررسی
  208 |     app.add_handler(
  209 |         CallbackQueryHandler(fj_check_callback, pattern="^fj_check:"),
  210 |         group=-1
  211 |     )
  212 | 
  213 |     # دستور معاف کردن
  214 |     app.add_handler(
```

**reply.py:706**
```
  701 |             except Exception:
  702 |                 await query.message.reply_text("بیو " + cat + ":" + NL + NL + bio, reply_markup=kb)
  703 | 
  704 | 
  705 | def register(app):
  706 |     from telegram.ext import CallbackQueryHandler
  707 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler, block=False), group=1)
  708 |     app.add_handler(CallbackQueryHandler(bio_button_handler, pattern="^bio_"))
```

**reply.py:708**
```
  703 | 
  704 | 
  705 | def register(app):
  706 |     from telegram.ext import CallbackQueryHandler
  707 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler, block=False), group=1)
  708 |     app.add_handler(CallbackQueryHandler(bio_button_handler, pattern="^bio_"))
```


## بخش ۳: هندلری که owner_section_back رو پردازش می‌کنه

**start.py:186**
```
  171 | 
  172 | def group_panel_for_sudo(uid, chat_id=0):
  173 | 
  174 |     """پنل گروه برای سازنده/سودو (بدون دکمه اشتراک)"""
  175 | 
  176 |     return InlineKeyboardMarkup([
  177 | 
  178 |         [InlineKeyboardButton("👥 مدیریت گروه", callback_data="g_op_manage:" + str(uid) + ":" + str(chat_id))],
  179 | 
  180 |         [InlineKeyboardButton("⚙️ تنظیمات گروه", callback_data="g_op_settings:" + str(uid) + ":" + str(chat_id))],
  181 | 
  182 |         [InlineKeyboardButton("💰 خدمات/پشتیبانی", callback_data="g_depset_menu:" + str(uid) + ":" + str(chat_id))],
  183 | 
  184 |         [InlineKeyboardButton("📖 راهنمای مالک", callback_data="g_op_ownerguide:" + str(uid) + ":" + str(chat_id))],
  185 | 
  186 |         [InlineKeyboardButton("🔙 بازگشت به پنل سازنده", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
  187 | 
  188 | 
  189 |     ])
  190 | 
  191 | 
  192 | 
  193 | 
  194 | 
  195 | def group_owner_panel_menu(uid, chat_id=0):
  196 | 
  197 |     btns = [
  198 | 
  199 |         [InlineKeyboardButton("💳 مدیریت اشتراک گروه", callback_data="g_op_sub:" + str(uid) + ":" + str(chat_id))],
  200 | 
  201 |         [InlineKeyboardButton("👥 مدیریت گروه", callback_data="g_op_manage:" + str(uid) + ":" + str(chat_id))],
```

**start.py:219**
```
  204 | 
  205 |         [InlineKeyboardButton("💰 خدمات/پشتیبانی", callback_data="g_depset_menu:" + str(uid) + ":" + str(chat_id))],
  206 | 
  207 |         [InlineKeyboardButton("📖 راهنمای مالک", callback_data="g_op_ownerguide:" + str(uid) + ":" + str(chat_id))],
  208 | 
  209 |     ]
  210 | 
  211 |     # فقط اگه سودو باشه، دکمه بازگشت به پنل سازنده اضافه بشه
  212 | 
  213 |     try:
  214 | 
  215 |         from database import is_bot_owner_or_sudo
  216 | 
  217 |         if is_bot_owner_or_sudo(uid):
  218 | 
  219 |             btns.append([InlineKeyboardButton("🔙 بازگشت به پنل سازنده", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
  220 | 
  221 |     except Exception:
  222 | 
  223 |         pass
  224 | 
  225 |     btns.append([InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))])
  226 | 
  227 |     return InlineKeyboardMarkup(btns)
  228 | 
  229 | 
  230 | 
  231 | def _group_owner_panel_old(uid, chat_id=0):
  232 | 
  233 |     return InlineKeyboardMarkup([
  234 | 
```

**start.py:465**
```
  450 | 
  451 | 
  452 | 
  453 | 
  454 | 
  455 | def owner_botadmins_menu(uid, chat_id=0):
  456 | 
  457 |     return InlineKeyboardMarkup([
  458 | 
  459 |         [InlineKeyboardButton("لیست ادمین های ربات", callback_data="op_ba_list:" + str(uid) + ":" + str(chat_id))],
  460 | 
  461 |         [InlineKeyboardButton("➕ افزودن ادمین", callback_data="op_ba_add:" + str(uid) + ":" + str(chat_id))],
  462 | 
  463 |         [InlineKeyboardButton("راهنما مدیریت ادمین", callback_data="op_ba_help:" + str(uid) + ":" + str(chat_id))],
  464 | 
  465 |         [InlineKeyboardButton("بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id) + ":" + str(chat_id))],
  466 | 
  467 | 
  468 |     ])
  469 | 
  470 | 
  471 | 
  472 | 
  473 | 
  474 | # ============================================
  475 | 
  476 | # پنل ادمین گروه (Telegram Admin)
  477 | 
  478 | # ============================================
  479 | 
  480 | 
```

**start.py:2977**
```
 2962 | 
 2963 |                     uname_str = "@" + uname if uname else "بدون یوزرنیم"
 2964 | 
 2965 |                     text += str(i) + ". " + name + NL
 2966 | 
 2967 |                     text += "   👤 " + uname_str + NL
 2968 | 
 2969 |                     text += "   🆔 " + str(uid_db) + NL + NL
 2970 | 
 2971 |             await query.edit_message_text(
 2972 | 
 2973 |                 text,
 2974 | 
 2975 |                 reply_markup=InlineKeyboardMarkup([
 2976 | 
 2977 |                     [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
 2978 | 
 2979 |                     [InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))]
 2980 | 
 2981 |                 ])
 2982 | 
 2983 |             )
 2984 | 
 2985 |         except Exception as e:
 2986 | 
 2987 |             print("[SUDO STATS ERR] " + str(e))
 2988 | 
 2989 |             await query.answer("خطا!", show_alert=True)
 2990 | 
 2991 |         return
 2992 | 
```

**start.py:3169**
```
 3154 | 
 3155 |                 text += "   ━━━━━━━━━━━━━━" + NL + NL
 3156 | 
 3157 |             conn.close()
 3158 | 
 3159 |             if len(text) > 4000:
 3160 | 
 3161 |                 text = text[:3900] + NL + NL + "... (لیست طولانی‌تر است)"
 3162 | 
 3163 |             await query.edit_message_text(
 3164 | 
 3165 |                 text,
 3166 | 
 3167 |                 reply_markup=InlineKeyboardMarkup([
 3168 | 
 3169 |                     [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
 3170 | 
 3171 |                     [InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))]
 3172 | 
 3173 |                 ])
 3174 | 
 3175 |             )
 3176 | 
 3177 |         except Exception as e:
 3178 | 
 3179 |             print("[GROUP STATS ERR] " + str(e))
 3180 | 
 3181 |             await query.answer("خطا!", show_alert=True)
 3182 | 
 3183 |         return
 3184 | 
```

**start.py:3885**
```
 3870 | 
 3871 |                     btns.append([InlineKeyboardButton("🔴 خاموش کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3872 | 
 3873 |                 else:
 3874 | 
 3875 |                     btns.append([InlineKeyboardButton("🟢 روشن کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3876 | 
 3877 |                 btns.append([InlineKeyboardButton("🗑️ حذف کامل جوین اجباری", callback_data="s_fj_del:" + str(uid) + ":" + str(chat_id))])
 3878 | 
 3879 |             else:
 3880 | 
 3881 |                 text += "❌ هنوز تنظیم نشده." + NL + NL
 3882 | 
 3883 |                 btns.append([InlineKeyboardButton("➕ تنظیم جوین اجباری", callback_data="s_fj_set:" + str(uid) + ":" + str(chat_id))])
 3884 | 
 3885 |             btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
 3886 | 
 3887 |             await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btns))
 3888 | 
 3889 |         except Exception as e:
 3890 | 
 3891 |             print("[FJ MENU ERR] " + str(e))
 3892 | 
 3893 |             await query.answer("خطا!", show_alert=True)
 3894 | 
 3895 |         return
 3896 | 
 3897 | 
 3898 | 
 3899 |     if action == "fj_toggle":
 3900 | 
```

**start.py:3969**
```
 3954 | 
 3955 |                     btns.append([InlineKeyboardButton("🔴 خاموش کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3956 | 
 3957 |                 else:
 3958 | 
 3959 |                     btns.append([InlineKeyboardButton("🟢 روشن کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
 3960 | 
 3961 |                 btns.append([InlineKeyboardButton("🗑️ حذف کامل جوین اجباری", callback_data="s_fj_del:" + str(uid) + ":" + str(chat_id))])
 3962 | 
 3963 |             else:
 3964 | 
 3965 |                 text += "❌ هنوز تنظیم نشده." + NL + NL
 3966 | 
 3967 |                 btns.append([InlineKeyboardButton("➕ تنظیم جوین اجباری", callback_data="s_fj_set:" + str(uid) + ":" + str(chat_id))])
 3968 | 
 3969 |             btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
 3970 | 
 3971 |             await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(btns))
 3972 | 
 3973 |         except Exception as e:
 3974 | 
 3975 |             print("[FJ TOGGLE ERR] " + str(e))
 3976 | 
 3977 |             await query.answer("خطا!", show_alert=True)
 3978 | 
 3979 |         return
 3980 | 
 3981 | 
 3982 | 
 3983 |     if action == "fj_set":
 3984 | 
```

**start.py:4448**
```
 4433 | 
 4434 |                 pass
 4435 | 
 4436 |             await query.answer("✅ بکاپ گرفته شد", show_alert=True)
 4437 | 
 4438 |             await query.edit_message_text(
 4439 | 
 4440 |                 "✅ بکاپ با موفقیت گرفته شد" + NL + "━━━━━━━━━━━━━━" + NL +
 4441 | 
 4442 |                 "📁 نام: " + _bk_name + NL +
 4443 | 
 4444 |                 "📊 حجم: " + str(_size) + " MB",
 4445 | 
 4446 |                 reply_markup=InlineKeyboardMarkup([
 4447 | 
 4448 |                     [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
 4449 | 
 4450 |                     [InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))]
 4451 | 
 4452 |                 ])
 4453 | 
 4454 |             )
 4455 | 
 4456 |         except Exception as e:
 4457 | 
 4458 |             print("[BACKUP ERR] " + str(e))
 4459 | 
 4460 |         return
 4461 | 
 4462 | 
 4463 | 
```

**start.py:6266**
```
 6251 |             _s = False if _o else is_bot_admin(user.id)
 6252 |             if not (_o or _s):
 6253 |                 await query.answer("⛔ فقط سازنده و سودو", show_alert=True)
 6254 |                 return
 6255 |         except Exception as _pe:
 6256 |             print("[FJ PERM ERR] " + str(_pe))
 6257 |         try:
 6258 |             from database import get_setting
 6259 |             _en = get_setting(0, "fj_enabled", "0") == "1"
 6260 |             _lnk = get_setting(0, "fj_link", "") or "(تنظیم نشده)"
 6261 |             _status = "✅ فعال" if _en else "❌ غیرفعال"
 6262 |             _txt = "🔒 جوین اجباری\n\n" + "وضعیت: " + _status + "\n🔗 لینک: " + _lnk
 6263 |             _kb_rows = [
 6264 |                 [InlineKeyboardButton(("❌ غیرفعال کردن" if _en else "✅ فعال کردن"), callback_data="fj_toggle_sudo:" + str(uid))],
 6265 |                 [InlineKeyboardButton("🔗 تنظیم لینک", callback_data="fj_setlink_sudo:" + str(uid))],
 6266 |                 [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
 6267 |             ]
 6268 |             await query.edit_message_text(_txt, reply_markup=InlineKeyboardMarkup(_kb_rows))
 6269 |         except Exception as e:
 6270 |             print("[FJ MENU ERR] " + str(e))
 6271 |         return
 6272 | 
 6273 |     if action == "fj_toggle_sudo":
 6274 |         try:
 6275 |             from database import get_setting, set_setting
 6276 |             _cur = get_setting(0, "fj_enabled", "0")
 6277 |             _new = "0" if _cur == "1" else "1"
 6278 |             set_setting(0, "fj_enabled", _new)
 6279 |             _en = _new == "1"
 6280 |             _lnk = get_setting(0, "fj_link", "") or "(تنظیم نشده)"
 6281 |             _status = "✅ فعال" if _en else "❌ غیرفعال"
```

**start.py:6286**
```
 6271 |         return
 6272 | 
 6273 |     if action == "fj_toggle_sudo":
 6274 |         try:
 6275 |             from database import get_setting, set_setting
 6276 |             _cur = get_setting(0, "fj_enabled", "0")
 6277 |             _new = "0" if _cur == "1" else "1"
 6278 |             set_setting(0, "fj_enabled", _new)
 6279 |             _en = _new == "1"
 6280 |             _lnk = get_setting(0, "fj_link", "") or "(تنظیم نشده)"
 6281 |             _status = "✅ فعال" if _en else "❌ غیرفعال"
 6282 |             _txt = "🔒 جوین اجباری\n\n" + "وضعیت: " + _status + "\n🔗 لینک: " + _lnk
 6283 |             _kb_rows = [
 6284 |                 [InlineKeyboardButton(("❌ غیرفعال کردن" if _en else "✅ فعال کردن"), callback_data="fj_toggle_sudo:" + str(uid))],
 6285 |                 [InlineKeyboardButton("🔗 تنظیم لینک", callback_data="fj_setlink_sudo:" + str(uid))],
 6286 |                 [InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))],
 6287 |             ]
 6288 |             await query.edit_message_text(_txt, reply_markup=InlineKeyboardMarkup(_kb_rows))
 6289 |             await query.answer("✅ فعال شد" if _en else "❌ غیرفعال شد")
 6290 |         except Exception as e:
 6291 |             print("[FJ TOGGLE ERR] " + str(e))
 6292 |         return
 6293 | 
 6294 |     if action == "fj_setlink_sudo":
 6295 |         await query.edit_message_text(
 6296 |             "🔗 برای تنظیم لینک، دستور زیر رو بفرست:\n\n"
 6297 |             "/setfjlink https://t.me/yourlink"
 6298 |         )
 6299 |         return
 6300 | 
 6301 |     if action == "s_op_sudo_stats":
```

**start.py:6322**
```
 6307 |             if not (_o or _s):
 6308 |                 await query.answer("⛔ فقط سازنده و سودو", show_alert=True)
 6309 |                 return
 6310 |             import sqlite3
 6311 |             conn = sqlite3.connect(DATABASE_PATH)
 6312 |             cur = conn.cursor()
 6313 |             cur.execute("SELECT user_id FROM bot_admins ORDER BY user_id")
 6314 |             admins = [r[0] for r in cur.fetchall()]
 6315 |             conn.close()
 6316 |             txt = "📊 آمار سودوها\n\n"
 6317 |             txt += "👥 تعداد: " + str(len(admins)) + "\n\n"
 6318 |             for aid in admins[:30]:
 6319 |                 txt += "• " + str(aid) + "\n"
 6320 |             if len(admins) > 30:
 6321 |                 txt += "... و " + str(len(admins) - 30) + " نفر دیگر"
 6322 |             _kb = [[InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))]]
 6323 |             await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(_kb))
 6324 |         except Exception as e:
 6325 |             print("[SUDO STATS ERR] " + str(e))
 6326 |         return
 6327 | 
 6328 |     if action == "s_op_group_stats":
 6329 |         try:
 6330 |             from config import OWNER_ID, DATABASE_PATH
 6331 |             from database import is_bot_admin
 6332 |             _o = (user.id == OWNER_ID)
 6333 |             _s = False if _o else is_bot_admin(user.id)
 6334 |             if not (_o or _s):
 6335 |                 await query.answer("⛔ فقط سازنده و سودو", show_alert=True)
 6336 |                 return
 6337 |             import sqlite3
```

**start.py:6350**
```
 6335 |                 await query.answer("⛔ فقط سازنده و سودو", show_alert=True)
 6336 |                 return
 6337 |             import sqlite3
 6338 |             conn = sqlite3.connect(DATABASE_PATH)
 6339 |             cur = conn.cursor()
 6340 |             cur.execute("SELECT chat_id, title FROM groups ORDER BY chat_id")
 6341 |             groups = cur.fetchall()
 6342 |             conn.close()
 6343 |             txt = "📈 آمار گروه‌ها\n\n"
 6344 |             txt += "🏠 تعداد: " + str(len(groups)) + "\n\n"
 6345 |             for cid, ttl in groups[:15]:
 6346 |                 _t = (ttl or str(cid))[:30]
 6347 |                 txt += "• " + _t + "\n  🆔 " + str(cid) + "\n"
 6348 |             if len(groups) > 15:
 6349 |                 txt += "... و " + str(len(groups) - 15) + " گروه دیگر"
 6350 |             _kb = [[InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))]]
 6351 |             await query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(_kb))
 6352 |         except Exception as e:
 6353 |             print("[GROUP STATS ERR] " + str(e))
 6354 |         return
 6355 | 
 6356 |     if action == "owner_section_menu":
 6357 |         # [SECURITY FIX] فقط سازنده/سودو
 6358 |         try:
 6359 |             from config import OWNER_ID
 6360 |             from database import is_bot_admin
 6361 |             _is_owner = (query.from_user.id == OWNER_ID)
 6362 |             _is_sudo = False
 6363 |             if not _is_owner:
 6364 |                 try:
 6365 |                     _is_sudo = is_bot_admin(query.from_user.id)
```

**start.py:6383**
```
 6368 |             if not (_is_owner or _is_sudo):
 6369 |                 await query.answer("\u26d4 \u0641\u0642\u0637 \u0633\u0627\u0632\u0646\u062f\u0647 \u0648 \u0633\u0648\u062f\u0648 \u062f\u0633\u062a\u0631\u0633\u06cc \u062f\u0627\u0631\u0646\u062f.", show_alert=True)
 6370 |                 return
 6371 |         except Exception as _pe:
 6372 |             print("[SECTION SEC ERR] " + str(_pe))
 6373 |             return
 6374 |         try:
 6375 |             await query.edit_message_text(
 6376 |                 "\U0001F527 \u0628\u062e\u0634 \u0633\u0627\u0632\u0646\u062f\u0647\n\n\u06af\u0632\u06cc\u0646\u0647 \u0645\u0648\u0631\u062f \u0646\u0638\u0631 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f:",
 6377 |                 reply_markup=owner_section_menu(query.from_user.id, query.message.chat.id)
 6378 |             )
 6379 |         except Exception as e:
 6380 |             print("[SECTION MENU ERR] " + str(e))
 6381 |         return
 6382 | 
 6383 |     if action == "owner_section_back":
 6384 |         # [SECURITY FIX] فقط سازنده/سودو
 6385 |         try:
 6386 |             from config import OWNER_ID
 6387 |             from database import is_bot_admin
 6388 |             _is_owner = (query.from_user.id == OWNER_ID)
 6389 |             _is_sudo = False
 6390 |             if not _is_owner:
 6391 |                 try:
 6392 |                     _is_sudo = is_bot_admin(query.from_user.id)
 6393 |                 except Exception:
 6394 |                     pass
 6395 |             if not (_is_owner or _is_sudo):
 6396 |                 await query.answer("\u26d4 \u0641\u0642\u0637 \u0633\u0627\u0632\u0646\u062f\u0647 \u0648 \u0633\u0648\u062f\u0648 \u062f\u0633\u062a\u0631\u0633\u06cc \u062f\u0627\u0631\u0646\u062f.", show_alert=True)
 6397 |                 return
 6398 |         except Exception:
```

**start.py:6861**
```
 6846 | 
 6847 |     app.add_handler(CommandHandler("lang", lang_cmd))
 6848 | 
 6849 |     app.add_handler(CommandHandler("rules", rules_cmd))
 6850 | 
 6851 |     app.add_handler(CommandHandler("id", id_cmd))
 6852 | 
 6853 |     app.add_handler(CommandHandler("restart", do_restart))
 6854 | 
 6855 |     app.add_handler(CommandHandler("refresh", do_refresh))
 6856 | 
 6857 |     app.add_handler(CommandHandler("config", do_refresh))
 6858 | 
 6859 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, persian_handler, block=False), group=7)
 6860 | 
 6861 |     app.add_handler(CallbackQueryHandler(handler, pattern="^(gowner_back|menu_back|menu_manage|menu_settings|menu_status|menu_owners|menu_admins|menu_vip|menu_deputies|menu_help|menu_close|menu_admin_perms|menu_deputy_perms|aperm|dperm|invite_unban_toggle|games_toggle|forces_|help_page_|set_lang_|pv_|pvc_|op_|sub_|vcall_|music_|purge_|nsfw_|nsub_|vsub_|msub_|rmt_|s_fj_|s_ba_|link_|s_panel_group|s_op_|s_backup|s_logs|s_restart_bot|s_sudo_stats|s_group_stats|osub_|rn_|greq_|gdur_|g_op_sub_|g_op_|pm_|g_back_panel|g_depset|g_ownerguide)|owner_section_menu|owner_section_back|sudo_panel_back|s_fj_menu|fj_toggle_sudo|fj_setlink_sudo|s_op_sudo_stats|s_op_group_stats|group_panel_back"), group=1)
 6862 | 
 6863 |     # Reports System
 6864 | 
 6865 |     try:
 6866 | 
 6867 |         from modules.reports import register as register_reports
 6868 | 
 6869 |         register_reports(app)
 6870 | 
 6871 |     except Exception as _re:
 6872 | 
 6873 |         print("[REPORTS REG ERR] " + str(_re))
```

**remote_groups.py:13**
```
    1 | from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    2 | 
    3 | NL = chr(10)
    4 | 
    5 | 
    6 | def remote_groups_menu(uid, chat_id=0):
    7 |     from database import get_all_bot_chats
    8 |     chats = get_all_bot_chats()
    9 |     btns = []
   10 |     for cid, title in chats[:30]:
   11 |         t = (title or "بدون نام")[:30]
   12 |         btns.append([InlineKeyboardButton("👥 " + t, callback_data="rmt_g:" + str(uid) + ":" + str(cid))])
   13 |     btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
   14 |     btns.append([InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))])
   15 |     return InlineKeyboardMarkup(btns)
   16 | 
   17 | 
   18 | def remote_group_menu(uid, target_chat_id):
   19 |     return InlineKeyboardMarkup([
   20 |         [InlineKeyboardButton("🔗 دریافت لینک دعوت", callback_data="rmt_link:" + str(uid) + ":" + str(target_chat_id))],
   21 |         [InlineKeyboardButton("📊 آمار گروه", callback_data="rmt_stat:" + str(uid) + ":" + str(target_chat_id))],
   22 |         [InlineKeyboardButton("📢 ارسال پیام به گروه", callback_data="rmt_msg:" + str(uid) + ":" + str(target_chat_id))],
   23 |         [InlineKeyboardButton("📌 ارسال و پین پیام", callback_data="rmt_pin:" + str(uid) + ":" + str(target_chat_id))],
   24 |         [InlineKeyboardButton("👥 لیست ادمین‌ها", callback_data="rmt_mem:" + str(uid) + ":" + str(target_chat_id))],
   25 |         [InlineKeyboardButton("🔙 بازگشت", callback_data="rmt_groups:" + str(uid) + ":" + str(target_chat_id))],
   26 |     ])
```


## بخش ۴: خطوط آخر start.py (برای پیدا کردن pattern اصلی)

```
 6794 | 
 6795 |             await query.edit_message_text(text, reply_markup=pv_chat_menu(uid, target_chat))
 6796 | 
 6797 |             reset_timer(context, chat_id, msg_id)
 6798 | 
 6799 |         except Exception:
 6800 | 
 6801 |             pass
 6802 | 
 6803 |         return
 6804 | 
 6805 | 
 6806 | 
 6807 |     if action == "pvc_manage":
 6808 | 
 6809 |         try:
 6810 | 
 6811 |             await query.edit_message_text("مدیریت گروه:", reply_markup=group_manage_menu(uid))
 6812 | 
 6813 |             reset_timer(context, chat_id, msg_id)
 6814 | 
 6815 |         except Exception:
 6816 | 
 6817 |             pass
 6818 | 
 6819 |         return
 6820 | 
 6821 | 
 6822 | 
 6823 |     if action == "pvc_settings":
 6824 | 
 6825 |         target_chat = extra if extra else chat_id
 6826 | 
 6827 |         try:
 6828 | 
 6829 |             await query.edit_message_text("تنظیمات:", reply_markup=group_settings_menu(uid, target_chat))
 6830 | 
 6831 |             reset_timer(context, chat_id, msg_id)
 6832 | 
 6833 |         except Exception:
 6834 | 
 6835 |             pass
 6836 | 
 6837 |         return
 6838 | 
 6839 | 
 6840 | 
 6841 | 
 6842 | 
 6843 | def register(app):
 6844 | 
 6845 |     app.add_handler(CommandHandler("start", start))
 6846 | 
 6847 |     app.add_handler(CommandHandler("lang", lang_cmd))
 6848 | 
 6849 |     app.add_handler(CommandHandler("rules", rules_cmd))
 6850 | 
 6851 |     app.add_handler(CommandHandler("id", id_cmd))
 6852 | 
 6853 |     app.add_handler(CommandHandler("restart", do_restart))
 6854 | 
 6855 |     app.add_handler(CommandHandler("refresh", do_refresh))
 6856 | 
 6857 |     app.add_handler(CommandHandler("config", do_refresh))
 6858 | 
 6859 |     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, persian_handler, block=False), group=7)
 6860 | 
 6861 |     app.add_handler(CallbackQueryHandler(handler, pattern="^(gowner_back|menu_back|menu_manage|menu_settings|menu_status|menu_owners|menu_admins|menu_vip|menu_deputies|menu_help|menu_close|menu_admin_perms|menu_deputy_perms|aperm|dperm|invite_unban_toggle|games_toggle|forces_|help_page_|set_lang_|pv_|pvc_|op_|sub_|vcall_|music_|purge_|nsfw_|nsub_|vsub_|msub_|rmt_|s_fj_|s_ba_|link_|s_panel_group|s_op_|s_backup|s_logs|s_restart_bot|s_sudo_stats|s_group_stats|osub_|rn_|greq_|gdur_|g_op_sub_|g_op_|pm_|g_back_panel|g_depset|g_ownerguide)|owner_section_menu|owner_section_back|sudo_panel_back|s_fj_menu|fj_toggle_sudo|fj_setlink_sudo|s_op_sudo_stats|s_op_group_stats|group_panel_back"), group=1)
 6862 | 
 6863 |     # Reports System
 6864 | 
 6865 |     try:
 6866 | 
 6867 |         from modules.reports import register as register_reports
 6868 | 
 6869 |         register_reports(app)
 6870 | 
 6871 |     except Exception as _re:
 6872 | 
 6873 |         print("[REPORTS REG ERR] " + str(_re))
```