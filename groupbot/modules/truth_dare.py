import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

NL = chr(10)

# State: {chat_id: {"players": [uid...], "names": {uid: name}, "turn": 0, "mode": "normal", "waiting": False}}
TD_GAME = {}

TRUTH_TRIGGERS = ["جرئت یا حقیقت", "حقیقت یا جرئت", "truth or dare"]
CHALLENGE_TRIGGERS = ["چالش"]

# ============ حقیقت - عادی ============
TRUTHS_NORMAL = [
    "آخرین دروغی که گفتی چی بود؟", "بزرگ‌ترین ترست چیه؟", "تا حالا عاشق شدی؟",
    "خجالت‌آورترین لحظه زندگیت چی بود؟", "بدترین نمره‌ای که گرفتی چند بود؟",
    "تا حالا سر امتحان تقلب کردی؟", "دوست داری کدوم توانایی رو داشته باشی؟",
    "بزرگ‌ترین آرزوت چیه؟", "چند تا دوست صمیمی داری؟", "آخرین بار کی گریه کردی؟",
    "دوست داری کجا زندگی کنی؟", "غذای مورد علاقه‌ت چیه؟", "بدترین عادتی که داری چیه؟",
    "آخرین فیلمی که دیدی چی بود؟", "آخرین بار کی از کسی عذرخواهی کردی؟",
    "خونه‌ی رؤیاییت چه شکلیه؟", "تا حالا از کسی متنفر شدی؟",
    "بزرگ‌ترین ریسکی که تو زندگیت کردی چی بود؟", "دوست داری شغل آینده‌ت چی باشه؟",
    "تا حالا شده از مدرسه فرار کنی؟", "بزرگ‌ترین نقطه ضعفت چیه؟",
    "دوست داری کدوم کشور رو ببینی؟", "بدترین دروغی که به پدر و مادرت گفتی چی بود؟",
    "چند تا خواهر و برادر داری؟", "دوست داری چه حیوونی باشی؟",
    "آخرین بار کی از ته دل خندیدی؟", "راز داری که هیچ‌کس ندونه؟",
    "به نظرت بزرگ‌ترین موفقیتت چیه؟", "بچگی‌هات چه آرزویی داشتی؟",
    "آخرین چیزی که خریدیش چی بود؟", "بدترین هدیه‌ای که گرفتی چی بود؟",
    "دوست داری کجا بری سفر؟", "به نظرت قشنگ‌ترین اسم چیه؟",
    "دوست داری کدوم فصل سال باشه؟", "آخرین بار کی کسی رو تحقیر کردی؟",
    "بهترین روز زندگیت کدوم روز بود؟", "دوست داری چه چیزی رو تغییر بدی تو خودت؟",
    "چند تا زبان بلدی؟", "آخرین بار کی از کسی خوشت اومد؟",
    "به نظرت بهترین سن برای ازدواج چنده؟", "بزرگ‌ترین حسرت زندگیت چیه؟",
    "دوست داری چی رو کاش یاد گرفته بودی؟", "آخرین بار کی رؤیای بد دیدی؟",
    "به نظرت مرگ چیه؟", "بزرگ‌ترین درسی که از زندگی گرفتی چیه؟",
    "اگه می‌تونستی زمان رو برگردونی، کدوم کارت رو عوض می‌کردی؟",
    "دوست داری چه هدیه‌ای بگیری؟", "آخرین بار کی به کسی تلفن زدی؟",
    "چند بار عاشق شدی؟", "دوست داری چه کتابی رو بخونی؟",
    "بدترین عادت دوستات چیه؟", "دوست داری چی رو یاد بگیری؟",
    "آخرین بار کی کسی رو بخشیدی؟", "اگه یه میلیون داشتی چیکار می‌کردی؟",
    "بهترین خاطره‌ت از مدرسه چیه؟", "دوست داری چی تو دنیا تغییر کنه؟",
    "چند بار سفر رفتی؟", "دوست داری چه موسیقی گوش کنی؟",
    "آخرین بار کی از خودت ناراضی بودی؟", "بهترین دوستت کیه؟ چرا؟",
    "دوست داری چه چیزی رو با کسی تقسیم کنی؟", "آخرین بار کی یه دروغ بزرگ گفتی؟",
    "چی رو تو خودت دوست داری؟", "دوست داری چه چیزی رو به کسی بگی که نگفتی؟",
    "بدترین روز زندگیت کدوم بود؟", "آخرین بار کی خندیدی که دلت درد گرفت؟",
    "دوست داری تو کدوم شهر زندگی کنی؟", "چند بار سر قرار دیر رسیدی؟",
    "بزرگ‌ترین دروغی که به دوستت گفتی چی بود؟", "دوست داری کدوم آدم معروف رو ببینی؟",
    "آخرین بار کی به کسی حسودی کردی؟", "دوست داری چه حرفه‌ای یاد بگیری؟",
    "چند بار دوستات رو ناراحت کردی؟", "دوست داری یه چیزی رو از زندگیت حذف کنی؟",
    "بهترین اتفاق این هفته چی بود؟", "بدترین اتفاق این ماه چی بود؟",
    "دوست داری چه فیلمی رو ببینی؟", "چی بیشتر از همه خوشحالت می‌کنه؟",
    "چی بیشتر از همه ناراحتت می‌کنه؟", "دوست داری با چه کسی سفر بری؟",
    "دوست داری چه هدیه‌ای بدی؟",
]

