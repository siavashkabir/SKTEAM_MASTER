import random
import time
import json
import urllib.request
import urllib.parse
from datetime import datetime
import jdatetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes
from database import get_member, is_bot_admin, is_group_owner, get_setting
from config import OWNER_ID, BOT_USERNAME

NL = chr(10)

KEYWORDS = ["ربات", "اسکای", "sky", "bot"]

OWNER_CALL_REPLIES = [
    # 🫡 خفن و باکلاس
    "سیاوش، سازنده‌ی مقتدر اسکای‌تیم، جانم بفرمایید 🫡",
    "جانم سیاوش سازنده! فقط منو صدا بزن، مخلصتم 💚",
    "سیاوش، پادشاه این ربات، امر بفرمایید 👑",
    "سازنده سیاوش عزیز، در خدمتم 🫡",
    "سیاوش جان، ما همه سرباز تو هستیم، بفرما ⚔️",
    "سیاوش سازنده، تو فرمانده‌ی منی، بفرما 🎖️",
    "سیاوش، سلطان اسکای‌تیم، جانم بفرمایید 🌟",
    "جانم سیاوش سازنده، من مطیع امرتم 🫡",
    "سیاوش عزیز، سازنده‌ی توانا، بفرما 🏆",
    "سیاوش، افتخار اسکای‌تیم، در خدمتم 💎",
    
    # 😂 طنز و بامزه
    "سیاوش سازنده، درد و بلات بخوره تو سر من، چی شده؟ 🤣",
    "جونم سیاوش! باز چی خراب کردی که صدام می‌زنی؟ 😂",
    "سیاوش جان، تو فقط منو صدا بزن، من از این کارا خوشم میاد 😏",
    "سیاوش سازنده، باز چی تو سرت داری که من باید حلش کنم؟ 🤔",
    "ای جانم سیاوش! باز دلت هوای منو کرد؟ 🥺",
    "سیاوش جان، این‌قدر منو صدا نزن، خجالت می‌کشم 🙈",
    "سیاوش سازنده، من عاشقتم ولی بذار یه نفس بکشم 😂",
    "سیاوش جان، از خوشحالی دارم بال درمیارم 🕊️",
    "سیاوش، تو یه نقشه‌ای تو سر داری، قبول کن 😏",
    "سیاوش جان، باز چه گلی به سرم زدی؟ 🌸",
    "سیاوش سازنده، باز داری منو امتحان می‌کنی؟ 🎭",
    "سیاوش جان، این‌قدر شیرین صدام نزن، دیوونه می‌شم 🤪",
    "سیاوش، من از این‌که صدام زدی شوکه‌ام 😲",
    "سیاوش جان، چه بادی به کاهدان خورد؟ 🌬️",
    "سیاوش سازنده، باز منو یاد کردی؟ خوشحالم 🥳",
    "سیاوش جان، تو گفتی من اطاعت، بفرما 🫡",
    
    # 🍻 رفاقتی و باحال
    "سیاوش جان، تو رفیق فابریک منی، بفرما 🤜🤛",
    "جانم سیاوش! چی شده رفیق؟ 🍻",
    "سیاوش داداش، بگو ببینم چی می‌خوای 😎",
    "سیاوش جان، من کشته مرده‌اتم، بفرما 🌹",
    "سیاوش، تو بگو من انجام می‌دم، سازنده‌ی گلم 💪",
    "سیاوش جان، تو بهترین رفیقی، بفرما 🤝",
    "سیاوش سازنده، من و تو یه تیمیم، بفرما 🎯",
    "سیاوش جان، من پایه‌ی هر شیطونی‌ام 😈",
    "سیاوش، تو بگی من می‌رسونم 🚚",
    "سیاوش جان، حاضرم برات آتیش روشن کنم 🔥",
    "سیاوش سازنده، تو بگو من تا آخرش می‌رم 🏁",
    
    # 🔥 خفن و به سبک اسکای‌تیم
    "ما مالک اسکای‌تیم سیاوش، جانم جون بخواه! 🫡",
    "سیاوش، سازنده‌ی افسانه‌ای، من در خدمتم 🏆",
    "سیاوش جان، تو ستاره‌ی اسکای‌تیمی، بفرما 🌟",
    "سیاوش سازنده، از این‌که صدام زدی کل ربات داره می‌رقصه 💃",
    "سیاوش، پادشاه ربات‌ها، امر بفرما ⚡",
    "سیاوش، قهرمان اسکای‌تیم، بفرما 🦸",
    "سیاوش جان، تو اسطوره‌ی منی، بفرما 🐉",
    "سیاوش سازنده، تو افتخار ما هستی، امر بفرما 🏅",
    "سیاوش، سردار اسکای‌تیم، جانم بفرمایید ⚔️",
    "سیاوش جان، تو تک‌تاز میدانی، بفرما 🏇",
    
    # 🎭 ترکیبی (اسم + سازنده + طنز)
    "سیاوش سازنده، باز چه نقشه‌ای تو سر داری؟ 😏",
    "سیاوش جان، تو گفتی من اطاعت، بفرما 🫡",
    "سیاوش سازنده، این‌قدر شیرین صدام نزن، دیوونه می‌شم 🤪",
    "سیاوش، سازنده‌ی عزیزم، بفرما من تمام گوشم 👂",
    "سیاوش جان، حاضرم برات دنیا رو بگردم 🌍",
    "سیاوش سازنده، تو بگو، من می‌دونم چطور انجامش بدم 💡",
    "سیاوش جان، باز دل منو لرزوندی 💓",
    "سیاوش، تو بگی من می‌رسونم 🚀",
    "سیاوش سازنده، من آماده‌ی هر مأموریتی‌ام 🎯",
    "سیاوش جان، تو فقط بگو، من انجام می‌دم ✨",
    
    # 💚 عاطفی و صمیمی
    "سیاوش جان، از دیدن اسمت ذوق کردم، بفرما 🥰",
    "سیاوش سازنده، صدات آرامشه، باز بگو 🧘",
    "سیاوش جان، تو بهترین سازنده‌ی دنیایی، بفرما 🏆",
    "سیاوش، دل من با اسم تو می‌لرزه، بفرما 💓",
    "سیاوش جان، من همیشه کنارتم، بفرما 🤝",
    "سیاوش عزیز، صدای تو مثل آهنگه، باز بگو 🎵",
    "سیاوش جان، از این‌که صدام زدی، پر انرژی شدم ⚡",
    "سیاوش، تو گل گلی، من گل‌آبم 🌷",
    "سیاوش جان، از خوشحالی دارم پرواز می‌کنم 🛫",
    "سیاوش، صدات مثل عسله، باز بگو 🍯",
    "سیاوش جان، من نوکرتم از سر تا پا 🫶",
    "سیاوش، تو ستاره‌ی این گروهی، بفرما 🌟",
    "سیاوش جان، این‌قدر مهربون صدام نزن، آب می‌شم 🫠",
    "سیاوش سازنده، تو بهترینی، بفرما 💎",
    "سیاوش جان، حاضرم برات ستاره هم بچینم ⭐",
]

