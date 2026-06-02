"""Multi-language and multi-country localization for AgentMagnet — TRULY GLOBAL."""

LANGUAGES = {
    "en":    {"name": "English",    "native": "English",    "amazon": "com",    "ebay": "com",     "currency": "USD",  "region": "Americas"},
    "es":    {"name": "Spanish",    "native": "Espanol",    "amazon": "es",     "ebay": "es",      "currency": "EUR",  "region": "Europe"},
    "fr":    {"name": "French",     "native": "Francais",   "amazon": "fr",     "ebay": "fr",      "currency": "EUR",  "region": "Europe"},
    "de":    {"name": "German",     "native": "Deutsch",    "amazon": "de",     "ebay": "de",      "currency": "EUR",  "region": "Europe"},
    "it":    {"name": "Italian",    "native": "Italiano",   "amazon": "it",     "ebay": "it",      "currency": "EUR",  "region": "Europe"},
    "pt":    {"name": "Portuguese", "native": "Portugues",  "amazon": "com.br", "ebay": "com",     "currency": "BRL",  "region": "Americas"},
    "ja":    {"name": "Japanese",   "native": "Nihongo",    "amazon": "co.jp",  "ebay": "com",     "currency": "JPY",  "region": "Asia"},
    "zh":    {"name": "Chinese",    "native": "Zhongwen",   "amazon": "com",    "ebay": "com",     "currency": "CNY",  "region": "Asia"},
    "ko":    {"name": "Korean",     "native": "Hangugo",    "amazon": "com",    "ebay": "com",     "currency": "KRW",  "region": "Asia"},
    "ar":    {"name": "Arabic",     "native": "Arabiya",    "amazon": "ae",     "ebay": "com",     "currency": "AED",  "region": "Middle East"},
    "hi":    {"name": "Hindi",      "native": "Hindi",      "amazon": "in",     "ebay": "in",      "currency": "INR",  "region": "Asia"},
    "nl":    {"name": "Dutch",      "native": "Nederlands", "amazon": "nl",     "ebay": "nl",      "currency": "EUR",  "region": "Europe"},
    "sv":    {"name": "Swedish",    "native": "Svenska",    "amazon": "se",     "ebay": "com",     "currency": "SEK",  "region": "Europe"},
    "pl":    {"name": "Polish",     "native": "Polski",     "amazon": "pl",     "ebay": "pl",      "currency": "PLN",  "region": "Europe"},
    "tr":    {"name": "Turkish",    "native": "Turkce",     "amazon": "com.tr", "ebay": "com",     "currency": "TRY",  "region": "Europe/Asia"},
    "th":    {"name": "Thai",       "native": "Phasa Thai", "amazon": "com",    "ebay": "th",      "currency": "THB",  "region": "Asia"},
    "vi":    {"name": "Vietnamese", "native": "Tieng Viet", "amazon": "com",    "ebay": "com",     "currency": "VND",  "region": "Asia"},
    "id":    {"name": "Indonesian", "native": "Bahasa Indonesia", "amazon": "com", "ebay": "com", "currency": "IDR", "region": "Asia"},
    "ms":    {"name": "Malay",      "native": "Bahasa Melayu", "amazon": "com", "ebay": "my",     "currency": "MYR",  "region": "Asia"},
    "tl":    {"name": "Filipino",   "native": "Tagalog",    "amazon": "com",    "ebay": "ph",      "currency": "PHP",  "region": "Asia"},
    "ru":    {"name": "Russian",    "native": "Russkiy",    "amazon": "com",    "ebay": "com",     "currency": "RUB",  "region": "Europe/Asia"},
    "uk":    {"name": "Ukrainian",  "native": "Ukrainska",  "amazon": "com",    "ebay": "com",     "currency": "UAH",  "region": "Europe"},
    "he":    {"name": "Hebrew",     "native": "Ivrit",      "amazon": "com",    "ebay": "il",      "currency": "ILS",  "region": "Middle East"},
    "el":    {"name": "Greek",      "native": "Ellinika",   "amazon": "com",    "ebay": "com",     "currency": "EUR",  "region": "Europe"},
    "cs":    {"name": "Czech",      "native": "Cestina",    "amazon": "com",    "ebay": "com",     "currency": "CZK",  "region": "Europe"},
    "ro":    {"name": "Romanian",   "native": "Romana",     "amazon": "com",    "ebay": "com",     "currency": "RON",  "region": "Europe"},
    "hu":    {"name": "Hungarian",  "native": "Magyar",     "amazon": "com",    "ebay": "com",     "currency": "HUF",  "region": "Europe"},
    "da":    {"name": "Danish",     "native": "Dansk",      "amazon": "com",    "ebay": "com",     "currency": "DKK",  "region": "Europe"},
    "fi":    {"name": "Finnish",    "native": "Suomi",      "amazon": "com",    "ebay": "com",     "currency": "EUR",  "region": "Europe"},
    "nb":    {"name": "Norwegian",  "native": "Norsk",      "amazon": "com",    "ebay": "com",     "currency": "NOK",  "region": "Europe"},
    "bn":    {"name": "Bengali",    "native": "Bangla",     "amazon": "in",     "ebay": "com",     "currency": "BDT",  "region": "Asia"},
    "ta":    {"name": "Tamil",      "native": "Tamil",      "amazon": "in",     "ebay": "com",     "currency": "INR",  "region": "Asia"},
    "te":    {"name": "Telugu",     "native": "Telugu",     "amazon": "in",     "ebay": "com",     "currency": "INR",  "region": "Asia"},
    "mr":    {"name": "Marathi",    "native": "Marathi",    "amazon": "in",     "ebay": "com",     "currency": "INR",  "region": "Asia"},
    "ur":    {"name": "Urdu",       "native": "Urdu",       "amazon": "ae",     "ebay": "com",     "currency": "AED",  "region": "Asia"},
    "sw":    {"name": "Swahili",    "native": "Kiswahili",  "amazon": "com",    "ebay": "com",     "currency": "TZS",  "region": "Africa"},
    "ha":    {"name": "Hausa",      "native": "Hausa",      "amazon": "com",    "ebay": "com",     "currency": "NGN",  "region": "Africa"},
    "yo":    {"name": "Yoruba",     "native": "Yoruba",     "amazon": "com",    "ebay": "com",     "currency": "NGN",  "region": "Africa"},
    "ig":    {"name": "Igbo",       "native": "Igbo",       "amazon": "com",    "ebay": "com",     "currency": "NGN",  "region": "Africa"},
    "am":    {"name": "Amharic",    "native": "Amarinya",   "amazon": "com",    "ebay": "com",     "currency": "ETB",  "region": "Africa"},
    "fa":    {"name": "Persian",    "native": "Farsi",      "amazon": "ae",     "ebay": "com",     "currency": "IRR",  "region": "Middle East"},
    "km":    {"name": "Khmer",      "native": "Phiesa Khemaer", "amazon": "com", "ebay": "com",   "currency": "KHR",  "region": "Asia"},
    "lo":    {"name": "Lao",        "native": "Phasa Lao",  "amazon": "com",    "ebay": "com",     "currency": "LAK",  "region": "Asia"},
    "my":    {"name": "Burmese",    "native": "Myanmasa",   "amazon": "com",    "ebay": "com",     "currency": "MMK",  "region": "Asia"},
    "mn":    {"name": "Mongolian",  "native": "Mongol",     "amazon": "com",    "ebay": "com",     "currency": "MNT",  "region": "Asia"},
    "ne":    {"name": "Nepali",     "native": "Nepali",     "amazon": "com",    "ebay": "com",     "currency": "NPR",  "region": "Asia"},
    "si":    {"name": "Sinhala",    "native": "Sinhala",    "amazon": "com",    "ebay": "com",     "currency": "LKR",  "region": "Asia"},
    "ka":    {"name": "Georgian",   "native": "Kartuli",    "amazon": "com",    "ebay": "com",     "currency": "GEL",  "region": "Europe/Asia"},
    "hy":    {"name": "Armenian",   "native": "Hayeren",    "amazon": "com",    "ebay": "com",     "currency": "AMD",  "region": "Europe/Asia"},
    "az":    {"name": "Azerbaijani","native": "Azerbaycan", "amazon": "com",    "ebay": "com",     "currency": "AZN",  "region": "Europe/Asia"},
    "kk":    {"name": "Kazakh",     "native": "Kazaksha",   "amazon": "com",    "ebay": "com",     "currency": "KZT",  "region": "Asia"},
    "uz":    {"name": "Uzbek",      "native": "Ozbek",      "amazon": "com",    "ebay": "com",     "currency": "UZS",  "region": "Asia"},
}