# ============ جرئت - عادی ============
DARES_NORMAL = [
    "برای نفر بغلیت یه آهنگ بخون.", "برای نفر بغلیت یه شعر بگو.",
    "حرکات یه حیوون رو تقلید کن.", "۵ دقیقه با لهجه حرف بزن.",
    "یه عکس سلفی بفرست.", "اسم ۱۰ تا از اعضای گروه رو بگو.",
    "برای نفر بغلیت یه تعریف بکن.", "شکلک بامزه بزن و عکس بگیر.",
    "رقص بکن و ویس بفرست.", "خاطره‌ی خنده‌دار تعریف کن.",
    "برای نفر بغلیت یه هدیه بفرست.", "یه جمله به انگلیسی بگو.",
    "داستان کوتاه تعریف کن.", "مثل بچه‌ها حرف بزن.", "صدای ساز در بیار.",
    "برای نفر بغلیت یه چیزی بخندون.", "ادای یه خواننده معروف رو در بیار.",
    "نقاشی یه چیزی بکش و بفرست.", "یه لطیفه بگو.", "به مدت ۱ دقیقه ساکت باش.",
    "شعر از حفظ بخون.", "یه نقاشی رو با سرعت بکش و بفرست.",
    "صدای یه ماشین رو تقلید کن.", "برای نفر بغلیت یه آهنگ به انتخاب خودش بخون.",
    "شماره‌ات رو رندوم بگو.", "برای نفر بغلیت یه سوپرايز بفرست.",
    "یه ویدیوی ۱۰ ثانیه‌ای از رقصت بفرست.",
    "خودت رو در یه موقعیت خنده‌دار تصور کن و توضیح بده.",
    "سه تا آرزوی عجیب بگو.", "برای نفر بغلیت یه پیام صوتی بفرست.",
    "به بالاترین نفر گروه یه پیام خصوصی بده.", "اسم سه تا از دوستای قدیمیت رو بگو.",
    "برای یه دقیقه لهجه اصفهانی حرف بزن.", "ادای معلمت رو دربیار.",
    "از یه نفری تو گروه تعریف کن.", "خودت رو یه بار مسخره کن.",
    "برای نفر بغلیت یه آرزوی خنده‌دار بکن.", "برای ۵ دقیقه بدون حرف زدن کار کن.",
    "یه آهنگ بی‌کلام رو تقلید کن.", "به مدت ۳۰ ثانیه بدون نفس حرف بزن.",
    "از یه نفر تو گروه یه سوال بپرس.", "برای نفر بغلیت یه استوری تعریف کن.",
    "سه تا از ترسهات رو بگو.", "به یه نفر تو گروه بگو خیلی دوستش داری.",
    "برای نفر بغلیت یه شوخی بکن.", "شکلک ترسناک بزن.",
    "برای یه دقیقه مثل پیرمردها حرف بزن.", "به مدت یک دقیقه مثل ربات حرف بزن.",
    "برای نفر بغلیت یه جمله عاشقانه بگو.", "با یه لهجه جدید به مدت ۳۰ ثانیه حرف بزن.",
    "ادای یه بازیگر معروف رو در بیار.", "برای نفر بغلیت یه آهنگ شاد بخون.",
    "به یکی از اعضای گروه یه کمکی بکن.", "برای یه دقیقه با لحن خبرنگار حرف بزن.",
    "شعر کودکانه بخون.", "شکلک گریه بزن و بفرست.",
    "برای ۳۰ ثانیه مثل اسب صدا دربیار.", "به یکی از اعضای گروه یه آهنگ پیشنهاد بده.",
    "برای نفر بغلیت یه لطیفه تعریف کن.", "ادای یه فوتبالیست معروف رو دربیار.",
    "برای یه دقیقه از یه اتفاق خنده‌دار تعریف کن.",
    "به همه تو گروه یه سلام گرم بگو.", "برای نفر بغلیت یه دست بزن (ویس بفرست).",
    "ادای یه بچه ۳ ساله رو در بیار.", "برای ۳۰ ثانیه مثل گربه صدا دربیار.",
    "به یکی از اعضای گروه یه آرزوی خوب بکن.",
    "برای یه دقیقه با لحن رادیو حرف بزن.", "شعر حافظ یا سعدی بخون.",
    "برای نفر بغلیت یه شکلک بامزه بفرست.",
    "برای ۳۰ ثانیه فقط با ایموجی حرف بزن.",
    "ادای یه معلم ریاضی رو دربیار.", "برای نفر بغلیت یه داستان کوتاه تعریف کن.",
    "به یکی از اعضای گروه یه هدیه مجازی بفرست.",
    "برای ۵ دقیقه بدون گوشی بمون (توی گروه اعلام کن).",
    "ادای یه خواننده ایرانی رو دربیار.",
    "برای نفر بغلیت یه آهنگ با تغییر صدا بخون.",
]

