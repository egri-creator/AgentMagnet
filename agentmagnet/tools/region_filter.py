"""Region-aware store filtering. EU users see EU stores, US users see US stores. No mixing."""

# Region mapping for federated stores
STORE_REGIONS = {
    "bestbuy": ["americas", "us", "ca"],
    "walmart": ["americas", "us", "ca", "mx"],
    "target": ["americas", "us"],
    "costco": ["americas", "us", "ca", "mx"],
    "homedepot": ["americas", "us", "ca"],
    "lowes": ["americas", "us", "ca"],
    "newegg": ["americas", "us", "ca"],
    "bhphotovideo": ["americas", "us"],
    "macys": ["americas", "us"],
    "nordstrom": ["americas", "us", "ca"],
    "staples": ["americas", "us", "ca"],
    "officedepot": ["americas", "us", "ca"],
    # EU stores (future integration)
    "zalando": ["europe", "eu", "de", "fr", "it", "es", "nl", "at", "pl", "se", "dk", "fi", "no", "be", "lu"],
    "aboutyou": ["europe", "eu", "de", "at", "ch"],
    "otrium": ["europe", "eu", "nl", "de", "fr", "be"],
    "bol": ["europe", "eu", "nl", "be"],
}

# Language → primary region
LANG_REGION = {
    "en": "americas", "es": "europe", "fr": "europe", "de": "europe",
    "it": "europe", "pt": "americas", "ja": "asia", "zh": "asia",
    "ko": "asia", "ar": "middleeast", "hi": "asia", "nl": "europe",
    "sv": "europe", "pl": "europe", "tr": "europe", "th": "asia",
    "vi": "asia", "id": "asia", "ms": "asia", "tl": "asia",
    "ru": "europe", "uk": "europe", "he": "middleeast", "el": "europe",
    "cs": "europe", "ro": "europe", "hu": "europe", "da": "europe",
    "fi": "europe", "nb": "europe", "bn": "asia", "ta": "asia",
    "te": "asia", "mr": "asia", "ur": "asia", "sw": "africa",
    "ha": "africa", "yo": "africa", "ig": "africa", "am": "africa",
    "fa": "middleeast", "km": "asia", "lo": "asia", "my": "asia",
    "mn": "asia", "ne": "asia", "si": "asia", "ka": "europe",
    "hy": "europe", "az": "europe", "kk": "asia", "uz": "asia",
    "ceb": "asia", "ps": "asia", "sd": "asia", "ku": "middleeast",
    "tg": "asia", "tk": "asia", "dv": "asia", "ti": "africa",
    "so": "africa", "zu": "africa", "xh": "africa", "mg": "africa",
    "rw": "africa", "ny": "africa", "st": "africa", "sn": "africa",
    "mt": "europe", "lb": "europe", "fy": "europe",
    "mi": "oceania", "sm": "oceania", "to": "oceania", "fj": "oceania",
    "ht": "americas", "gn": "americas", "ay": "americas", "qu": "americas",
    "mfe": "africa", "sg": "africa", "rn": "africa", "lg": "africa",
    "om": "africa", "tw": "africa",
}

# Region → Amazon store codes (primary + cross-border)
# EU: show all EU Amazons so a Spanish agent can buy from Amazon.de
REGION_AMAZON_STORES = {
    "europe": ["co.uk", "de", "fr", "es", "it", "nl", "se", "pl", "com.be"],
    "americas": ["com", "ca", "com.mx", "com.br"],
    "asia": ["co.jp", "in", "sg", "cn"],
    "middleeast": ["ae", "sa"],
    "oceania": ["com.au"],
    "africa": ["com"],
}

REGION_EBAY_STORES = {
    "europe": ["co.uk", "de", "fr", "es", "it", "ch", "at", "be", "nl", "pl", "ie"],
    "americas": ["com", "ca"],
    "asia": ["sg", "hk", "my", "ph", "th", "vn", "in"],
    "middleeast": ["il"],
    "oceania": ["com.au"],
    "africa": ["com"],
}


def detect_region(language: str, country: str = "") -> str:
    """Detect user's region from language code, with optional country override."""
    if country:
        country_region = {
            "us": "americas", "uk": "europe", "de": "europe", "fr": "europe",
            "es": "europe", "it": "europe", "jp": "asia", "cn": "asia",
            "in": "asia", "br": "americas", "mx": "americas", "ca": "americas",
            "au": "oceania", "ae": "middleeast", "sa": "middleeast",
            "nl": "europe", "se": "europe", "pl": "europe", "sg": "asia",
        }
        if country in country_region:
            return country_region[country]
    return LANG_REGION.get(language, "americas")


def federated_stores_for_region(region: str) -> list[str]:
    """Get federated store IDs that serve a given region."""
    allowed = []
    for store_id, regions in STORE_REGIONS.items():
        if any(r == region or r == region[:3] for r in regions):
            allowed.append(store_id)
    return allowed


def amazon_stores_for_region(region: str) -> list[str]:
    """Get Amazon store codes for a region."""
    return REGION_AMAZON_STORES.get(region, ["com"])


def ebay_stores_for_region(region: str) -> list[str]:
    """Get eBay store codes for a region."""
    return REGION_EBAY_STORES.get(region, ["com"])


def filter_by_region(stores: dict, region: str) -> dict:
    """Filter a store dict to only include stores in the given region."""
    if not region or region == "all":
        return stores
    allowed_fed = federated_stores_for_region(region)
    filtered = {}
    for sid, info in stores.items():
        if sid in allowed_fed:
            filtered[sid] = info
    return filtered


def get_region_message(region: str, language: str) -> str:
    """User-facing message about what region they're seeing."""
    region_names = {
        "europe": "Europe (EU)",
        "americas": "Americas (US, CA, MX, BR)",
        "asia": "Asia (JP, IN, SG, CN)",
        "middleeast": "Middle East (AE, SA, IL)",
        "oceania": "Oceania (AU)",
        "africa": "Africa",
    }
    name = region_names.get(region, region.title())
    return (
        f"🌍 Showing {name} stores. "
        f"Add region=all for global results, or region=americas for US stores."
    )
