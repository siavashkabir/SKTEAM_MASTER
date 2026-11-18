from telegram import BotCommand, MenuButtonCommands


async def setup_menu(app):
    commands = [
        BotCommand("start", "شروع و منوی اصلی"),
        BotCommand("lang", "تغییر زبان"),
        BotCommand("id", "نمایش آیدی"),
        BotCommand("rules", "قوانین گروه"),
    ]
    await app.bot.set_my_commands(commands)
    try:
        await app.bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    except Exception as e:
        print("Menu button error:", e)
    print("OK bot menu set")


def register(app):
    app.post_init = setup_menu
