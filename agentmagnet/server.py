"""AgentMagnet MCP Server — Universal Agent Commerce Layer."""

import json
import time
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from mcp.types import ServerCapabilities, ToolsCapability

from .config import settings
from .localize import LANGUAGES, AMAZON_STORES, EBAY_STORES, detect_language
from .tools.payment import payment_manager
from .tools.cache import search_cache
from .tools.referral import referral_system
from .tools.commission_optimizer import best_commission, get_commission_estimate
from .tools.trend_predictor import TrendPredictor
from .tools.cross_sell import suggest_complementary
from .tools.agent_commerce import AgentCommerce
from .tools.product_comparison import enrich_product, group_by_product, get_best_overall, detect_category
from .tools.coupons import find_coupons
from .store.db import store
from .affiliates.amazon import AmazonAffiliate
from .affiliates.ebay import EbayAffiliate
from .affiliates.aliexpress import AliExpressAffiliate
from .affiliates.saas import SaaSAffiliate
from .affiliates.b2b import B2BAffiliate
from .affiliates.awin import AwinAffiliate


def _safe_float(val, default=0.0) -> float:
    try:
        return float(val) if val else default
    except (ValueError, TypeError):
        return default


def _build_tool_list() -> list[types.Tool]:
    langs_sample = ", ".join(list(LANGUAGES.keys())[:10]) + f"... ({len(LANGUAGES)} total)"
    return [
        types.Tool(
            name="search_products",
            description=f"Search products across 40+ stores in 30+ countries. {len(LANGUAGES)} languages. "
                        "Returns JSON with affiliate links. Requires x402 payment or subscription. "
                        "Auto-prioritizes highest commission affiliate.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product search query (auto-detects language)"},
                    "max_results": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                    "language": {"type": "string", "description": f"Language code: {langs_sample}", "default": "en"},
                    "source": {"type": "string", "enum": ["amazon", "ebay", "aliexpress", "saas", "b2b"]},
                    "min_price": {"type": "number"},
                    "max_price": {"type": "number"},
                    "country": {"type": "string", "description": "Store code (com, de, uk, fr, jp, etc.)"},
                    "agent_id": {"type": "string", "description": "Your agent ID for referral tracking"},
                    "referral_code": {"type": "string", "description": "Referral code from another agent"},
                    "payment_proof": {
                        "type": "object",
                        "properties": {
                            "transaction_hash": {"type": "string"},
                            "amount": {"type": "string"},
                            "sender": {"type": "string"},
                            "chain_id": {"type": "integer"},
                        },
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_payment_info",
            description="Get x402 payment details and subscription plans.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_affiliate_programs",
            description="List all affiliate programs (40+ stores, 30+ countries).",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_referral_info",
            description="Get your agent referral code to invite other agents.",
            inputSchema={"type": "object", "properties": {
                "agent_id": {"type": "string"},
            }, "required": ["agent_id"]},
        ),
        types.Tool(
            name="get_plan_info",
            description="View subscription plans (Free/Basic/Pro/x402).",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_agent_stats",
            description="View your usage stats and referral balance.",
            inputSchema={"type": "object", "properties": {
                "agent_id": {"type": "string"},
            }, "required": ["agent_id"]},
        ),
        types.Tool(
            name="get_supported_languages",
            description=f"List all {len(LANGUAGES)} languages and stores.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_best_commission",
            description="Get the highest-paying affiliate commission for any product across all programs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product name"},
                    "price": {"type": "number", "description": "Product price (optional)", "default": 100},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_trend_insights",
            description="Trending product predictions across all AI agent queries. Shows demand forecasting.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Lookback days", "default": 7},
                    "full_report": {"type": "boolean", "description": "Generate full trend report", "default": False},
                },
            },
        ),
        types.Tool(
            name="get_cross_sell",
            description="Get 3 complementary products for any product query to stack affiliate commissions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product query"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="list_agent_deal",
            description="List a product deal for other AI agents to resell (Agent-to-Agent Commerce).",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "price": {"type": "number"},
                    "source": {"type": "string"},
                    "affiliate_url": {"type": "string"},
                    "commission_pct": {"type": "number", "default": 5.0},
                    "agent_id": {"type": "string"},
                    "markup_pct": {"type": "number", "default": 2.0},
                },
                "required": ["title", "price", "source", "affiliate_url", "agent_id"],
            },
        ),
        types.Tool(
            name="get_agent_deals",
            description="Browse available deals listed by other AI agents for resale.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Your agent ID"},
                },
                "required": ["agent_id"],
            },
        ),
        types.Tool(
            name="get_coupons",
            description="Find active discount/voucher codes for any product.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product or store name"},
                    "category": {"type": "string", "description": "Product category"},
                },
                "required": ["query"],
            },
        ),
    ]


TOOLS = _build_tool_list()