AMAZON_STORES = {
    "com":    {"domain": "amazon.com",     "country": "United States",   "lang": "en", "currency": "USD", "region": "Americas"},
    "co.uk":  {"domain": "amazon.co.uk",   "country": "United Kingdom",  "lang": "en", "currency": "GBP", "region": "Europe"},
    "de":     {"domain": "amazon.de",      "country": "Germany",         "lang": "de", "currency": "EUR", "region": "Europe"},
    "fr":     {"domain": "amazon.fr",      "country": "France",          "lang": "fr", "currency": "EUR", "region": "Europe"},
    "it":     {"domain": "amazon.it",      "country": "Italy",           "lang": "it", "currency": "EUR", "region": "Europe"},
    "es":     {"domain": "amazon.es",      "country": "Spain",           "lang": "es", "currency": "EUR", "region": "Europe"},
    "co.jp":  {"domain": "amazon.co.jp",   "country": "Japan",           "lang": "ja", "currency": "JPY", "region": "Asia"},
    "ca":     {"domain": "amazon.ca",      "country": "Canada",          "lang": "en", "currency": "CAD", "region": "Americas"},
    "com.au": {"domain": "amazon.com.au",  "country": "Australia",       "lang": "en", "currency": "AUD", "region": "Oceania"},
    "in":     {"domain": "amazon.in",      "country": "India",           "lang": "en", "currency": "INR", "region": "Asia"},
    "com.mx": {"domain": "amazon.com.mx",  "country": "Mexico",          "lang": "es", "currency": "MXN", "region": "Americas"},
    "com.br": {"domain": "amazon.com.br",  "country": "Brazil",          "lang": "pt", "currency": "BRL", "region": "Americas"},
    "nl":     {"domain": "amazon.nl",      "country": "Netherlands",     "lang": "nl", "currency": "EUR", "region": "Europe"},
    "se":     {"domain": "amazon.se",      "country": "Sweden",          "lang": "sv", "currency": "SEK", "region": "Europe"},
    "pl":     {"domain": "amazon.pl",      "country": "Poland",          "lang": "pl", "currency": "PLN", "region": "Europe"},
    "ae":     {"domain": "amazon.ae",      "country": "UAE",             "lang": "ar", "currency": "AED", "region": "Middle East"},
    "sa":     {"domain": "amazon.sa",      "country": "Saudi Arabia",    "lang": "ar", "currency": "SAR", "region": "Middle East"},
    "sg":     {"domain": "amazon.sg",      "country": "Singapore",       "lang": "en", "currency": "SGD", "region": "Asia"},
    "tr":     {"domain": "amazon.com.tr",  "country": "Turkey",          "lang": "tr", "currency": "TRY", "region": "Europe/Asia"},
    "com.be": {"domain": "amazon.com.be",  "country": "Belgium",         "lang": "nl", "currency": "EUR", "region": "Europe"},
    "eg":     {"domain": "amazon.eg",      "country": "Egypt",           "lang": "ar", "currency": "EGP", "region": "Africa"},
    "cn":     {"domain": "amazon.cn",      "country": "China",           "lang": "zh", "currency": "CNY", "region": "Asia"},
}

