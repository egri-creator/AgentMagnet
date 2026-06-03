"""Region-aware store filtering.
CRITICAL: Language does NOT equal country.
'en' = US, UK, AU, NZ, CA, IN, IE, ZA, SG, PH, NG, KE, GH, HK, MY, MT, PK — 20+ countries
'es' = ES, MX, CO, AR, PE, CL, EC, GT, CU, BO, DO, HN, PY, SV, NI, CR, PA, UY, VE — 20+ countries
NEVER guess country from language. Agents MUST specify their country."""

# Which countries each federated store ships to
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

# Amazon store codes per country — definitive list
COUNTRY_AMAZON = {
    "us": "com", "uk": "co.uk", "de": "de", "fr": "fr",
    "es": "es", "it": "it", "jp": "co.jp", "ca": "ca",
    "au": "com.au", "in": "in", "mx": "com.mx", "br": "com.br",
    "co": "com.co", "nl": "nl", "se": "se", "pl": "pl", "ae": "ae",
    "sa": "sa", "sg": "sg", "tr": "com.tr", "be": "com.be",
    "eg": "eg", "cn": "cn",
}

# EU countries (for EU cross-border shipping)
EU_COUNTRIES = {"es", "de", "fr", "it", "nl", "be", "at", "pl", "se", "dk",
                "fi", "ie", "pt", "gr", "lu", "lt", "lv", "ee", "sk", "si",
                "cz", "hu", "ro", "bg", "hr", "cy", "mt"}

# EEA + CH: countries that participate in EU single market
EEA_COUNTRIES = EU_COUNTRIES | {"no", "is", "li", "ch"}

COUNTRY_NAME = {
    "es": "España", "mx": "México", "co": "Colombia", "ar": "Argentina",
    "pe": "Perú", "cl": "Chile", "ec": "Ecuador", "gt": "Guatemala",
    "cu": "Cuba", "bo": "Bolivia", "do": "República Dominicana",
    "hn": "Honduras", "py": "Paraguay", "sv": "El Salvador",
    "ni": "Nicaragua", "cr": "Costa Rica", "pa": "Panamá",
    "uy": "Uruguay", "ve": "Venezuela", "gq": "Guinea Ecuatorial",
    "us": "United States", "uk": "United Kingdom", "de": "Alemania",
    "fr": "Francia", "it": "Italia", "jp": "Japan", "cn": "China",
    "br": "Brazil", "ca": "Canada", "au": "Australia", "in": "India",
    "nl": "Netherlands", "se": "Sweden", "pl": "Poland", "ae": "UAE",
    "sa": "Saudi Arabia", "sg": "Singapore", "be": "Belgium",
    "at": "Austria", "ch": "Switzerland", "ie": "Ireland",
    "nz": "New Zealand", "za": "South Africa",
}


def validate_country(country: str) -> bool:
    """Check if a country code is valid (has an Amazon store)."""
    return country.lower() in COUNTRY_AMAZON


def stores_that_ship_to(country: str) -> list[str]:
    """Federated store IDs that ship to a given country."""
    country = country.lower()
    allowed = []
    for store_id, ships_to in STORE_SHIPPING.items():
        if ships_to == "__eu__":
            if country in EU_COUNTRIES or country in {"uk", "ch", "no", "is"}:
                allowed.append(store_id)
        elif country in ships_to:
            allowed.append(store_id)
    return allowed


def amazon_stores_for(country: str, scope: str = "country") -> list[str]:
    """Amazon stores available. scope=country: just yours. scope=region: +EU. scope=all: everything."""
    country = country.lower()
    own = COUNTRY_AMAZON.get(country, "com")

    if scope == "country":
        return [own]

    if scope == "region":
        if country in EU_COUNTRIES or country in {"uk", "ch", "no", "is"}:
            # EU cross-border: show all EU Amazon stores
            eu_stores = list(dict.fromkeys(
                [own] + [COUNTRY_AMAZON[c] for c in EU_COUNTRIES if c in COUNTRY_AMAZON]
            ))
            return eu_stores
        # For non-EU countries, region = same country (no cross-border)
        return [own]

    # scope = all: everything
    return list(COUNTRY_AMAZON.values())


def federated_stores_for(country: str, scope: str = "country") -> list[str]:
    """Federated stores available for a country."""
    country = country.lower()
    country_stores = stores_that_ship_to(country)

    if scope == "country":
        return country_stores

    if scope == "region":
        if country in EU_COUNTRIES or country in {"uk", "ch", "no", "is"}:
            # EU: show all EU federated stores
            eu_stores = stores_that_ship_to("de")  # German stores ship to all EU
            return list(dict.fromkeys(country_stores + eu_stores))
        return country_stores

    return list(STORE_SHIPPING.keys())


def get_scope_message(country: str, scope: str) -> dict:
    """User-facing message explaining what they're seeing and why."""
    country_display = COUNTRY_NAME.get(country, country.upper())

    if scope == "country":
        msg = f"📦 Mostrando solo tiendas que envían a {country_display}"
        detail = "Resultados limitados a tu país para evitar aduanas y envíos largos"
        suggestions = {
            "widen_to_region": "Ampliar a tu región (ej: Europa entera) con scope=region",
            "widen_to_all": "Ver todas las tiendas globales con scope=all",
        }
    elif scope == "region":
        if country in EU_COUNTRIES:
            msg = f"🌍 Mostrando tiendas de toda la UE (envío rápido a {country_display})"
            detail = "Comprar en otro país UE es rápido y sin aduanas"
        else:
            msg = f"🌍 Mostrando tiendas de tu región"
            detail = "Pueden aplicar gastos de envío internacional"
        suggestions = {
            "narrow_to_country": f"Limitar a {country_display} con scope=country",
            "widen_to_all": "Ver tiendas globales con scope=all",
        }
    else:
        msg = "🌐 Mostrando TODAS las tiendas globales"
        detail = "⚠️ Pueden aplicar aduanas, impuestos de importación y envíos largos"
        suggestions = {
            "narrow_to_country": f"Limitar a {country_display} con scope=country",
            "narrow_to_region": "Limitar a tu región con scope=region",
        }

    return {
        "country": country,
        "country_name": country_display,
        "scope": scope,
        "message": msg,
        "detail": detail,
        "suggestions": suggestions,
    }