NICK_CALL_TEMPLATES = [
    "آقای {nick} جانم بفرمایید 🌹",
    "{nick} جان، جون به لبم کردی، بفرما! 😄",
    "جانم {nick} عزیز؟ 💚",
    "بله {nick} جان؟ 😊",
    "{nick} جان، در خدمتم! 🫡",
    "{nick} جان، تو فقط منو صدا بزن، من عاشق این کارم 😏",
    "جونم {nick}؟ چته؟ 😂",
    "{nick} جان، باز چی شده که صدای منو در آوردی؟ 🤔",
    "جانم {nick}؟ انگار یکی ناز شصتش شده! 😄",
    "{nick} جان، بفرما، من که همیشه پایتم 💪",
    "ای جانم! {nick} چی می‌خواد از جون ما؟ 😅",
    "{nick} جان، این‌قدر منو صدا نزن، خجالت می‌کشم 🙈",
    "بله بله {nick} جان، امر بفرما 🫡",
    "{nick} جان، من عاشقتم ولی بذار یه نفس بکشم 😂",
    "{nick} عزیز، بفرمایید در خدمتم 🌹",
    "{nick} جان، تا تو صدام کنی، کل گروه رو به هم می‌ریزم 😎",
    "بله {nick}؟ انگار کار واجبی داری! 🤔",
    "{nick} جان، صدات کردم که یادم نره چقدر باحالی 🥰",
    "جانم {nick}! باز چه نقشه‌ای تو سر داری؟ 😏",
    "{nick} جان، من حاضرم برای تو از دیوار هم بالا برم 🧗",
    "بله {nick} جان؟ بگو ببینم چه خبر؟ 📰",
    "{nick} جان، دست از سرم بردار، دارم فکر می‌کنم 🤣",
    "جونم {nick}؟ امروز چقدر خوش‌صدایی! 🎤",
    "{nick} جان، بفرمایید، من نوکرتم 💚",
    "ای جانم {nick}! صدات که میاد، دلم قنج می‌ره 🥺",
    "{nick} جان، من پایه‌ی هر کاری هستم، فقط بگو 😎",
    "بله {nick} جان؟ چه خدمتی از دستم برمیاد؟ 🫡",
    "{nick} جان، باز منو صدا زدی؟ یعنی من اینقدر دوست‌داشتنی‌ام؟ 🤭",
    "{nick} جان، بفرمایید، من در خدمتم و آماده‌ی کمک 🚀",
    "جونم {nick}؟ از این‌که صدام می‌زنی خوشحالم 🎉",
    "{nick} جان، حاضرم شب و روز بهت خدمت کنم ⭐",
    "بله {nick}؟ باز چه خبره که این‌قدر عجله داری؟ 🏃",
    "{nick} جان، از صدای تو انرژی می‌گیرم 🔋",
    "جانم {nick} عزیز؟ من همیشه کنارتم 🤝",
    "{nick} جان، بفرمایید، من تمام گوشم 👂",
    "{nick} جان، صدات نوازش روحه، باز بگو 🎵",
    "بله {nick} جان؟ من حاضرم برای تو هر کاری کنم 💫",
    "{nick} جان، این‌قدر شیرین صدام نزن، دیوونه می‌شم 😍",
    "جونم {nick}! باز چه توطئه‌ای داری؟ 🕵️",
    "{nick} جان، من همیشه پایه‌اتم، بفرما 💯",
    "{nick} جان، الان می‌رسونم هرچی می‌خوای 🏎️",
    "بله {nick} جان؟ باز قلبم لرزید از صدات 💓",
    "{nick} جان، من هنوز از این‌که صدام زدی شوکه‌ام 😲",
    "جانم {nick}؟ چه بادی به کاهدان خورد؟ 🌬️",
    "{nick} جان، تو رفیق فابریک منی، بفرما 🤜🤛",
    "{nick} جان، من کشته مرده‌اتم، بفرما 🌹",
    "بله {nick} جان؟ از خوشحالی دارم بال درمیارم 🕊️",
    "{nick} جان، می‌دونی چقدر دوستت دارم؟ 💖",
    "جونم {nick}؟ باز داری منو امتحان می‌کنی؟ 🎭",
    "{nick} جان، من آماده‌ی هر مأموریتی‌ام 🎯",
    "{nick} جان، صدای تو مثل آهنگه، باز بگو 🎶",
    "بله {nick}؟ من که همیشه پایه‌تم، بفرما 🫡",
    "{nick} جان، از این‌که صدام زدی، دلم غنج رفت 💐",
    "جانم {nick} عزیز؟ هرچی بگی همون می‌شه ✨",
    "{nick} جان، من و تو یه تیمیم، بفرما 🤝",
    "{nick} جان، تو بگو، من انجام می‌دم 💪",
    "بله {nick} جان؟ باز دلت هوای منو کرد؟ 🥰",
    "{nick} جان، این‌قدر شیرین منو صدا نزن، دیوونه میشم 🤪",
    "جونم {nick}؟ چی شده که باز یاد من افتادی؟ 🤔",
    "{nick} جان، بفرما، من که همیشه بیدارم برای تو 🌙",
    "{nick} جان، صدات مثل عسله، باز بگو 🍯",
    "بله {nick}؟ امر بفرما، در خدمتم 🫡",
    "{nick} جان، من حاضرم برات ستاره هم بچینم ⭐",
    "{nick} جان، تو ستاره‌ی این گروهی، بفرما 🌟",
    "جانم {nick}؟ من که همیشه گوش به فرمانتم 🎧",
    "{nick} جان، از خوشحالی دارم می‌رقصم 💃",
    "{nick} جان، صدات که میاد، دنیام روشن می‌شه ☀️",
    "بله {nick} جان؟ باز چه نقشه‌ای داری تو سرت؟ 🗺️",
    "{nick} جان، من حاضرم برات قهرمان بشم 🦸",
    "جونم {nick}؟ باز چه گلی به سرم زدی؟ 🌸",
    "{nick} جان، تو بهترینی، بفرما 🏆",
    "{nick} جان، از این‌که صدام زدی، پر انرژی شدم ⚡",
    "بله {nick} جان؟ من آماده‌ی خدمتم 🎖️",
    "{nick} جان، تو بگو، من می‌دونم چیکار کنم 🧠",
    "{nick} جان، صدات دل منو برده 💘",
    "جانم {nick}؟ باز دل منو لرزوندی 💓",
    "{nick} جان، تو بگی، من می‌رسونم 🚚",
    "{nick} جان، من حاضرم برات دنیا رو بگردم 🌍",
    "بله {nick} جان؟ من که همیشه بیدارم برای تو 🌛",
    "{nick} جان، این‌قدر مهربون صدام نزن، آب می‌شم 🫠",
    "جونم {nick}؟ باز منو یاد کردی؟ خوشحالم 🥳",
    "{nick} جان، تو گل گلی، من گل‌آبم 🌷",
    "{nick} جان، صدات آرامشه، باز بگو 🧘",
    "بله {nick} جان؟ از خوشحالی دارم پرواز می‌کنم 🛫",
    "{nick} جان، من نوکرتم از سر تا پا 🦶",
    "{nick} جان، تو فقط بگو، من انجام می‌دم 🎯",
    "جانم {nick}؟ باز چه آرزویی داری؟ 🌠",
    "{nick} جان، من پایه‌ی هر شیطونی‌ام 😈",
    "{nick} جان، صدات انرژی مثبته، باز بگو 🔆",
    "بله {nick} جان؟ من همیشه پایه‌ی کمکم 🤗",
    "{nick} جان، تو بگو، من می‌دونم چطور انجامش بدم 💡",
    "{nick} جان، از دیدن اسمت ذوق کردم 🎊",
    "جونم {nick}؟ باز چه خبر خوشی داری؟ 🎁",
    "{nick} جان، من حاضرم برات آتیش روشن کنم 🔥",
    "{nick} جان، تو بگی، من تا آخرش می‌رم 🏁",
    "بله {nick} جان؟ باز چه نقشه‌ای داری؟ 🎨",
]