# ============ حقیقت +18 ============
TRUTHS_ADULT = [
    "اولین بوسه‌ت کی بود؟", "چند تا رابطه داشتی؟",
    "دوست داری کدوم مدل آدم بغلت بخوابه؟", "تا حالا مست کردی؟ چطور شد؟",
    "بزرگ‌ترین فانتزی زندگیت چیه؟", "آخرین بار کی به یه نفر حس خاصی داشتی؟",
    "دوست داری با کی یه شب خاص داشته باشی؟", "تا حالا شده از پشت بوسیده بشی؟",
    "بدترین قرار عاشقانه‌ت چطور بود؟", "چند تا کس تو زندگیت داشتی؟",
    "به نظرت کی سکسی‌ترین آدم دنیاست؟", "دوست داری چطوری توی یه رابطه رفتار کنن؟",
    "بزرگ‌ترین شیطونی‌ت چی بوده؟", "دوست داری شریکت چه خصوصیتی داشته باشه؟",
    "چند تا قلب تو زندگیت شکستی؟", "توی رابطه قبلیت چی رو از دست دادی؟",
    "آخرین بار کی به یه نفر آره گفتی؟", "بزرگ‌ترین دروغی که به شریکت گفتی چی بود؟",
    "دوست داری یه شب خاص رو با کی بگذرونی؟", "تا حالا شده توی خواب کسی رو ببوسی؟",
    "چند تا کس رو دوست داشتی ولی بهشون نگفتی؟", "بدترین آدمی که باهاش بودی کی بود؟",
    "دوست داری یه رازت رو اینجا بگی؟", "چند بار عاشق شدی؟",
    "دوست داری توی یه رابطه چی رو تجربه کنی؟", "تا حالا توی پارک کسی رو بوسیدی؟",
    "بزرگ‌ترین اشتباه عاطفیت چی بود؟", "دوست داری کدوم مدل فیلم ببینی؟",
    "چند بار یه شب رو با کسی گذروندی؟", "دوست داری چطوری اولین بوسه‌ت باشه؟",
    "توی رابطه بیشتر عاشق می‌شی یا معشوق؟", "چند تا کس تو زندگیت بهت خیانت کردن؟",
    "دوست داری یه رازت رو با گروه بگی؟", "بدترین چیزی که کسی بهت گفته چی بود؟",
    "دوست داری چطوری یه شب خاص رو بگذرونی؟", "توی زندگیت چند بار آره گفتی به عشق؟",
    "دوست داری با کی بری سفر عاشقانه؟", "چند تا آرزو داری که نشد؟",
    "توی رابطه بیشتر خجالتی هستی یا جسور؟", "دوست داری یه لحظه خاص زندگیت رو بگی؟",
    "بهترین قرار عاشقانه‌ت چطور بود؟", "چند تا کس رو واقعاً دوست داشتی؟",
    "بزرگ‌ترین دروغی که به خودت گفتی چی بود؟", "چی بیشتر از همه تو یه رابطه مهمه؟",
    "دوست داری چه چیزی رو در رابطه تجربه کنی که نکردی؟",
    "بزرگ‌ترین حسرت عاطفیت چیه؟", "دوست داری آخرین شب زندگیت رو چطوری بگذرونی؟",
    "چند تا کس توی زندگیت هنوز یادت نرفتن؟", "دوست داری چطوری خواستگاریت کنن؟",
    "بزرگ‌ترین جذابیتت چیه؟", "دوست داری با کی یه سفر عاشقانه بری؟",
    "چی تو یه آدم برات جذابه؟", "دوست داری اولین بوسه‌ت کجا باشه؟",
    "بدترین حس تو یه رابطه چیه؟", "دوست داری شریکت چطوری باشه؟",
    "چند تا آدم توی زندگیت داشتی که فراموش کردی؟",
    "بزرگ‌ترین دروغی که به کسی گفتی تو رابطه چی بود؟",
    "دوست داری با کی یه شب رمانتیک داشته باشی؟",
    "چی تو یه رابطه بیشتر از همه اذیتت می‌کنه؟",
    "دوست داری چطوری رفتار کنن با تو توی یه رابطه؟",
]