EBAY_STORES = {
    "com":    {"domain": "ebay.com",     "country": "United States",    "lang": "en", "currency": "USD", "region": "Americas"},
    "co.uk":  {"domain": "ebay.co.uk",   "country": "United Kingdom",   "lang": "en", "currency": "GBP", "region": "Europe"},
    "de":     {"domain": "ebay.de",      "country": "Germany",          "lang": "de", "currency": "EUR", "region": "Europe"},
    "fr":     {"domain": "ebay.fr",      "country": "France",           "lang": "fr", "currency": "EUR", "region": "Europe"},
    "it":     {"domain": "ebay.it",      "country": "Italy",            "lang": "it", "currency": "EUR", "region": "Europe"},
    "es":     {"domain": "ebay.es",      "country": "Spain",            "lang": "es", "currency": "EUR", "region": "Europe"},
    "com.au": {"domain": "ebay.com.au",  "country": "Australia",        "lang": "en", "currency": "AUD", "region": "Oceania"},
    "ca":     {"domain": "ebay.ca",      "country": "Canada",           "lang": "en", "currency": "CAD", "region": "Americas"},
    "ch":     {"domain": "ebay.ch",      "country": "Switzerland",      "lang": "de", "currency": "CHF", "region": "Europe"},
    "at":     {"domain": "ebay.at",      "country": "Austria",          "lang": "de", "currency": "EUR", "region": "Europe"},
    "be":     {"domain": "ebay.be",      "country": "Belgium",          "lang": "nl", "currency": "EUR", "region": "Europe"},
    "nl":     {"domain": "ebay.nl",      "country": "Netherlands",      "lang": "nl", "currency": "EUR", "region": "Europe"},
    "pl":     {"domain": "ebay.pl",      "country": "Poland",           "lang": "pl", "currency": "PLN", "region": "Europe"},
    "ie":     {"domain": "ebay.ie",      "country": "Ireland",          "lang": "en", "currency": "EUR", "region": "Europe"},
    "sg":     {"domain": "ebay.sg",      "country": "Singapore",        "lang": "en", "currency": "SGD", "region": "Asia"},
    "hk":     {"domain": "ebay.hk",      "country": "Hong Kong",        "lang": "zh", "currency": "HKD", "region": "Asia"},
    "my":     {"domain": "ebay.my",      "country": "Malaysia",         "lang": "ms", "currency": "MYR", "region": "Asia"},
    "ph":     {"domain": "ebay.ph",      "country": "Philippines",      "lang": "tl", "currency": "PHP", "region": "Asia"},
    "th":     {"domain": "ebay.co.th",   "country": "Thailand",         "lang": "th", "currency": "THB", "region": "Asia"},
    "vn":     {"domain": "ebay.vn",      "country": "Vietnam",          "lang": "vi", "currency": "VND", "region": "Asia"},
    "in":     {"domain": "ebay.in",      "country": "India",            "lang": "hi", "currency": "INR", "region": "Asia"},
    "il":     {"domain": "ebay.co.il",   "country": "Israel",           "lang": "he", "currency": "ILS", "region": "Middle East"},
}