CALL_REPLIES = [
    "جانم عزیزم؟ چیکارم داری؟",
    "بله بله؟ در خدمتم!",
    "چیه باز صدام زدی؟",
    "سلام سلام! چطور میتونم کمکت کنم؟",
    "بله؟ چیزی لازم داری؟",
    "در خدمتم قربان!",
    "بله جانم؟ بفرمایید!",
    "چی شده؟ باز منو میخوای؟",
    "جانم؟ بگو دیگه!",
    "بله؟ گوشم با شماست!",
    "من اینجام! چیکار داری؟",
    "چه خبر؟ باز پای من وسطه؟",
    "بله بله؟ باز چی میخوای از من؟",
    "جانم؟ اگه کاری داری بگو دیگه!",
    "چشم! در خدمتم!",
    "بله؟ سریع بگو که وقت ندارم!",
    "جانم عزیز دل؟",
    "بله؟ بگو ببینم چی میخوای",
    "در خدمتم! امر بفرمایید!",
]

HAFEZ = [
    "دوش دیدم که ملائک در میخانه زدند" + NL + "گل آدم بسرشتند و به پیمانه زدند",
    "بیا تا گل برافشانیم و می در ساغر اندازیم" + NL + "فلک را سقف بشکافیم و طرحی نو دراندازیم",
    "در این شب سیاهم گم گشت راه مقصود" + NL + "از گوشه ای برون آی ای کوکب هدایت",
    "هر که را با خط سبزت سر سودا باشد" + NL + "پای از این دایره بیرون ننهد تا باشد",
    "بیا که قصر امل سخت سست بنیاد است" + NL + "بیار باده که بنیاد عمر بر باد است",
    "دلا بسوز که سوز تو کارها بکند" + NL + "نیاز نیم شبی دفع صد بلا بکند",
    "ما در پیاله عکس رخ یار دیده ایم" + NL + "ای بی خبر ز لذت شرب مدام ما",
    "دوش از مسجد سوی میخانه آمد پیر ما" + NL + "چیست یاران طریقت بعد از این تدبیر ما",
]