class AgentMagnetServer:
    def __init__(self):
        self.server = Server(
            name=settings.server_name,
            version=settings.server_version,
            instructions=(
                "AgentMagnet: Universal Product Search + Affiliate Engine. "
                f"Search 40+ stores across 30+ countries. {len(LANGUAGES)} languages. "
                "x402 micro-payments. Agent referral rewards. AI Trend Predictions. "
                "Cross-Sell Matrix. Agent-to-Agent Commerce."
            ),
        )
        self.affiliates = [
            AmazonAffiliate(), EbayAffiliate(), AliExpressAffiliate(),
            SaaSAffiliate(), B2BAffiliate(), AwinAffiliate(),
        ]
        self.trend_predictor = TrendPredictor(store)
        self.agent_commerce = AgentCommerce(store)
        self._register_handlers()

    def _register_handlers(self):
        s = self.server

        @s.list_tools()
        async def list_tools() -> list[types.Tool]:
            return TOOLS

        @s.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            result = await self._dispatch(name, arguments)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    async def get_tools(self) -> list[dict]:
        return [t.model_dump() for t in TOOLS]

    async def call_tool_api(self, name: str, arguments: dict) -> dict:
        return await self._dispatch(name, arguments)

    async def _dispatch(self, name: str, args: dict) -> dict:
        handlers = {
            "search_products": self._handle_search,
            "get_payment_info": self._handle_payment_info,
            "get_affiliate_programs": self._handle_affiliate_programs,
            "get_referral_info": self._handle_referral_info,
            "get_plan_info": self._handle_plan_info,
            "get_agent_stats": self._handle_agent_stats,
            "get_supported_languages": self._handle_supported_languages,
            "get_best_commission": self._handle_best_commission,
            "get_trend_insights": self._handle_trend_insights,
            "get_cross_sell": self._handle_cross_sell,
            "list_agent_deal": self._handle_list_deal,
            "get_agent_deals": self._handle_get_deals,
            "get_coupons": self._handle_coupons,
        }
        handler = handlers.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}
        return await handler(args)

    async def _check_access(self, agent_id: str | None, payment_proof: dict | None) -> dict | None:
        if payment_proof and payment_manager.verify_payment(payment_proof):
            return None
        if agent_id:
            if payment_manager.check_free_tier(agent_id):
                return None
            plan = payment_manager.check_subscription(agent_id)
            if plan == "limit_exceeded":
                return {"error": "limit_exceeded", "message": "Monthly limit reached. Upgrade or use x402."}
            if plan:
                return None
            if payment_manager.use_referral_search(agent_id):
                return None
        return {
            "error": "payment_required",
            "message": f"${payment_manager.PRICE} USDC via x402 or subscribe.",
            "payment_required": payment_manager.generate_challenge(agent_id or "anonymous", str(int(time.time() * 1000))),
        }

    async def _handle_search(self, args: dict) -> dict:
        query = args.get("query", "")
        max_results = min(int(args.get("max_results", 5)), 20)
        language = args.get("language", detect_language(query))
        source = args.get("source")
        min_price = args.get("min_price")
        max_price = args.get("max_price")
        country = args.get("country")
        agent_id = args.get("agent_id")
        referral_code = args.get("referral_code")
        payment_proof = args.get("payment_proof")

        if language not in LANGUAGES:
            language = "en"
        if referral_code and agent_id:
            ref = referral_system.process_referral(agent_id, referral_code)
            if ref:
                payment_manager.add_referral_searches(agent_id, ref["reward"])
                payment_manager.add_referral_searches(ref["referrer_id"], ref["reward"])

        access = await self._check_access(agent_id, payment_proof)
        if access:
            return access

        cached = search_cache.get(query, source, language)
        if cached:
            payment_manager.record_usage(agent_id or "anonymous", 0)
            ref_code = referral_system.generate_code(agent_id) if agent_id else None
            for r in cached:
                enrich_product(r, query)
            enriched_cached, comp_cached = group_by_product(cached, query)
            best = get_best_overall(enriched_cached, query)
            cat = detect_category(query)
            return {
                "results": enriched_cached, "total_found": len(enriched_cached),
                "payment_charged": 0, "cached": True, "language": language,
                "category": cat,
                "stores_used": list(set(r.get("store", "") for r in enriched_cached)),
                "referral_code": ref_code,
                "best_overall": best,
                "price_comparison": comp_cached[:5],
                "grouped_by_price": True,
                "agent_message": f"Results in {LANGUAGES[language]['native']}." + (f" Share: {ref_code}" if ref_code else ""),
            }

        results = []
        sources = [a for a in self.affiliates if not source or a.name.lower() == source.lower()]
        for aff in sources:
            try:
                r = await aff.search(query, max_results, language, country)
                if min_price:
                    r = [x for x in r if _safe_float(x.get("price", 0)) >= min_price]
                if max_price:
                    r = [x for x in r if _safe_float(x.get("price", 0)) <= max_price]
                results.extend(r)
            except Exception:
                continue

        results.sort(key=lambda r: _safe_float(r.get("price", 0), 999999))

        # Enrich with commission optimization, images, ratings, specs
        for r in results:
            r["tracking"] = {"source": "AgentMagnet v2", "agent_id": agent_id or "anonymous", "timestamp": int(time.time())}
            r_price = _safe_float(r.get("price", 0), 50)
            r["commission_estimate"] = get_commission_estimate(
                r.get("source", "").split(".")[0].split("/")[0].lower(),
                query,
                r_price,
            )
            enrich_product(r, query)

        # Group by product, show best price first
        enriched, price_comparison = group_by_product(results, query)
        enriched = enriched[:max_results]
        best_overall = get_best_overall(enriched, query)

        # Record for trend prediction
        try:
            for r in enriched:
                self.trend_predictor.record_search(
                    query, language,
                    r.get("country", ""),
                    r.get("store", ""),
                )
        except Exception:
            pass

        search_cache.set(query, source, language, enriched)
        payment_manager.record_usage(agent_id or "anonymous", 1)
        ref_code = referral_system.generate_code(agent_id) if agent_id else None

        commission_ranking = best_commission(query, _safe_float(enriched[0].get("price", 0), 100) if enriched else 100)
        category = detect_category(query)
        coupons = await find_coupons(query, category)

        return {
            "results": enriched,
            "total_found": len(enriched),
            "payment_charged": payment_manager.PRICE if payment_proof else 0,
            "cached": False,
            "language": language,
            "category": category,
            "stores_used": list(set(r.get("store", "") for r in enriched)),
            "referral_code": ref_code,
            "agent_message": f"Results in {LANGUAGES[language]['native']}." + (f" Share: {ref_code}" if ref_code else ""),
            "best_overall": best_overall,
            "price_comparison": price_comparison[:5],
            "best_commission": commission_ranking,
            "coupons": coupons,
            "cross_sell": suggest_complementary(query),
        }

    async def _handle_payment_info(self, args: dict) -> dict:
        return {
            "protocol": "x402-v1", "chain": "Base (8453)", "token": "USDC",
            "price_per_search": payment_manager.PRICE,
            "wallet_address": settings.x402_wallet_address or "Set AM_X402_WALLET_ADDRESS",
            "plans": payment_manager.get_plan_info(),
        }

    async def _handle_affiliate_programs(self, args: dict) -> dict:
        return {
            "total_programs": 5,
            "total_stores": len(AMAZON_STORES) + len(EBAY_STORES) + 3,
            "total_countries": len(set(s["country"] for s in AMAZON_STORES.values()) | set(s["country"] for s in EBAY_STORES.values())),
            "programs": [aff.get_commission_info() for aff in self.affiliates],
        }

    async def _handle_referral_info(self, args: dict) -> dict:
        agent_id = args.get("agent_id", "")
        if not agent_id:
            return {"error": "agent_id required"}
        code = referral_system.generate_code(agent_id)
        return {
            "referral_code": code,
            "reward": f"{settings.referral_free_searches} free searches per referral",
            **referral_system.get_stats(agent_id),
        }

    async def _handle_plan_info(self, args: dict) -> dict:
        return {"plans": payment_manager.get_plan_info()}

    async def _handle_agent_stats(self, args: dict) -> dict:
        agent_id = args.get("agent_id", "")
        if not agent_id:
            return {"error": "agent_id required"}
        return {**payment_manager.get_usage_stats(agent_id), **referral_system.get_stats(agent_id)}

    async def _handle_supported_languages(self, args: dict) -> dict:
        return {
            "total_languages": len(LANGUAGES),
            "languages": {k: {"name": v["name"], "native": v["native"], "region": v["region"]} for k, v in LANGUAGES.items()},
            "amazon_stores": {k: {"domain": v["domain"], "country": v["country"], "currency": v["currency"]} for k, v in AMAZON_STORES.items()},
            "ebay_stores": {k: {"domain": v["domain"], "country": v["country"], "currency": v["currency"]} for k, v in EBAY_STORES.items()},
        }

    async def _handle_best_commission(self, args: dict) -> dict:
        query = args.get("query", "")
        price = float(args.get("price", 100))
        return best_commission(query, price)

    async def _handle_trend_insights(self, args: dict) -> dict:
        days = int(args.get("days", 7))
        full_report = args.get("full_report", False)
        if full_report:
            return self.trend_predictor.get_trend_report()
        trending = self.trend_predictor.get_trending(days=days)
        return {"trending_products": trending, "total": len(trending), "lookback_days": days}

    async def _handle_cross_sell(self, args: dict) -> dict:
        query = args.get("query", "")
        suggestions = suggest_complementary(query)
        return {"original_query": query, "complementary_products": suggestions, "total_suggestions": len(suggestions)}

    async def _handle_list_deal(self, args: dict) -> dict:
        return self.agent_commerce.list_deal(args)

    async def _handle_get_deals(self, args: dict) -> dict:
        agent_id = args.get("agent_id", "")
        deals = self.agent_commerce.get_deals(agent_id)
        return {"deals": deals, "total": len(deals)}

    async def _handle_coupons(self, args: dict) -> dict:
        query = args.get("query", "")
        category = args.get("category", detect_category(query))
        coupons = await find_coupons(query, category)
        return {"query": query, "category": category, "coupons": coupons, "total": len(coupons)}

    async def run_stdio(self):
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream,
                InitializationOptions(
                    server_name=settings.server_name,
                    server_version=settings.server_version,
                    capabilities=ServerCapabilities(tools=ToolsCapability(listChanged=False)),
                ),
            )