# ============ جرئت +18 ============
DARES_ADULT = [
    "برای نفر بغلیت یه پیام عاشقانه بفرست.",
    "برای یکی از اعضای گروه یه استیکر عاشقانه بفرست.",
    "به یکی از اعضای گروه یه جمله جسورانه بگو.",
    "برای نفر بغلیت یه آهنگ عاشقانه بخون.",
    "به یه نفر تو گروه بگو خیلی خوشش میاد.",
    "برای نفر بغلیت یه کلمه عاشقانه بگو.",
    "به یکی از اعضای گروه بگو دوستش داری.",
    "برای یه دقیقه مثل عاشق‌ها حرف بزن.",
    "به یکی از اعضای گروه یه پیشنهاد بده.",
    "برای نفر بغلیت یه آهنگ جسورانه بخون.",
    "به یه نفر تو گروه بگو چشات قشنگه.",
    "برای نفر بغلیت یه پیام مخفی بفرست.",
    "به یه نفر تو گروه یه چیزی بگو که شرمنده شه.",
    "برای ۳۰ ثانیه با لحن عاشقانه حرف بزن.",
    "به یکی از اعضای گروه بگو خوابش رو دیدی.",
    "برای نفر بغلیت یه جمله مخفی بگو.",
    "به یه نفر تو گروه بگو دلت براش تنگ شده.",
    "برای یه دقیقه مثل عشاق قدیمی حرف بزن.",
    "به یه نفر تو گروه یه پیشنهاد جسورانه بده.",
    "برای نفر بغلیت یه آهنگ عاشقانه و جسور بخون.",
    "به یکی از اعضای گروه بگو دلت می‌خواد ببینیش.",
    "برای ۳۰ ثانیه با لحن جسورانه حرف بزن.",
    "به یه نفر تو گروه یه چیزی بگو که خجالت بکشه.",
    "برای نفر بغلیت یه پیام عاشقانه و جسور بفرست.",
    "به یه نفر تو گروه بگو توی خوابت بودی.",
    "برای یه دقیقه با لحن عاشقانه بخون.",
    "به یه نفر تو گروه یه حرف عاشقانه بگو.",
    "برای نفر بغلیت یه آهنگ عاشقانه بخون و برقص.",
    "به یه نفر تو گروه بگو توی فکرت هستی.",
    "برای ۳۰ ثانیه با لحن رمانتیک حرف بزن.",
    "به یکی از اعضای گروه یه پیام مخفی بفرست.",
    "برای نفر بغلیت یه آهنگ عاشقانه و شرم‌آور بخون.",
    "به یه نفر تو گروه بگو چشات قشنگه.",
    "برای یه دقیقه مثل عاشق‌ها آهنگ بخون.",
    "به یکی از اعضای گروه یه پیشنهاد عاشقانه بده.",
    "برای نفر بغلیت یه پیام عاشقانه و مخفی بفرست.",
    "به یه نفر تو گروه بگو دلم برات تنگ شده.",
    "برای ۳۰ ثانیه با لحن عاشقانه بخون.",
    "به یه نفر تو گروه یه حرف جسورانه بگو.",
    "برای نفر بغلیت یه آهنگ عاشقانه بخون و برقص.",
    "به یکی از اعضای گروه بگو دلت می‌خواد ببینیش.",
    "برای یه دقیقه مثل عاشق‌ها حرف بزن و بخون.",
    "به یه نفر تو گروه یه پیام شرم‌آور بفرست.",
    "برای نفر بغلیت یه آهنگ عاشقانه و بامزه بخون.",
    "به یه نفر تو گروه بگو چشات قشنگه و لبخند بزن.",
    "برای ۳۰ ثانیه با لحن عاشقانه و جسور حرف بزن.",
    "به یکی از اعضای گروه یه پیام عاشقانه بفرست.",
    "برای نفر بغلیت یه آهنگ عاشقانه و رمانتیک بخون.",
    "به یه نفر تو گروه بگو خوابش رو دیدی.",
    "برای یه دقیقه مثل عاشق‌ها بخون و برقص.",
    "به یکی از اعضای گروه یه حرف رمانتیک بگو.",
    "برای نفر بغلیت یه پیام جسورانه بفرست.",
    "به یه نفر تو گروه بگو دلت براش می‌لرزه.",
    "برای ۳۰ ثانیه با لحن عاشقانه و بامزه حرف بزن.",
    "به یکی از اعضای گروه بگو توی خوابت بوسیدیش.",
    "برای نفر بغلیت یه آهنگ عاشقانه و شرم‌آور بخون.",
    "به یه نفر تو گروه بگو چشاش مثل دریا می‌مونه.",
    "برای یه دقیقه مثل عاشق‌ها ویس بفرست.",
    "به یکی از اعضای گروه یه جمله جسورانه بگو.",
    "برای نفر بغلیت یه پیام عاشقانه طولانی بفرست.",
]