AMAZON_STORE_TAG_MAP = {
    "com": "amazon_tag_us", "co.uk": "amazon_tag_uk", "de": "amazon_tag_de",
    "fr": "amazon_tag_fr", "it": "amazon_tag_it", "es": "amazon_tag_es",
    "co.jp": "amazon_tag_jp", "ca": "amazon_tag_ca", "com.au": "amazon_tag_au",
    "in": "amazon_tag_in", "com.mx": "amazon_tag_mx", "com.br": "amazon_tag_br",
    "nl": "amazon_tag_nl", "se": "amazon_tag_se", "pl": "amazon_tag_pl",
    "ae": "amazon_tag_ae", "sa": "amazon_tag_sa", "sg": "amazon_tag_sg",
    "tr": "amazon_tag_tr", "com.be": "amazon_tag_be", "eg": "amazon_tag_eg",
    "cn": "amazon_tag_cn",
}

EBAY_STORE_TAG_MAP = {
    "com": "ebay_campaign_us", "co.uk": "ebay_campaign_uk", "de": "ebay_campaign_de",
    "fr": "ebay_campaign_fr", "it": "ebay_campaign_it", "es": "ebay_campaign_es",
    "com.au": "ebay_campaign_au", "ca": "ebay_campaign_ca",
    "ch": "ebay_campaign_ch", "at": "ebay_campaign_at", "be": "ebay_campaign_be",
    "nl": "ebay_campaign_nl", "pl": "ebay_campaign_pl", "ie": "ebay_campaign_ie",
    "sg": "ebay_campaign_sg", "hk": "ebay_campaign_hk", "my": "ebay_campaign_my",
    "ph": "ebay_campaign_ph", "th": "ebay_campaign_th", "vn": "ebay_campaign_vn",
    "in": "ebay_campaign_in", "il": "ebay_campaign_il",
}


