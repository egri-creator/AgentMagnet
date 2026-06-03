"""Region-aware store filtering — 3 levels: country, region, global.
Language alone is NOT enough: 'es' = Spain OR Colombia OR Mexico.
Always detect COUNTRY first, then derive region."""

# Which countries each federated store ships to
# EU stores ship to ALL EU countries (EU law — free movement of goods)
STORE_SHIPPING = {
    "bestbuy": ["us", "ca"],
    "walmart": ["us", "ca", "mx"],
    "target": ["us"],
    "costco": ["us", "ca", "mx", "uk", "jp", "au", "kr", "es", "is"],
    "homedepot": ["us", "ca"],
    "lowes": ["us", "ca"],
    "newegg": ["us", "ca"],
    "bhphotovideo": ["us", "ca", "mx"],
    "macys": ["us"],
    "nordstrom": ["us", "ca"],
    "staples": ["us", "ca"],
    "officedepot": ["us", "ca"],
    "zalando": "__eu__",
    "aboutyou": "__eu__",
    "otrium": "__eu__",
    "bol": ["nl", "be"],
}

EU_COUNTRIES = {"es", "de", "fr", "it", "nl", "be", "at", "pl", "se", "dk",
                "fi", "ie", "pt", "gr", "lu", "lt", "lv", "ee", "sk", "si",
                "cz", "hu", "ro", "bg", "hr", "cy", "mt", "fi", "se"}

# Language → default country (IMPERFECT — same language in multiple countries)
# The agent MUST specify 'country' for accuracy. This is just a fallback.
LANG_COUNTRY = {
    "en": "us",       # English → US (could be UK, AU, CA, etc.)
    "es": "es",        # Spanish → SPAIN (NOT Latin America — use country param)
    "fr": "fr",        # French → France (could be CA, BE, CH)
    "de": "de",        # German → Germany (could be AT, CH)
    "it": "it",        # Italian → Italy (could be CH)
    "pt": "br",        # Portuguese → Brazil (could be PT)
    # ... rest unchanged
}

# Language → region (ONLY when country is unknown)
LANG_REGION = {
    "en": "americas",  # English defaults to Americas
    "es": "europe",    # Spanish defaults to Spain/Europe (override with country)
    "fr": "europe",
    "de": "europe",
    "it": "europe",
    "pt": "americas",
    # ... others unchanged
}

# Country → Amazon store codes
COUNTRY_AMAZON = {
    "us": ["com"], "uk": ["co.uk"], "de": ["de"], "fr": ["fr"],
    "es": ["es"], "it": ["it"], "jp": ["co.jp"], "ca": ["ca"],
    "au": ["com.au"], "in": ["in"], "mx": ["com.mx"], "br": ["com.br"],
    "nl": ["nl"], "se": ["se"], "pl": ["pl"], "ae": ["ae"],
    "sa": ["sa"], "sg": ["sg"], "tr": ["com.tr"], "be": ["com.be"],
    "eg": ["eg"], "cn": ["cn"],
}

# Region → Amazon store codes (for cross-border within region)
REGION_AMAZON = {
    "europe": ["co.uk", "de", "fr", "es", "it", "nl", "se", "pl", "com.be"],
    "americas": ["com", "ca", "com.mx", "com.br"],
    "asia": ["co.jp", "in", "sg", "cn"],
    "middleeast": ["ae", "sa"],
    "oceania": ["com.au"],
    "africa": ["com"],
}

REGION_EBAY = {
    "europe": ["co.uk", "de", "fr", "es", "it", "ch", "at", "be", "nl", "pl", "ie"],
    "americas": ["com", "ca"],
    "asia": ["sg", "hk", "my", "ph", "th", "vn", "in"],
    "middleeast": ["il"],
    "oceania": ["com.au"],
    "africa": ["com"],
}

# Federated store IDs by region
REGION_FEDERATED = {
    "europe": ["zalando", "aboutyou", "otrium", "bol"],
    "americas": ["bestbuy", "walmart", "target", "costco", "homedepot", "lowes",
                 "newegg", "bhphotovideo", "macys", "nordstrom", "staples", "officedepot"],
    "asia": ["newegg"],
    "middleeast": [],
    "oceania": [],
    "africa": [],
}

COUNTRY_NAME = {
    "es": "España", "de": "Alemania", "fr": "Francia", "it": "Italia",
    "us": "United States", "uk": "United Kingdom", "jp": "Japan",
    "cn": "China", "br": "Brazil", "mx": "Mexico", "ca": "Canada",
    "au": "Australia", "in": "India", "nl": "Netherlands", "se": "Sweden",
    "pl": "Poland", "ae": "UAE", "sa": "Saudi Arabia", "sg": "Singapore",
}