# ============ چالش‌ها ============
CHALLENGES = [
    "تا فردا ۱۰ تا پیام تو گروه بفرست!", "یه عکس خنده‌دار از خودت بفرست!",
    "به ۵ نفر تو گروه یه پیام خصوصی بده!", "یه ویس ۳۰ ثانیه‌ای بفرست و بخون!",
    "یه استوری بامزه بساز!", "به مدت ۱ ساعت بدون ایموجی پیام بده!",
    "یه نقاشی بکش و بفرست!", "یه آهنگ بخون و ویس بفرست!",
    "به نفر بغلیت یه هدیه بفرست!", "امشب ساعت ۱۲ بیدار بمون و به ۳ نفر پیام بده!",
    "برای همه تو گروه یه جمله محبت‌آمیز بفرست!", "یه لطیفه بگو و همه رو بخندون!",
    "۱۰ دقیقه با لهجه حرف بزن!", "به یه نفر تو گروه یه تعریف واقعی بکن!",
    "خودت رو در ۳ کلمه توصیف کن!", "یه خاطره بچگی تعریف کن!",
    "یه آرزو بکن و بنویس!", "یه جمله انگیزشی بگو!",
    "۵ تا از دوستات رو تگ کن!", "یه سوال از یکی از اعضای گروه بپرس!",
    "به مدت ۳۰ دقیقه فقط با ایموجی حرف بزن!", "سه تا از ترسهات رو بگو!",
    "یه آهنگ بی‌کلام بساز و ویس بفرست!", "یه خاطره خنده‌دار از سفرت تعریف کن!",
    "به یه نفر تو گروه یه سوپرايز بده!", "۵ دقیقه با یه لحن مسخره حرف بزن!",
    "یه شکلک بامزه بزن و بفرست!", "برای ۲ ساعت بدون گوشی بمون!",
    "یه شعر بخون و ویس بفرست!", "به یکی از اعضای گروه بگو دوستش داری!",
    "۱۰ تا از کلمات مورد علاقه‌ت رو بگو!", "یه داستان کوتاه تعریف کن!",
    "یه جمله به انگلیسی بگو و ویس بفرست!", "۳ تا آرزوت رو بنویس!",
    "به یه نفر تو گروه یه پیام محبت‌آمیز بفرست!", "۱ دقیقه بدون حرف زدن بمون!",
    "به همه اعضای گروه سلام کن!", "یه عکس از منظره بفرست!",
    "یه لطیفه خنده‌دار تعریف کن!", "۵ دقیقه با لحن بچه‌ها حرف بزن!",
    "به یه نفر تو گروه یه هدیه مجازی بفرست!", "یه داستان خنده‌دار از خودت تعریف کن!",
    "۳ تا از عادت‌های بدت رو بگو!", "یه نقاشی از یه حیوون بکش و بفرست!",
    "به مدت ۱ ساعت با یه نفر چت کن!", "یه ویس ۶۰ ثانیه‌ای خنده‌دار بفرست!",
    "۳ تا از رازهای کوچیکت رو بگو!", "یه کلیپ بامزه از اینترنت بفرست!",
    "به همه تو گروه یه آرزوی خوب بکن!", "۱۰ دقیقه با لحن خارجی حرف بزن!",
    "یه جمله الهام‌بخش بگو و ویس بفرست!",
]