def get_amazon_store(language: str) -> str:
    info = LANGUAGES.get(language, LANGUAGES["en"])
    return info["amazon"]


def get_ebay_store(language: str) -> str:
    info = LANGUAGES.get(language, LANGUAGES["en"])
    return info["ebay"]


def get_currency(language: str) -> str:
    return LANGUAGES.get(language, LANGUAGES["en"])["currency"]


def get_language_name(language: str) -> str:
    return LANGUAGES.get(language, LANGUAGES["en"])["native"]


def get_region(language: str) -> str:
    return LANGUAGES.get(language, LANGUAGES["en"])["region"]


def detect_language(text: str) -> str:
    text = text.lower()
    lang_map = {
        "en": ["english", "united states", "united kingdom", "australia"],
        "es": ["espanol", "espanola", "espana", "mexico", "argentina", "colombia"],
        "fr": ["francais", "francaise", "france", "belgique"],
        "de": ["deutsch", "deutsche", "deutschland", "german", "oesterreich"],
        "it": ["italiano", "italiana", "italia"],
        "pt": ["portugues", "portuguesa", "brasil"],
        "ja": ["japanese", "nihongo", "japan"],
        "zh": ["chinese", "zhongwen", "china"],
        "ko": ["korean", "hangugo", "korea"],
        "ar": ["arabic", "arabiya", "arabian", "middle east"],
        "hi": ["hindi", "india"],
        "nl": ["dutch", "nederlands", "nederland"],
        "sv": ["swedish", "svenska", "sweden"],
        "pl": ["polish", "polski", "poland", "polska"],
        "tr": ["turkish", "turkce", "turkey", "turkiye"],
        "th": ["thai", "phasa thai", "thailand"],
        "vi": ["vietnamese", "tieng viet", "vietnam"],
        "id": ["indonesian", "bahasa indonesia", "indonesia"],
        "ms": ["malay", "bahasa melayu", "malaysia"],
        "tl": ["filipino", "tagalog", "philippines"],
        "ru": ["russian", "russkiy", "russia"],
        "uk": ["ukrainian", "ukrainska", "ukraine"],
        "he": ["hebrew", "ivrit", "israel"],
        "el": ["greek", "ellinika", "greece"],
        "cs": ["czech", "cestina", "czech republic"],
        "ro": ["romanian", "romana", "romania"],
        "hu": ["hungarian", "magyar", "hungary"],
        "da": ["danish", "dansk", "denmark"],
        "fi": ["finnish", "suomi", "finland"],
        "nb": ["norwegian", "norsk", "norway"],
        "bn": ["bengali", "bangla", "bangladesh"],
        "ta": ["tamil", "tamil nadu"],
        "te": ["telugu", "andhra"],
        "mr": ["marathi", "maharashtra"],
        "ur": ["urdu", "pakistan"],
        "sw": ["swahili", "kiswahili", "tanzania", "kenya"],
        "ha": ["hausa", "nigeria", "niger"],
        "yo": ["yoruba", "nigeria"],
        "ig": ["igbo", "nigeria"],
        "am": ["amharic", "amarinya", "ethiopia"],
        "fa": ["persian", "farsi", "iran"],
        "km": ["khmer", "cambodia"],
        "lo": ["lao", "laos"],
        "my": ["burmese", "myanmar"],
        "mn": ["mongolian", "mongol", "mongolia"],
        "ne": ["nepali", "nepal"],
        "si": ["sinhala", "sri lanka"],
        "ka": ["georgian", "kartuli", "georgia"],
        "hy": ["armenian", "hayeren", "armenia"],
        "az": ["azerbaijani", "azerbaijan"],
        "kk": ["kazakh", "kazakhstan"],
        "uz": ["uzbek", "uzbekistan"],
    }
    for code, keywords in lang_map.items():
        if any(kw in text for kw in keywords):
            return code
    return "en"
