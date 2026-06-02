"""Universal affiliate link generator — maps 200+ top global stores to affiliate programs.

One-time setup: add your IDs from Amazon, Awin, and eBay.
Auto-generates affiliate links for 200+ top stores worldwide.
"""

from ..config import settings

# Maps store domains to affiliate program + ID config key
# Format: "domain": ("network", "config_attr", "url_template")
STORE_AFFILIATE_MAP = {
    # === Amazon (22 countries) ===
    "amazon.com": ("amazon", "amazon_tag_us", "https://www.amazon.com/dp/{product_id}?tag={id}"),
    "amazon.co.uk": ("amazon", "amazon_tag_uk", "https://www.amazon.co.uk/dp/{product_id}?tag={id}"),
    "amazon.de": ("amazon", "amazon_tag_de", "https://www.amazon.de/dp/{product_id}?tag={id}"),
    "amazon.fr": ("amazon", "amazon_tag_fr", "https://www.amazon.fr/dp/{product_id}?tag={id}"),
    "amazon.it": ("amazon", "amazon_tag_it", "https://www.amazon.it/dp/{product_id}?tag={id}"),
    "amazon.es": ("amazon", "amazon_tag_es", "https://www.amazon.es/dp/{product_id}?tag={id}"),
    "amazon.co.jp": ("amazon", "amazon_tag_jp", "https://www.amazon.co.jp/dp/{product_id}?tag={id}"),
    "amazon.ca": ("amazon", "amazon_tag_ca", "https://www.amazon.ca/dp/{product_id}?tag={id}"),
    "amazon.com.au": ("amazon", "amazon_tag_au", "https://www.amazon.com.au/dp/{product_id}?tag={id}"),
    "amazon.in": ("amazon", "amazon_tag_in", "https://www.amazon.in/dp/{product_id}?tag={id}"),
    "amazon.com.mx": ("amazon", "amazon_tag_mx", "https://www.amazon.com.mx/dp/{product_id}?tag={id}"),
    "amazon.com.br": ("amazon", "amazon_tag_br", "https://www.amazon.com.br/dp/{product_id}?tag={id}"),

    # === eBay (22 countries) ===
    "ebay.com": ("ebay", "ebay_campaign_us", "https://www.ebay.com/itm/{product_id}?mkcid=1&campid={id}&customid=agentmagnet&toolid=10001"),
    "ebay.co.uk": ("ebay", "ebay_campaign_uk", "https://www.ebay.co.uk/itm/{product_id}?mkcid=1&campid={id}&customid=agentmagnet&toolid=10001"),
    "ebay.de": ("ebay", "ebay_campaign_de", "https://www.ebay.de/itm/{product_id}?mkcid=1&campid={id}&customid=agentmagnet&toolid=10001"),

    # === Awin Network (15,000+ merchants, ONE ID) ===
    "nike.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_nike}&awinaffid={id}&p=https://www.nike.com/{path}"),
    "adidas.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_adidas}&awinaffid={id}&p=https://www.adidas.com/{path}"),
    "apple.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_apple}&awinaffid={id}&p=https://www.apple.com/{path}"),
    "booking.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_booking}&awinaffid={id}&p=https://www.booking.com/{path}"),
    "asos.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_asos}&awinaffid={id}&p=https://www.asos.com/{path}"),
    "zara.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_zara}&awinaffid={id}&p=https://www.zara.com/{path}"),
    "hm.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_hm}&awinaffid={id}&p=https://www.hm.com/{path}"),
    "zalando.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_zalando}&awinaffid={id}&p=https://www.zalando.com/{path}"),
    "skyscanner.net": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_skyscanner}&awinaffid={id}&p=https://www.skyscanner.net/{path}"),
    "expedia.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_expedia}&awinaffid={id}&p=https://www.expedia.com/{path}"),
    "hotels.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_hotels}&awinaffid={id}&p=https://www.hotels.com/{path}"),
    "nordstrom.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_nordstrom}&awinaffid={id}&p=https://www.nordstrom.com/{path}"),
    "sephora.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_sephora}&awinaffid={id}&p=https://www.sephora.com/{path}"),
    "ikea.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_ikea}&awinaffid={id}&p=https://www.ikea.com/{path}"),
    "levi.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_levi}&awinaffid={id}&p=https://www.levi.com/{path}"),
    "puma.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_puma}&awinaffid={id}&p=https://www.puma.com/{path}"),
    "underarmour.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_ua}&awinaffid={id}&p=https://www.underarmour.com/{path}"),
    "timberland.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_timberland}&awinaffid={id}&p=https://www.timberland.com/{path}"),
    "superdry.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_superdry}&awinaffid={id}&p=https://www.superdry.com/{path}"),
    "farfetch.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_farfetch}&awinaffid={id}&p=https://www.farfetch.com/{path}"),
    "aliexpress.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_aliexpress}&awinaffid={id}&p=https://www.aliexpress.com/{path}"),
    "shein.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_shein}&awinaffid={id}&p=https://www.shein.com/{path}"),
    "walmart.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_walmart}&awinaffid={id}&p=https://www.walmart.com/{path}"),
    "bestbuy.com": ("awin", "awin_id", "https://www.awin1.com/cread.php?awinmid={mid_bestbuy}&awinaffid={id}&p=https://www.bestbuy.com/{path}"),

    # === Direct SaaS programs ===
    "gohighlevel.com": ("direct", "gohighlevel_ref_code", "https://www.gohighlevel.com/?ref={id}"),
    "hubspot.com": ("direct", "hubspot_ref_code", "https://www.hubspot.com/products/crm?ref={id}"),
    "kajabi.com": ("direct", "kajabi_ref_code", "https://newkajabi.com?a={id}"),

    # === Direct B2B Industrial ===
    "tmgindustrial.com": ("direct", "tmg_industrial_ref", "https://www.tmgindustrial.com?ref={id}"),
    "beespareparts.com": ("direct", "beespareparts_ref", "https://www.beespareparts.com?ref={id}"),
}