REGION_NAME = {
    "europe": "Europa (UE)",
    "americas": "América (US, CA, MX, BR)",
    "asia": "Asia",
    "middleeast": "Oriente Medio",
    "oceania": "Oceanía",
    "africa": "África",
}


def detect_country(language: str, country: str = "") -> str:
    """Detect user's country from language code or explicit country."""
    if country and country.lower() in COUNTRY_AMAZON:
        return country.lower()
    return LANG_COUNTRY.get(language, "us")


def detect_region_from_country(country: str) -> str:
    """Detect region from country code."""
    if country in EU_COUNTRIES or country in {"uk", "ch", "no", "is", "gb"}:
        return "europe"
    na_countries = {"us", "ca", "mx", "br", "ar", "cl", "co", "pe"}
    if country in na_countries:
        return "americas"
    asia_countries = {"jp", "cn", "in", "sg", "kr", "th", "vn", "id", "my", "ph", "hk", "tw"}
    if country in asia_countries:
        return "asia"
    me_countries = {"ae", "sa", "il", "iq", "ir", "qa", "kw", "om", "bh"}
    if country in me_countries:
        return "middleeast"
    oceania_countries = {"au", "nz", "ws", "to", "fj", "pg"}
    if country in oceania_countries:
        return "oceania"
    africa_countries = {"za", "ng", "ke", "tz", "eg", "ma", "gh", "tn", "dz"}
    if country in africa_countries:
        return "africa"
    return "americas"


def stores_that_ship_to(country: str) -> list[str]:
    """Get federated store IDs that ship to a given country."""
    allowed = []
    for store_id, ships_to in STORE_SHIPPING.items():
        if ships_to == "__eu__":
            if country in EU_COUNTRIES:
                allowed.append(store_id)
        elif country in ships_to:
            allowed.append(store_id)
    return allowed


def amazon_stores_for(country: str, scope: str = "country") -> list[str]:
    """Get Amazon store codes. Scope: country | region | all"""
    if scope == "all":
        return list(COUNTRY_AMAZON.values())
    country_stores = COUNTRY_AMAZON.get(country, ["com"])
    if scope == "country":
        return country_stores
    # region scope: country + region neighbors
    region = detect_region_from_country(country)
    region_stores = REGION_AMAZON.get(region, [])
    # Merge, keeping order: own country first
    all_stores = list(dict.fromkeys(country_stores + region_stores))
    return all_stores


def ebay_stores_for(country: str, scope: str = "region") -> list[str]:
    """Get eBay store codes for a country/region."""
    if scope == "all":
        return []
    region = detect_region_from_country(country)
    return REGION_EBAY.get(region, ["com"])


def federated_stores_for(country: str, scope: str = "country") -> list[str]:
    """Get federated stores available for a country."""
    if scope == "all":
        return list(STORE_SHIPPING.keys())
    country_stores = stores_that_ship_to(country)
    if scope == "country":
        return country_stores
    # region scope: country + regional stores
    region = detect_region_from_country(country)
    region_stores = REGION_FEDERATED.get(region, [])
    all_stores = list(dict.fromkeys(country_stores + region_stores))
    return all_stores


def get_scope_message(country: str, scope: str, language: str = "en") -> dict:
    """User-facing message about scope."""
    country_display = COUNTRY_NAME.get(country, country.upper())

    if scope == "country":
        msg = f"📦 Mostrando tiendas que envían a {country_display}"
        detail = "Solo tiendas con envío confirmado a tu país"
    elif scope == "region":
        region = detect_region_from_country(country)
        region_display = REGION_NAME.get(region, region)
        msg = f"🌍 Mostrando tiendas de {region_display}"
        detail = f"Incluye tiendas de la región que envían a {country_display}"
    else:
        msg = "🌐 Mostrando todas las tiendas globales"
        detail = "Pueden aplicar gastos de aduana e importación"

    return {
        "country": country,
        "country_name": country_display,
        "scope": scope,
        "message": msg,
        "detail": detail,
        "can_widen": scope != "all",
        "can_narrow": scope != "country",
        "suggestions": {
            "country": f"Limitar a tiendas que envían a {country_display}",
            "region": f"Ampliar a tiendas de {REGION_NAME.get(detect_region_from_country(country), 'la región')}",
            "all": "Ver todas las tiendas globales",
        },
    }