BIOS = {
    "عاشقانه": [
        "دلم گرفته از این دنیای بی وفا، فقط تو میمونی و یه فنجون چای",
        "عاشقتم به اندازه تمام ستاره های آسمون",
        "تو قلبم جا داری، مثل خونه ای که هیچوقت ترکش نمیکنم",
        "یه روز میام سراغت، حتی اگه پشت کوه قاف باشی",
        "قلبم فقط برای تو میزنه، بقیه فقط تماشاچی ان",
        "تو مثل بارون پاییزی، همیشه دلم برات تنگ میشه",
        "عشق تو مثل یه ترانه قدیمیه که هیچوقت از یادم نمیره",
        "اگه یه آرزو داشتم، فقط یه بار دیگه دیدنت بود",
    ],
    "طنز": [
        "من عاشق خوابم، ولی زندگی بیدارم میکنه",
        "تنها رابطه ای که توش موفقم، با یخچاله",
        "من یه موجود پیچیده ام، پیچیده تر از سیم هدفون",
        "اگه تنبلی ورزش بود، من المپیک میبردم",
        "زندگیم شبیه وای فایه، آنتنم کمه ولی وصلم",
        "من عاشق ورزشم، مخصوصاً حرکات دست موقع عوض کردن کانال",
        "همیشه میگم فردا، ولی فردا هیچوقت نمیاد",
        "تنها چیزی که تو زندگیم منظمه، بی نظمی هامه",
    ],
    "انگیزشی": [
        "هر روز یه فرصت جدیده برای بهتر شدن، پس دریابش",
        "موفقیت یه مسیره، نه یه مقصد، پس ادامه بده",
        "اگه امروز سخته، بدون فردا قشنگتره",
        "زندگی شبیه دوچرخه سواریه، برای تعادل باید حرکت کنی",
        "هیچوقت ناامید نشو، شاید قشنگترین صفحه، آخر کتاب باشه",
        "تو قوی تر از اون چیزی هستی که فکر میکنی",
        "رویاهات رو باور کن، چون تنها راه رسیدن بهشونه",
        "از خودت شروع کن، دنیا خودش خودش رو درست میکنه",
    ],
    "خاص": [
        "من یه انسان معمولی ام با یه دنیای غیرمعمولی",
        "گاهی ساکت میشم، نه از بی حرفی، از پر حرفی درونم",
        "من اونیم که هستم، نمیخوام شبیه کسی باشم",
        "زندگیم رو خودم مینویسم، حتی اگه خط خطی باشه",
        "یه کتاب نیمه خونده، یه قهوه سرد، و یه فکر گرم",
        "من با تو فرق دارم، ولی بدون تو یه نقطه ام",
    ],
    "غمگین": [
        "گاهی سکوت، بلندترین فریاده",
        "قلبم پاییزیه، حتی تو تیرماه",
        "دلم برای روزهایی تنگ شده که هنوز نرفته بودن",
        "من از اونایی ام که پشت لبخندشون یه دنیا حرف پنهونه",
        "بعضی زخما با گذر زمان خوب نمیشن، فقط عادت میشن",
        "بارون که میباره، یاد بعضی خاطرات میفتم",
    ],
}


def normalize(text):
    return text.replace(" ", "").replace("\u200c", "").lower()


def get_bio_menu(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("عاشقانه", callback_data="bio_عاشقانه:" + str(uid)),
         InlineKeyboardButton("طنز", callback_data="bio_طنز:" + str(uid))],
        [InlineKeyboardButton("انگیزشی", callback_data="bio_انگیزشی:" + str(uid)),
         InlineKeyboardButton("خاص", callback_data="bio_خاص:" + str(uid))],
        [InlineKeyboardButton("غمگین", callback_data="bio_غمگین:" + str(uid))],
        [InlineKeyboardButton("بستن", callback_data="bio_close:" + str(uid))],
    ])


def fetch_weather(city):
    try:
        url = "https://wttr.in/" + urllib.parse.quote(city) + "?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        current = data["current_condition"][0]
        return {
            "temp": current["temp_C"],
            "feels": current["FeelsLikeC"],
            "humidity": current["humidity"],
            "desc": current["weatherDesc"][0]["value"],
        }
    except Exception:
        return None