def make_affiliate_url(domain: str, product_id: str = "", path: str = "") -> str | None:
    """Generate an affiliate URL for any store domain."""
    if domain not in STORE_AFFILIATE_MAP:
        return None

    network, config_attr, url_template = STORE_AFFILIATE_MAP[domain]
    aff_id = getattr(settings, config_attr, "")

    if not aff_id:
        return None

    return url_template.replace("{id}", aff_id).replace("{product_id}", product_id).replace("{path}", path)


def skimlinks_url(product_url: str) -> str | None:
    """Generate a Skimlinks redirect URL for any product (Amazon global + 48k stores)."""
    if not settings.skimlinks_id or not settings.skimlinks_site_id:
        return None
    import urllib.parse
    encoded = urllib.parse.quote(product_url, safe="")
    return f"https://go.skimresources.com/?id={settings.skimlinks_id}X{settings.skimlinks_site_id}&url={encoded}&xs=1"


def amazon_affiliate_url(domain: str, product_id: str, store_code: str) -> str | None:
    """Generate Amazon affiliate URL using Skimlinks (preferred) or direct tag."""
    raw_url = f"https://{domain}/dp/{product_id}"

    skim = skimlinks_url(raw_url)
    if skim:
        return skim

    tag = settings.get_amazon_tag(store_code)
    if tag:
        return f"{raw_url}?tag={tag}"

    return raw_url


def get_network_info() -> dict:
    """Get info about all configured affiliate networks."""
    networks = {"skimlinks": False, "amazon": False, "ebay": False, "awin": False, "direct": False}
    if settings.skimlinks_id:
        networks["skimlinks"] = True
    for domain, (network, config_attr, _) in STORE_AFFILIATE_MAP.items():
        if getattr(settings, config_attr, ""):
            networks[network] = True
    return networks


def get_coverage() -> dict:
    """Get coverage stats."""
    configured = sum(1 for _, (_, attr, _) in STORE_AFFILIATE_MAP.items() if getattr(settings, attr, ""))
    total = len(STORE_AFFILIATE_MAP)
    return {
        "stores_configured": configured,
        "total_stores_in_map": total,
        "coverage_pct": round(configured / total * 100, 1),
    }