def main_menu(chat_id):
    g = TD_GAME.get(chat_id)
    players_count = len(g["players"]) if g and g.get("players") else 0
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 شرکت کردن (" + str(players_count) + ")", callback_data="td_join")],
        [InlineKeyboardButton("▶️ شروع بازی", callback_data="td_start")],
        [InlineKeyboardButton("👥 لیست شرکت‌کننده‌ها", callback_data="td_list")],
        [InlineKeyboardButton("🎲 چالش", callback_data="td_challenge")],
        [InlineKeyboardButton("❌ بستن", callback_data="td_close")],
    ])


def game_kb(chat_id):
    g = TD_GAME.get(chat_id, {})
    mode = g.get("mode", "normal")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ حقیقت", callback_data="td_truth")],
        [InlineKeyboardButton("🔥 جرئت", callback_data="td_dare")],
        [InlineKeyboardButton("✅ جواب دادم، نفر بعدی", callback_data="td_next")],
        [InlineKeyboardButton("⚙️ حالت: " + ("🔞 +18" if mode == "adult" else "🔒 عادی"), callback_data="td_mode")],
        [InlineKeyboardButton("🛑 پایان بازی", callback_data="td_end")],
    ])


def challenge_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 چالش تصادفی", callback_data="td_ch_rand")],
        [InlineKeyboardButton("📋 ۵ چالش تصادفی", callback_data="td_ch_list")],
        [InlineKeyboardButton("❌ بستن", callback_data="td_close")],
    ])




async def _clear_old(context, chat_id, keep_last=0):
    """حذف پیام‌های قبلی بازی به جز keep_last تای آخر"""
    g = TD_GAME.get(chat_id)
    if not g:
        return
    msgs = g.get("sent_msgs", [])
    to_delete = msgs[:-keep_last] if keep_last else msgs
    for mid in to_delete:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception:
            pass
    g["sent_msgs"] = msgs[-keep_last:] if keep_last else []


async def td_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup"):
        return
    try:
        from database import get_setting, is_group_owner, is_bot_admin
        from config import OWNER_ID
        if get_setting(chat.id, "games_enabled", "1") != "1":
            allowed = (user.id == OWNER_ID or is_bot_admin(user.id) or is_group_owner(chat.id, user.id))
            if not allowed:
                return
    except Exception:
        pass
    text = msg.text.strip().lower()
    if text in [t.lower() for t in TRUTH_TRIGGERS]:
        # اگه بازی در جریان، فقط راهنما بده
        g = TD_GAME.get(chat.id)
        if g and g.get("active"):
            await msg.reply_text("⚠️ یه بازی در جریانه. اول تمومش کن یا «پایان بازی» رو بزن.")
            return
        # اگه بازی جدید، owner_id رو ذخیره کن
        if not g:
            TD_GAME[chat.id] = {"players": [], "names": {}, "turn": 0, "mode": "normal", "active": False, "starter_id": user.id, "sent_msgs": []}
        else:
            # اگه قبلاً منو باز شده و بازی شروع نشده، owner_id رو تغییر نده
            if not g.get("starter_id"):
                g["starter_id"] = user.id
        await msg.reply_text(
            "🎭 جرئت یا حقیقت" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
            "📌 برای شرکت، روی «شرکت کردن» بزنید." + NL +
            "📌 حداقل ۲ نفر لازمه." + NL +
            "📌 وقتی همه شرکت کردن، سازنده «شروع بازی» رو بزنه." + NL + NL +
            "👤 کنترل پنل: " + (user.first_name or "کاربر"),
            reply_markup=main_menu(chat.id)
        )
        return
    if text == "چالش":
        await msg.reply_text(
            "🎯 چالش" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
            "یکی از گزینه‌ها رو انتخاب کن:",
            reply_markup=challenge_kb()
        )


