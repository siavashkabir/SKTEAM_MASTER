from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from modules.nsfw import build_nsfw_sub_menu, build_nsfw_menu, get_nsfw_sub
from modules.nsfw import NL

async def nsfw_menu_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    print(f"[NSFW_MENU] Received: {data}")
    
    parts = data.split(":")
    action = parts[0]
    owner = int(parts[1]) if len(parts) >= 2 else 0
    chat_id = int(parts[2]) if len(parts) >= 3 else 0
    
    try:
        if action == "nsub_menu":
            await query.edit_message_text(
                "👤 اشتراک NSFW (سازنده):" + NL + NL +
                "برای فعال‌سازی اشتراک، با پشتیبانی تماس بگیرید.",
                reply_markup=build_nsfw_sub_menu(owner, chat_id)
            )
            await query.answer()
            return
        
        if action == "nsfw_menu":
            await query.edit_message_text(
                "⚙️ تنظیمات NSFW (مالک گروه):",
                reply_markup=build_nsfw_menu(owner, chat_id)
            )
            await query.answer()
            return
    except Exception as e:
        print(f"[NSFW_MENU ERR] {e}")
        await query.answer("خطا!", show_alert=True)

def register(app):
    app.add_handler(
        CallbackQueryHandler(nsfw_menu_cb, pattern="^(nsub_menu|nsfw_menu):"),
        group=-300
    )
    print("OK module nsfw_menu_handler loaded")
