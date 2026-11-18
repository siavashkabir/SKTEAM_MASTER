import json
import os

LANG_FILE = "data/lang.json"


def load_langs():
    if os.path.exists(LANG_FILE):
        try:
            with open(LANG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_langs(data):
    os.makedirs("data", exist_ok=True)
    with open(LANG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def get_lang(chat_id):
    data = load_langs()
    return data.get(str(chat_id), "fa")


def set_lang(chat_id, lang):
    data = load_langs()
    data[str(chat_id)] = lang
    save_langs(data)


def t(chat_id, key):
    from langs import FA, EN
    lang = get_lang(chat_id)
    d = FA if lang == "fa" else EN
    return d.get(key, key)