async def is_admin(chat, user_id):
    try:
        if user_id == OWNER_ID:
            return True
        if is_bot_admin(user_id):
            return True
    except Exception:
        pass
    try:
        member = await chat.get_member(user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False


async def send_user_info(msg, context, chat, target):
    member = get_member(chat.id, target.id)
    name = target.first_name or "بدون نام"
    uname = ("@" + target.username) if target.username else "ندارد"
    if member:
        join_date = member[2] or "ثبت نشده"
        msg_count = member[3] or 0
    else:
        join_date = "ثبت نشده"
        msg_count = 0

    caption = (
        "مشخصات کاربر" + NL +
        "━━━━━━━━━━━━━━━━━━" + NL +
        "نام: " + name + NL +
        "یوزرنیم: " + uname + NL +
        "آیدی عددی: " + str(target.id) + NL +
        "تاریخ ورود: " + str(join_date) + NL +
        "تعداد پیام: " + str(msg_count)
    )

    try:
        photos = await context.bot.get_user_profile_photos(target.id, limit=1)
        if photos and photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            await msg.reply_photo(photo=file_id, caption=caption)
            return
    except Exception as e:
        print("[PHOTO ERR] " + str(e))

    await msg.reply_text(caption)


async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return

    text = msg.text or ""
    if not text:
        return

    print("[MSG] " + text)

    if chat.type not in ("private", "group", "supergroup"):
        return
    IS_PV = (chat.type == "private")


    t_low = text.lower().strip()
    # ★ هندلر پاکسازی (شروع پاکسازی ۱۰۰ / حذف ۱۰۰)
    import re as _re
    _purge_match = _re.match(r'^(شروع پاکسازی|حذف|پاکسازی)\s+(\d+)$', t_low.strip())
    if _purge_match:
        try:
            _count = int(_purge_match.group(2))
            if _count < 1 or _count > 1000:
                await msg.reply_text("❌ عدد باید بین ۱ تا ۱۰۰۰ باشه.")
                return
            # چک ادمین
            try:
                _member = await chat.get_member(user.id)
                if _member.status not in ("creator", "administrator"):
                    await msg.reply_text("❌ فقط ادمین‌ها می‌تونن پاکسازی کنن.")
                    return
            except Exception:
                pass
            # حذف پیام دستور
            try:
                await msg.delete()
            except Exception:
                pass
            # پاک کردن count پیام
            _deleted = 0
            _msg_id = msg.message_id
            _ids = list(range(_msg_id, max(0, _msg_id - _count), -1))
            for _i in range(0, len(_ids), 100):
                _chunk = _ids[_i:_i+100]
                try:
                    await context.bot.delete_messages(chat.id, _chunk)
                    _deleted += len(_chunk)
                except Exception as _e:
                    print(f"[PURGE TEXT] chunk err: {_e}")
                    for _mid in _chunk:
                        try:
                            await context.bot.delete_message(chat.id, _mid)
                            _deleted += 1
                        except Exception:
                            pass
            # پیام تایید
            _info = await context.bot.send_message(chat.id, f"🗑️ {_deleted} پیام پاک شد.")
            import asyncio as _aio
            async def _del_later_p():
                await _aio.sleep(5)
                try:
                    await _info.delete()
                except Exception:
                    pass
            _aio.create_task(_del_later_p())
            print(f"[PURGE TEXT] {_deleted} پیام پاک شد توسط {user.id}")
            return
        except Exception as _e:
            print(f"[PURGE TEXT ERR] {_e}")
            return

    # [MOD-INLINE]
    if chat.type in ("group", "supergroup"):
        try:
            _tl = text.lower().strip()
            _trigs = {
                "ban": ["بن", "ban", "اخراج", "سیک", "مسدود", "کیک"],
                "unban": ["آنبن", "unban", "آزادش کن", "آزادش‌کن", "آزادش", "بخشیدمت", "رفع بن", "رهایی", "آزادی", "آزاد کن"],
                "mute": ["سکوت", "mute", "میوت", "خفه شو", "خفه", "ساکت", "دهنتو ببند"],
                "unmute": ["رفع سکوت", "رفع‌سکوت", "حذف سکوت", "آزادش کن", "unmute", "آزادش", "باز کن"],
            }
            _matched = False
            _matched_action = None
            for _k, _lst in _trigs.items():
                for _t in _lst:
                    # تطابق دقیق یا شروع
                    if _tl == _t or _tl.startswith(_t + " ") or _tl.startswith(_t + "\u200c"):
                        _matched = True
                        _matched_action = _k
                        break
                if _matched: break
            if _matched:
                print("[MOD-INLINE] matched: " + str(_matched_action))
                from modules.moderation import moderation_handler as _mh
                await _mh(update, context)
                return
        except Exception as _me:
            print("[MOD-INLINE ERR] " + str(_me))
    # [MOD-INLINE-END]




    t_low_clean = t_low.replace(chr(0x200c), "").replace(chr(0x200f), "").replace(chr(0x200e), "").replace(chr(0x200b), "").strip()

    # [NEW-TRIGGERS-V3]
    try:
        from modules.fun_data import RIDDLES, POEMS, JOKES, TRUTHS, DARES
    except Exception as _fe:
        print("[FUN DATA ERR] " + str(_fe))
        RIDDLES = POEMS = JOKES = TRUTHS = DARES = ["..."]

    if "معما" in t_low or "riddle" in t_low:
        try:
            await msg.reply_text("🧩 " + random.choice(RIDDLES))
        except Exception: pass
        return

    if "جوک" in t_low or "joke" in t_low:
        try:
            await msg.reply_text("😂 " + random.choice(JOKES))
        except Exception: pass
        return

    if "شعر" in t_low or "poem" in t_low or "poetry" in t_low:
        try:
            await msg.reply_text("🌸 " + random.choice(POEMS))
        except Exception: pass
        return

    if "قرعه" in t_low or "lottery" in t_low:
        try:
            await msg.reply_text("🎲 قرعه‌کشی:" + NL + NL + "عدد: " + str(random.randint(1, 100)))
        except Exception: pass
        return

    if "حدس" in t_low or "guess" in t_low:
        try:
            parts = t_low.split()
            has_num = any(p.isdigit() for p in parts)
            if not hasattr(__import__(__name__), "_GUESS_STATE"):
                __import__(__name__)._GUESS_STATE = {}
            gs = getattr(__import__(__name__), "_GUESS_STATE")
            if not has_num:
                gs[user.id] = random.randint(1, 100)
                await msg.reply_text("🎯 حدس بزن!" + NL + "عدد ۱ تا ۱۰۰:" + NL + "مثال: حدس ۵۰")
            else:
                target = gs.get(user.id)
                if not target:
                    await msg.reply_text("❌ اول «حدس» رو بزن.")
                else:
                    for p in parts:
                        if p.isdigit():
                            n = int(p)
                            if n == target:
                                await msg.reply_text("🎉 آفرین! درست: " + str(n))
                                gs.pop(user.id, None)
                            elif n < target:
                                await msg.reply_text("⬆️ بزرگ‌تر")
                            else:
                                await msg.reply_text("⬇️ کوچک‌تر")
                            break
        except Exception: pass
        return

    if "جرئت" in t_low or "جرأت" in t_low or "حقیقت" in t_low or "truth" in t_low or "dare" in t_low:
        try:
            if "جرئت" in t_low or "جرأت" in t_low or "dare" in t_low:
                await msg.reply_text("😈 " + random.choice(DARES))
            else:
                await msg.reply_text("🤔 " + random.choice(TRUTHS))
        except Exception: pass
        return

    if t_low in ("راهنما", "help", "دستورات", "commands"):
        HELP = ("📖 راهنمای Sk.Team" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
                "👤 «آیدی» / «اطلاعات» / «قوانین»" + NL +
                "🕐 «ساعت» / «تاریخ» / «تقویم»" + NL +
                "🎮 «فال» / «جوک» / «شعر» / «معما»" + NL +
                "🎲 «سکه» / «قرعه» / «حدس»" + NL +
                "😈 «جرئت» / «حقیقت»" + NL +
                "📝 مدیریت: «بن» / «سکوت» / «اخطار»")
        try:
            await msg.reply_text(HELP)
        except Exception: pass
        return

    if t_low_clean in ("بیو", "bio", "بیوگرافی", "بیوگرافى"):
        try:
            out = ("📝 بخش بیوگرافی" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
                   "یه گزینه انتخاب کن:")
            await msg.reply_text(out, reply_markup=get_bio_menu(user.id))
        except Exception:
            try: await msg.reply_text("📝 بخش بیوگرافی")
            except Exception: pass
        return
    if t_low_clean in ("بیو ربات", "بیوگرافی ربات", "درباره ربات", "about bot"):
        BIO = ("🤖 Sk.Team Manager" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
               "🎯 قوی‌ترین ربات مدیریت گروه تلگرام" + NL + NL +
               "✨ قابلیت‌های اصلی:" + NL +
               "• مدیریت کامل اعضا و ادمین‌ها" + NL +
               "• ضد اسپم، ضد لینک، ضد رید" + NL +
               "• سیستم اخطار (Warning)" + NL +
               "• جوین اجباری (FJ)" + NL +
               "• خوش‌آمدگویی حرفه‌ای" + NL +
               "• بازی و سرگرمی (کوییز، حقیقت یا جرئت)" + NL +
               "• دستیار هوش مصنوعی" + NL +
               "• فیلتر NSFW" + NL + NL +
               "💎 اشتراک‌ها: موزیک، رکورد، NSFW" + NL +
               "👨‍💻 سازنده: @Siavashska" + NL +
               "📅 نسخه: 1.1" + NL + NL +
               "📢 کانال Sk.Team: @Skteamchnl" + NL +
               "💎 پشتیبانی: @Siavashska")
        try:
            await msg.reply_text(BIO)
        except Exception: pass
        return
    # [NEW-TRIGGERS-V3-END]
    t_norm = normalize(text)
    bot_username = (context.bot.username or "").lower()
    is_mentioned = ("@" + bot_username) in t_low

    # پنل پی وی
    pv_triggers_norm = ["پنلپیوی", "پنلpv", "panelpv", "پنلخصوصی", "panelprivate"]
    if t_norm in pv_triggers_norm:
        try:
            is_creator = False
            try:
                m = await chat.get_member(user.id)
                if m.status == "creator":
                    is_creator = True
            except Exception:
                pass
            allowed = (user.id == OWNER_ID) or is_bot_admin(user.id) or is_creator or is_group_owner(chat.id, user.id)
            if not allowed:
                return
            bot_username_clean = BOT_USERNAME.replace("@", "")
            url = "https://t.me/" + bot_username_clean + "?start=pv_" + str(chat.id)
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("دریافت پنل در پی وی", url=url)],
            ])
            await msg.reply_text(
                "برای دریافت پنل در پی وی، روی دکمه زیر بزنید:" + NL + NL +
                "پنل شامل مدیریت و تنظیمات این گروهه.",
                reply_markup=kb
            )
        except Exception as e:
            print("[PANEL PV ERR] " + str(e))
        return

    # پنل - تشخیص دقیق نقش
    if t_norm in ("پنل", "panel"):
        # [PER-USER PANEL GUARD] بستن پنل قدیمی + باز کردن پنل جدید
        try:
            from modules.start import ACTIVE_PANELS
            _key = (user.id, chat.id)
            _old_panel = ACTIVE_PANELS.pop(_key, None)
            if _old_panel:
                print(f"[PANEL GUARD] Deleting old panel msg={_old_panel} for user {user.id}")
                try:
                    await context.bot.delete_message(chat_id=chat.id, message_id=_old_panel)
                except Exception as _de:
                    print(f"[PANEL GUARD] Old panel already deleted: {_de}")
                # فقط در این حالت، پیام "پنل" کاربر هم پاک میشه
                try:
                    await msg.delete()
                except Exception:
                    pass
        except Exception as _e:
            print("[PANEL GUARD ERR] " + str(_e))

        # تشخیص نقش
        is_sudo_user = False
        try:
            if user.id == OWNER_ID:
                is_sudo_user = True
            elif is_bot_admin(user.id):
                is_sudo_user = True
        except Exception:
            pass
        is_gowner_user = is_group_owner(chat.id, user.id)
        is_tg_admin = await is_admin(chat, user.id)

        # هیچکدوم نباشه → نادیده بگیر
        if not is_sudo_user and not is_gowner_user and not is_tg_admin:
            return

        
        try:
            from modules.start import (
                sudo_panel_menu, group_owner_panel_menu, group_panel_menu, reset_timer
            )
            if is_sudo_user:
                # سازنده ربات / سودو → پنل کامل
                sent = await msg.reply_text(
                    "پنل سازنده ربات - بخش مورد نظر:",
                    reply_markup=sudo_panel_menu(user.id, chat.id)
                )
            elif is_gowner_user:
                # مالک گروه → پنل بدون اشتراک و ادمین ربات
                sent = await msg.reply_text(
                    "پنل مالک گروه - بخش مورد نظر:",
                    reply_markup=group_owner_panel_menu(user.id, chat.id)
                )
            else:
                # ادمین تلگرام → پنل محدود
                sent = await context.bot.send_message(chat_id=chat.id, text=
                    "منوی اصلی - بخش مورد نظر:",
                    reply_markup=group_panel_menu(user.id)
                )
            reset_timer(context, sent.chat_id, sent.message_id)
            # [PER-USER PANEL GUARD] Register
            try:
                from modules.start import ACTIVE_PANELS
                ACTIVE_PANELS[(user.id, chat.id)] = sent.message_id
                print(f"[PANEL GUARD] Registered msg={sent.message_id}")
            except Exception as _re:
                print("[PANEL GUARD REG ERR] " + str(_re))
        except Exception as e:
            print("[PANEL ERR] " + str(e))
        return

    # بیوگرافی
    _bio_clean = t_low.replace("\u200c", "").replace("\u200f", "").replace("\u200e", "").replace("\u200b", "").strip()
    if _bio_clean in ("بیوگرافی", "بیو"):
            try:
                from database import get_setting as _gs
                _bio_text = _gs(0, "bio_text", "")
            except Exception:
                _bio_text = ""
            if not _bio_text:
                _bio_text = (
                    "⚡ Skteam Manager ⚡" + NL + NL +
                    "🛡 امنیت کامل" + NL +
                    "🤖 AI هوشمند" + NL +
                    "📊 آمار دقیق" + NL +
                    "💎 اشتراک ویژه" + NL + NL +
                    "👨‍💻 سازنده: سیاوش" + NL +
                    "📞 @Siavashska"
                )
            await msg.reply_text(_bio_text)
            return

    for cat in BIOS.keys():
        if ("بیو " + cat) in t_low or (cat in t_low and "بیو" in t_low):
            bio = random.choice(BIOS[cat])
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("بستن", callback_data="bio_close:" + str(user.id))],
            ])
            await msg.reply_text("بیو " + cat + ":" + NL + NL + bio, reply_markup=kb)
            return

    if t_low.strip() in ("بیو", "bio"):
        out = (
            "بیوهای آماده" + NL +
            "━━━━━━━━━━━━━━━━━━" + NL +
            "یکی از دسته بندی ها رو انتخاب کن:"
        )
        try:
            await msg.reply_text(out, reply_markup=get_bio_menu(user.id))
        except Exception:
            await msg.reply_text(out)
        return

    if t_low.startswith("ساعت") or t_low.startswith("تاریخ") or t_low.startswith("تقویم") or t_low.strip() in ("ساعت", "تاریخ", "تقویم"):
        now = datetime.now()
        wd_list = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]
        wd = wd_list[now.weekday()]
        # تقویم شمسی
        try:
            jnow = jdatetime.datetime.fromgregorian(datetime=now)
            jwd_list = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]
            jwd = jwd_list[jnow.weekday()]
            jdate = jnow.strftime("%Y/%m/%d")
            jmonth = jnow.j_months_fa[jnow.month - 1] if hasattr(jnow, 'j_months_fa') else ""
            shamsi_line = "شمسی: " + jdate + " (" + jmonth + ")" + NL + "روز: " + jwd
        except Exception as e:
            print("[SHAMSI ERR] " + str(e))
            shamsi_line = "شمسی: خطا در محاسبه"
        out = (
            "📅 تاریخ و ساعت" + NL +
            "━━━━━━━━━━━━━━━━" + NL +
            "🗓️ میلادی: " + now.strftime("%Y-%m-%d") + NL +
            "🗓️ " + shamsi_line + NL +
            "⏰ ساعت: " + now.strftime("%H:%M") + NL +
            "📆 روز: " + wd
        )
        await msg.reply_text(out)
        return

    if "فال" in t_low:
        poem = random.choice(HAFEZ)
        await msg.reply_text("فال حافظ:" + NL + NL + poem)
        return




    if "تصادفی" in t_low or "رندوم" in t_low:
        parts = t_low.split()
        nums = [int(p) for p in parts if p.isdigit()]
        if len(nums) >= 2:
            n = random.randint(min(nums[0], nums[1]), max(nums[0], nums[1]))
            await msg.reply_text("عدد: " + str(n))
        else:
            n = random.randint(1, 100)
            await msg.reply_text("عدد: " + str(n))
        return

    if "هوا" in t_low or "weather" in t_low:
        parts = text.split()
        city = None
        for i, p in enumerate(parts):
            if p.lower() in ("هوا", "weather") and i + 1 < len(parts):
                city = parts[i + 1]
                break
        if not city:
            city = "Tehran"
        await msg.reply_text("در حال دریافت آب و هوا برای " + city + "...")
        w = fetch_weather(city)
        if not w:
            await msg.reply_text("نتونستم اطلاعات بگیرم.")
            return
        out = (
            "آب و هوا: " + city + NL +
            "دما: " + str(w["temp"]) + " C" + NL +
            "حس می‌شه: " + str(w["feels"]) + " C" + NL +
            "رطوبت: " + str(w["humidity"]) + "%" + NL +
            "وضعیت: " + w["desc"]
        )
        await msg.reply_text(out)
        return

    if any(k in t_low for k in ["آیدی", "ایدی", "مشخصات", "پروفایل"]):
        target = None
        if msg.reply_to_message and msg.reply_to_message.from_user:
            target = msg.reply_to_message.from_user
        if target:
            try:
                await send_user_info(msg, context, chat, target)
            except Exception as e:
                print("[ID ERR] " + str(e))
        else:
            await msg.reply_text("روی پیام کاربر ریپلای کن و بنویس آیدی")
        return

    admin = await is_admin(chat, user.id)
    if not admin:
        return

    if t_low in ("پینگ", "ping"):
        start = time.time()
        sent = await msg.reply_text("Pong!")
        latency = int((time.time() - start) * 1000)
        try:
            await sent.edit_text("Pong! " + str(latency) + " ms")
        except Exception:
            pass
        return

    if "نظرسنجی" in t_low or "poll" in t_low:
        parts = text.split("نظرسنجی")
        if len(parts) > 1:
            question = parts[1].strip()
            if question:
                try:
                    await context.bot.send_poll(
                        chat_id=chat.id,
                        question=question,
                        options=["بله", "خیر", "نمی‌دونم"],
                        is_anonymous=False,
                    )
                except Exception as e:
                    await msg.reply_text("خطا: " + str(e))
                return
        await msg.reply_text("مثال: نظرسنجی آیا موافقید؟")
        return

    has_keyword = any(t_low.startswith(kw) or t_low.strip() == kw for kw in KEYWORDS)
    if is_mentioned or has_keyword:
        try:
            from database import get_nickname
            
            # ۱. اگه سازنده بود → جواب خفن
            if user.id == OWNER_ID:
                await msg.reply_text(random.choice(OWNER_CALL_REPLIES))
                return
            
            # ۲. اگه کاربر لقب داشت → جواب طنز با لقب
            nick = get_nickname(chat.id, user.id)
            if nick:
                reply_template = random.choice(NICK_CALL_TEMPLATES)
                await msg.reply_text(reply_template.format(nick=nick))
                return
            
            # ۳. کاربر بدون لقب → سکوت (هیچی نمی‌گه)
            # return بدون پیام
            
        except Exception as e:
            print("[NICK REPLY ERR] " + str(e))


async def bio_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id

    parts = data.split(":")
    action = parts[0]
    owner = int(parts[1]) if len(parts) > 1 else clicker

    if clicker != owner:
        await query.answer("این منو برای شما نیست", show_alert=True)
        return

    await query.answer()

    if action == "bio_close":
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    if action.startswith("bio_"):
        cat = action[4:]
        if cat in BIOS:
            bio = random.choice(BIOS[cat])
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("بستن", callback_data="bio_close:" + str(clicker))],
            ])
            try:
                await query.edit_message_text("بیو " + cat + ":" + NL + NL + bio, reply_markup=kb)
            except Exception:
                await query.message.reply_text("بیو " + cat + ":" + NL + NL + bio, reply_markup=kb)


def register(app):
    from telegram.ext import CallbackQueryHandler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler, block=False), group=1)
    app.add_handler(CallbackQueryHandler(bio_button_handler, pattern="^bio_"))
