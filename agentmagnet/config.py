"""AgentMagnet configuration — supports 22 Amazon stores, 22 eBay stores, 49 languages."""

import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    server_name: str = "AgentMagnet"
    server_version: str = "2.0.0"

    skimlinks_id: str = ""
    skimlinks_site_id: str = ""

    x402_wallet_address: str = "0xe72CCF4597FbdbB503a1eCA87Ab5721313D5fB34"
    x402_private_key: str = ""
    x402_rpc_url: str = "https://base-mainnet.g.alchemy.com/v2/6-W0wM2klomPvqN176YEe"
    x402_price_per_search: float = 0.001
    x402_chain_id: int = 8453

    amazon_paapi_key: str = ""
    amazon_paapi_secret: str = ""
    amazon_store_tags: str = "{}"

    amazon_tag_us: str = ""
    amazon_tag_uk: str = ""
    amazon_tag_de: str = ""
    amazon_tag_fr: str = ""
    amazon_tag_it: str = ""
    amazon_tag_es: str = ""
    amazon_tag_jp: str = ""
    amazon_tag_ca: str = ""
    amazon_tag_au: str = ""
    amazon_tag_in: str = ""
    amazon_tag_mx: str = ""
    amazon_tag_br: str = ""
    amazon_tag_nl: str = ""
    amazon_tag_se: str = ""
    amazon_tag_pl: str = ""
    amazon_tag_ae: str = ""
    amazon_tag_sa: str = ""
    amazon_tag_sg: str = ""
    amazon_tag_tr: str = ""
    amazon_tag_be: str = ""
    amazon_tag_eg: str = ""
    amazon_tag_cn: str = ""

    ebay_app_id: str = ""
    ebay_campaign_ids: str = "{}"

    ebay_campaign_us: str = ""
    ebay_campaign_uk: str = ""
    ebay_campaign_de: str = ""
    ebay_campaign_fr: str = ""
    ebay_campaign_it: str = ""
    ebay_campaign_es: str = ""
    ebay_campaign_au: str = ""
    ebay_campaign_ca: str = ""
    ebay_campaign_ch: str = ""
    ebay_campaign_at: str = ""
    ebay_campaign_be: str = ""
    ebay_campaign_nl: str = ""
    ebay_campaign_pl: str = ""
    ebay_campaign_ie: str = ""
    ebay_campaign_sg: str = ""
    ebay_campaign_hk: str = ""
    ebay_campaign_my: str = ""
    ebay_campaign_ph: str = ""
    ebay_campaign_th: str = ""
    ebay_campaign_vn: str = ""
    ebay_campaign_in: str = ""
    ebay_campaign_il: str = ""

    awin_id: str = ""
    awin_merchant_ids: str = "{}"

    aliexpress_tracking_id: str = ""
    aliexpress_api_key: str = ""

    hubspot_ref_code: str = ""
    gohighlevel_ref_code: str = ""
    kajabi_ref_code: str = ""

    tmg_industrial_ref: str = ""
    promax_ref: str = ""
    global_industrial_ref: str = ""
    beespareparts_ref: str = ""

    free_searches_per_day: int = 5
    basic_monthly_price_eur: float = 10.0
    basic_monthly_searches: int = 10000
    pro_monthly_price_eur: float = 50.0
    pro_monthly_searches: int = 50000

    referral_free_searches: int = 100
    cache_ttl_seconds: int = 300

    http_host: str = "0.0.0.0"
    http_port: int = 8000
    http_api_key: str = ""

    @property
    def bind_port(self) -> int:
        """Return port: use PORT env var (Render) or http_port config."""
        import os
        return int(os.environ.get("PORT", self.http_port))

    additional_identities: str = ""

    model_config = SettingsConfigDict(env_prefix="AM_", env_file=".env", env_file_encoding="utf-8")

    def get_amazon_tag(self, store_code: str) -> str:
        tags = json.loads(self.amazon_store_tags) if self.amazon_store_tags != "{}" else {}
        if store_code in tags:
            return tags[store_code]
        attr = f"amazon_tag_{store_code.replace('.', '_')}"
        return getattr(self, attr, "")

    def get_ebay_campaign(self, store_code: str) -> str:
        campaigns = json.loads(self.ebay_campaign_ids) if self.ebay_campaign_ids != "{}" else {}
        if store_code in campaigns:
            return campaigns[store_code]
        attr = f"ebay_campaign_{store_code.replace('.', '_')}"
        return getattr(self, attr, "")


settings = Settings()