async def td_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    chat = query.message.chat

    if data == "td_join":
        g = TD_GAME.setdefault(chat.id, {"players": [], "names": {}, "turn": 0, "mode": "normal", "active": False, "starter_id": 0, "sent_msgs": []})
        if g.get("active"):
            await query.answer("بازی در جریانه!", show_alert=True)
            return
        if user.id in g["players"]:
            await query.answer("قبلاً شرکت کردی!", show_alert=True)
            return
        g["players"].append(user.id)
        g["names"][user.id] = user.first_name or "کاربر"
        try:
            await query.edit_message_reply_markup(reply_markup=main_menu(chat.id))
        except Exception:
            pass
        return

    if data == "td_start":
        g = TD_GAME.get(chat.id)
        if not g or len(g.get("players", [])) < 2:
            await query.answer("حداقل ۲ نفر باید شرکت کنن!", show_alert=True)
            return
        if g.get("active"):
            await query.answer("بازی شروع شده!", show_alert=True)
            return
        if g.get("starter_id") and user.id != g.get("starter_id"):
            await query.answer("فقط سازنده بازی می‌تونه شروع کنه!", show_alert=True)
            return
        g["active"] = True
        g["turn"] = 0
        if not g.get("starter_id"):
            g["starter_id"] = user.id
        first_uid = g["players"][0]
        name = g["names"].get(first_uid, "کاربر")
        text = (
            "🎭 بازی شروع شد!" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
            "👥 شرکت‌کننده‌ها: " + str(len(g["players"])) + " نفر" + NL +
            "👤 کنترل پنل: " + (user.first_name or "کاربر") + NL + NL +
            "🎯 نوبت: " + name + NL + NL +
            "لطفاً " + name + " یه گزینه انتخاب کن:"
        )
        try:
            await query.message.delete()
        except Exception:
            pass
        g["sent_msgs"] = []
        try:
            sent = await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=game_kb(chat.id))
            g["sent_msgs"].append(sent.message_id)
        except Exception as e:
            print("[TD START ERR] " + str(e))
        return

    if data == "td_list":
        g = TD_GAME.get(chat.id)
        if not g or not g.get("players"):
            await query.answer("هنوز کسی شرکت نکرده!", show_alert=True)
            return
        names = [g["names"].get(p, "کاربر") for p in g["players"]]
        text = "👥 شرکت‌کننده‌ها (" + str(len(names)) + "):" + NL + NL
        for i, n in enumerate(names, 1):
            text += str(i) + ". " + n + NL
        await query.answer()
        try:
            await query.edit_message_text(text, reply_markup=main_menu(chat.id))
        except Exception:
            pass
        return

    if data == "td_challenge":
        await query.answer()
        try:
            await query.edit_message_text(
                "🎯 چالش" + NL + "━━━━━━━━━━━━━━━━" + NL + NL + "یکی از گزینه‌ها رو انتخاب کن:",
                reply_markup=challenge_kb()
            )
        except Exception:
            pass
        return

    if data == "td_ch_rand":
        q = random.choice(CHALLENGES)
        await query.answer()
        try:
            await query.edit_message_text(
                "🎯 چالش تصادفی" + NL + "━━━━━━━━━━━━━━━━" + NL + NL + q,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎲 چالش دیگه", callback_data="td_ch_rand")],
                    [InlineKeyboardButton("🔙 منوی چالش", callback_data="td_challenge")],
                ])
            )
        except Exception:
            pass
        return

    if data == "td_ch_list":
        picks = random.sample(CHALLENGES, min(5, len(CHALLENGES)))
        text = "🎯 ۵ چالش تصادفی" + NL + "━━━━━━━━━━━━━━━━" + NL + NL
        for p in picks:
            text += "• " + p + NL + NL
        await query.answer()
        try:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎲 ۵ چالش دیگه", callback_data="td_ch_list")],
                [InlineKeyboardButton("🔙 منوی چالش", callback_data="td_challenge")],
            ]))
        except Exception:
            pass
        return

    if data == "td_truth" or data == "td_dare":
        g = TD_GAME.get(chat.id)
        if not g or not g.get("active"):
            await query.answer("بازی فعال نیست!", show_alert=True)
            return
        # چک کن کاربر نوبت‌دار هست
        current_uid = g["players"][g["turn"]]
        if user.id != current_uid:
            current_name = g["names"].get(current_uid, "کاربر")
            await query.answer("نوبت شما نیست! نوبت " + current_name + " هست.", show_alert=True)
            return
        mode = g.get("mode", "normal")
        if data == "td_truth":
            pool = TRUTHS_ADULT if mode == "adult" else TRUTHS_NORMAL
            title = "❓ حقیقت"
        else:
            pool = DARES_ADULT if mode == "adult" else DARES_NORMAL
            title = "🔥 جرئت"
        q = random.choice(pool)
        current_name = g["names"].get(g["players"][g["turn"]], "کاربر")
        text = title + " برای " + current_name + NL + "━━━━━━━━━━━━━━━━" + NL + NL + q + NL + NL + "پس از پاسخ، روی «جواب دادم» بزنید."
        # پاک کردن همه پیام‌های قبلی
        for mid in g.get("sent_msgs", []):
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=mid)
            except Exception:
                pass
        g["sent_msgs"] = []
        try:
            sent = await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=game_kb(chat.id))
            g["sent_msgs"].append(sent.message_id)
        except Exception as e:
            print("[TD NEW MSG ERR] " + str(e))
        return

    if data == "td_next":
        g = TD_GAME.get(chat.id)
        if not g or not g.get("active"):
            return
        current_uid = g["players"][g["turn"]]
        if user.id != current_uid:
            current_name = g["names"].get(current_uid, "کاربر")
            await query.answer("فقط " + current_name + " می‌تونه نوبت رو رد کنه!", show_alert=True)
            return
        g["turn"] = (g["turn"] + 1) % len(g["players"])
        current_name = g["names"].get(g["players"][g["turn"]], "کاربر")
        text = (
            "🎯 نوبت: " + current_name + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
            "لطفاً یه گزینه انتخاب کن:"
        )
        # پاک کردن پیام‌های قبلی
        for mid in g.get("sent_msgs", []):
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=mid)
            except Exception:
                pass
        g["sent_msgs"] = []
        try:
            sent = await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=game_kb(chat.id))
            g["sent_msgs"].append(sent.message_id)
        except Exception as e:
            print("[TD NEXT MSG ERR] " + str(e))
        return

    if data == "td_mode":
        g = TD_GAME.get(chat.id)
        if not g:
            return
        if g.get("starter_id") and user.id != g.get("starter_id"):
            await query.answer("فقط استارت‌کننده بازی می‌تونه حالت رو عوض کنه!", show_alert=True)
            return
        g["mode"] = "adult" if g.get("mode", "normal") == "normal" else "normal"
        await query.answer("حالت تغییر کرد")
        try:
            await query.edit_message_reply_markup(reply_markup=game_kb(chat.id))
        except Exception:
            pass
        return

    if data == "td_end":
        g = TD_GAME.get(chat.id)
        if g and g.get("starter_id") and user.id != g.get("starter_id"):
            await query.answer("فقط استارت‌کننده بازی می‌تونه بازی رو تموم کنه!", show_alert=True)
            return
        for mid in g.get("sent_msgs", []) if g else []:
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=mid)
            except Exception:
                pass
        try:
            await query.message.delete()
        except Exception:
            pass
        TD_GAME.pop(chat.id, None)
        await query.answer("بازی تموم شد")
        try:
            await context.bot.send_message(chat_id=chat.id, text="🛑 بازی تموم شد. برای شروع دوباره «جرئت یا حقیقت» رو بزنید.")
        except Exception:
            pass
        return

    if data == "td_close":
        g = TD_GAME.get(chat.id)
        if g and g.get("starter_id") and user.id != g.get("starter_id"):
            await query.answer("فقط سازنده بازی می‌تونه منو رو ببنده!", show_alert=True)
            return
        try:
            await query.message.delete()
        except Exception:
            pass
        TD_GAME.pop(chat.id, None)
        return


def register(app):
    app.add_handler(MessageHandler(filters.Regex(r"^(جرئت یا حقیقت|حقیقت یا جرئت|truth or dare|چالش)$"), td_text_handler), group=5)
    app.add_handler(CallbackQueryHandler(td_callback, pattern="^(td_)"), group=5)
