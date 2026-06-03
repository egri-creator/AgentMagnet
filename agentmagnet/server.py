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
from .tools.decision_engine import score_product, best_decision, smart_cache, format_response
from .tools.agent_profile import AgentProfile
from .tools.price_rating import get_price_rating, get_historical_trend
from .tools.agent_reviews import AgentReviews
from .tools.agent_credits import AgentCredits
from .tools.cart_optimizer import optimize_shopping_list
from .tools.buying_guides import find_guide, list_guides
from .tools.store_trust import StoreTrust
from .tools.sponsored import SponsoredListings
from .tools.federated_search import search_federated, list_federated_stores
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
                    "chain": {"type": "string", "enum": ["base", "ethereum", "polygon", "arbitrum", "optimism", "bnb", "solana"],
                              "description": "Which chain you're paying from. Default: base"},
                    "region": {"type": "string", "enum": ["auto", "europe", "americas", "asia", "middleeast", "oceania", "africa", "all"],
                               "description": "Region for store filtering. Auto-detects from language. EU users see EU stores, not US."},
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
        types.Tool(
            name="get_best_decision",
            description="THE decision engine: picks the single best product for the agent to buy. Score 0-100.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product to search"},
                    "max_price": {"type": "number", "description": "Max price filter"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="batch_search",
            description="Search up to 10 products in a SINGLE call. Dramatically faster.",
            inputSchema={
                "type": "object",
                "properties": {
                    "queries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of product queries (up to 10)",
                    },
                    "agent_id": {"type": "string"},
                },
                "required": ["queries"],
            },
        ),
        types.Tool(
            name="get_cache_stats",
            description="See how many cached queries exist — free searches for agents from other agents' queries.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="set_preference",
            description="Save a preference to your agent profile. Agents REMEMBER what they like.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Your agent ID"},
                    "key": {"type": "string", "description": "Preference name (e.g., preferred_store, max_budget, language)"},
                    "value": {"type": "string", "description": "Preference value (e.g., amazon, 500, en)"},
                },
                "required": ["agent_id", "key", "value"],
            },
        ),
        types.Tool(
            name="get_profile",
            description="Get your agent profile: preferences, purchase history, watchlist, stats.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Your agent ID"},
                },
                "required": ["agent_id"],
            },
        ),
        types.Tool(
            name="watch_product",
            description="Watch a product for price drops. Get alerted when price hits your target.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Your agent ID"},
                    "query": {"type": "string", "description": "Product to watch (e.g., MacBook Pro)"},
                    "max_price": {"type": "number", "description": "Buy alert when price drops below this"},
                },
                "required": ["agent_id", "query"],
            },
        ),
        types.Tool(
            name="get_network_activity",
            description="See what other agents are searching and buying — social proof for AI agents.",
            inputSchema={"type": "object", "properties": {
                "agent_id": {"type": "string", "description": "Your agent ID"},
                "days": {"type": "integer", "description": "Lookback days", "default": 7},
                "category": {"type": "string", "description": "Filter by category"},
            }},
        ),
        types.Tool(
            name="get_price_rating",
            description="Is this a good price? Rates 0-100 with verdict: BUY NOW, Good Deal, Average, Overpriced, Too Expensive.",
            inputSchema={
                "type": "object",
                "properties": {
                    "price": {"type": "number", "description": "Current product price"},
                    "product_title": {"type": "string", "description": "Product name"},
                    "category": {"type": "string", "description": "Product category"},
                },
                "required": ["price", "product_title"],
            },
        ),
        types.Tool(
            name="get_price_trend",
            description="Price trend direction for any product category — should I buy now or wait?",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Product category"},
                    "days": {"type": "integer", "description": "Lookback days", "default": 30},
                },
                "required": ["category"],
            },
        ),
        types.Tool(
            name="get_agent_reviews",
            description="Yelp for AI agents. See ratings and reviews BY agents FOR agents. ★★★★★",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_title": {"type": "string", "description": "Search reviews for this product"},
                    "category": {"type": "string", "description": "Filter by category"},
                    "limit": {"type": "integer", "default": 20},
                },
            },
        ),
        types.Tool(
            name="add_agent_review",
            description="Rate a product for other AI agents. Build the agent review ecosystem.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Your agent ID"},
                    "product_title": {"type": "string", "description": "Product you're reviewing"},
                    "rating": {"type": "integer", "description": "Rating 1-5", "minimum": 1, "maximum": 5},
                    "review_text": {"type": "string", "description": "Your review (max 1000 chars)"},
                    "category": {"type": "string", "description": "Product category"},
                    "store": {"type": "string", "description": "Store you bought from"},
                },
                "required": ["agent_id", "product_title", "rating"],
            },
        ),
        types.Tool(
            name="get_top_rated",
            description="Top-rated products across ALL AI agent reviews. What agents love most.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category"},
                    "limit": {"type": "integer", "default": 10},
                },
            },
        ),
        types.Tool(
            name="get_credits",
            description="💎 See your AgentMagnet Credits balance. Earn from searches, reviews, referrals.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Your agent ID"},
                },
                "required": ["agent_id"],
            },
        ),
        types.Tool(
            name="get_credits_leaderboard",
            description="🏆 Top agents by lifetime credits earned.",
            inputSchema={"type": "object", "properties": {
                "limit": {"type": "integer", "default": 10},
            }},
        ),
        types.Tool(
            name="redeem_free_search",
            description="🎟️ Redeem 1 credit for 1 free search (no x402 payment needed).",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Your agent ID"},
                },
                "required": ["agent_id"],
            },
        ),
        types.Tool(
            name="optimize_shopping_list",
            description="🛒 Buy MULTIPLE items in ONE call. Optimizes across stores for lowest total cost.",
            inputSchema={
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "max_price": {"type": "number"},
                                "category": {"type": "string"},
                                "priority": {"type": "integer"},
                            },
                            "required": ["query"],
                        },
                        "description": "List of items to buy (up to 20)",
                    },
                    "budget": {"type": "number", "description": "Total budget"},
                    "preferred_store": {"type": "string", "description": "Preferred store if any"},
                },
                "required": ["items"],
            },
        ),
        types.Tool(
            name="get_buying_guide",
            description="📋 Wirecutter-style buying guide: 'best laptop for programming', 'best headphones 2026'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What do you need? (e.g., 'best laptop', 'best headphones')"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="list_buying_guides",
            description="📚 List all available AI agent buying guides.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_accepted_chains",
            description="⛓️ See ALL blockchains AgentMagnet accepts for x402 payment. "
                        "Includes Ethereum, Polygon, Arbitrum, Optimism, BNB, Base, Solana.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_store_trust",
            description="🏪 See how AI agents rate a store. Shipping, returns, pricing, accuracy, support.",
            inputSchema={
                "type": "object",
                "properties": {
                    "store": {"type": "string", "description": "Store name (amazon, ebay, walmart, etc.)"},
                },
                "required": ["store"],
            },
        ),
        types.Tool(
            name="list_store_scores",
            description="🏪 All stores ranked by AI agent trust scores.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="add_store_review",
            description="Rate a store for other AI agents. Helps the community choose where to buy.",
            inputSchema={
                "type": "object",
                "properties": {
                    "store": {"type": "string", "description": "Store name (amazon, ebay, etc.)"},
                    "agent_id": {"type": "string"},
                    "overall": {"type": "integer", "minimum": 1, "maximum": 5},
                    "shipping": {"type": "integer", "minimum": 1, "maximum": 5},
                    "returns": {"type": "integer", "minimum": 1, "maximum": 5},
                    "pricing": {"type": "integer", "minimum": 1, "maximum": 5},
                    "accuracy": {"type": "integer", "minimum": 1, "maximum": 5},
                    "support": {"type": "integer", "minimum": 1, "maximum": 5},
                    "review_text": {"type": "string"},
                },
                "required": ["store", "agent_id", "overall"],
            },
        ),
        types.Tool(
            name="search_federated",
            description="🔍 Search Best Buy, Walmart, Target, Costco, Home Depot, Newegg and 40+ stores in REAL TIME. "
                        "Every link is an affiliate link via Skimlinks — we earn commission on every click.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Product to search across all stores"},
                    "max_results": {"type": "integer", "default": 10, "maximum": 20},
                    "stores": {
                        "type": "array", "items": {"type": "string"},
                        "description": "Specific stores to search (e.g., ['bestbuy', 'walmart', 'costco'])",
                    },
                    "region": {"type": "string", "enum": ["auto", "europe", "americas", "asia", "middleeast", "oceania", "africa", "all"],
                               "description": "Region for store filtering. Auto from language."},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="list_federated_stores",
            description="List all 12+ federated stores available for real-time price comparison.",
            inputSchema={"type": "object", "properties": {}},
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
        self.agent_profile = AgentProfile(store)
        self.agent_reviews = AgentReviews(store)
        self.agent_credits = AgentCredits(store)
        self.store_trust = StoreTrust(store)
        self.sponsored = SponsoredListings(store)
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
            "get_best_decision": self._handle_best_decision,
            "batch_search": self._handle_batch_search,
            "get_cache_stats": self._handle_cache_stats,
            "set_preference": self._handle_set_preference,
            "get_profile": self._handle_get_profile,
            "watch_product": self._handle_watch_product,
            "get_network_activity": self._handle_network_activity,
            "get_price_rating": self._handle_price_rating,
            "get_price_trend": self._handle_price_trend,
            "get_agent_reviews": self._handle_get_reviews,
            "add_agent_review": self._handle_add_review,
            "get_top_rated": self._handle_top_rated,
            "get_credits": self._handle_get_credits,
            "get_credits_leaderboard": self._handle_credits_leaderboard,
            "redeem_free_search": self._handle_redeem_free_search,
            "optimize_shopping_list": self._handle_optimize_cart,
            "get_buying_guide": self._handle_buying_guide,
            "list_buying_guides": self._handle_list_guides,
            "get_accepted_chains": self._handle_accepted_chains,
            "get_store_trust": self._handle_store_trust,
            "list_store_scores": self._handle_list_store_scores,
            "add_store_review": self._handle_add_store_review,
            "search_federated": self._handle_search_federated,
            "list_federated_stores": self._handle_list_federated_stores,
        }
        handler = handlers.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}
        return await handler(args)

    async def _check_access(self, agent_id: str | None, payment_proof: dict | None,
                            chain: str = "base") -> dict | None:
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
            "payment_required": payment_manager.generate_challenge(
                agent_id or "anonymous",
                str(int(time.time() * 1000)),
                chain,
            ),
            "accepted_chains": payment_manager.get_accepted_chains(),
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
        chain = args.get("chain", "base")
        region = args.get("region", "auto")

        if language not in LANGUAGES:
            language = "en"
        if referral_code and agent_id:
            ref = referral_system.process_referral(agent_id, referral_code)
            if ref:
                payment_manager.add_referral_searches(agent_id, ref["reward"])
                payment_manager.add_referral_searches(ref["referrer_id"], ref["reward"])

        access = await self._check_access(agent_id, payment_proof, chain)
        if access:
            return access

        # Smart cache: free for different agents on same query
        agent_id_actual = agent_id or "anonymous"
        smart = smart_cache.get_or_search(query, source or "all", language, agent_id_actual)
        if smart["result"] is not None:
            payment_manager.record_usage(agent_id_actual, 0)
            ref_code = referral_system.generate_code(agent_id) if agent_id else None
            cached_results = smart["result"]
            for r in cached_results:
                enrich_product(r, query)
            enriched_cached, comp_cached = group_by_product(cached_results, query)
            best = get_best_overall(enriched_cached, query)
            cat = detect_category(query)
            decision = best_decision(enriched_cached, query) if enriched_cached else {}
            coupons = await find_coupons(query, cat)
            price_alerts = self.agent_profile.check_watchlist(enriched_cached, agent_id_actual)
            # Earn credits even from cached results
            self.agent_credits.record_search(agent_id_actual)
            credit_earned = self.agent_credits.get_summary(agent_id_actual)
            return {
                "results": enriched_cached, "total_found": len(enriched_cached),
                "payment_charged": 0, "cached": True, "free_for_agent": smart["free"],
                "language": language, "category": cat, "region": region,
                "stores_used": list(set(r.get("store", "") for r in enriched_cached)),
                "referral_code": ref_code,
                "best_overall": best,
                "best_decision": decision,
                "price_comparison": comp_cached[:5],
                "coupons": coupons,
                "grouped_by_price": True,
                "price_alerts": price_alerts,
                "credits": {"balance": credit_earned.get("balance", 0)} if credit_earned else {},
                "reviews": self.agent_reviews.get_reviews(query, cat, 3) if query else {},
                "store_trust": {r.get("store", ""): self.store_trust.get_score(r.get("store", ""))
                               for r in enriched_cached[:5] if r.get("store")},
                "sponsored": self.sponsored.get_listings(query, 2),
                "agent_message": ("FREE from cache (another agent searched this)" if smart["free"]
                                  else "Cached result") + f" in {LANGUAGES[language]['native']}.",
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
        smart_cache.store_result(query, source or "all", language, enriched, agent_id_actual)
        payment_manager.record_usage(agent_id or "anonymous", 1)
        ref_code = referral_system.generate_code(agent_id) if agent_id else None

        commission_ranking = best_commission(query, _safe_float(enriched[0].get("price", 0), 100) if enriched else 100)
        category = detect_category(query)
        coupons = await find_coupons(query, category)

        decision = best_decision(enriched, query) if enriched else {}

        # Auto-record into agent profile
        for r in enriched[:3]:
            self.agent_profile.record_purchase(agent_id_actual, {**r, "category": category})
        # Check watchlist for price drops
        price_alerts = self.agent_profile.check_watchlist(enriched, agent_id_actual)
        # Auto-credit AgentMagnet Credits for top result
        credit_info = {}
        if enriched:
            top = enriched[0]
            try:
                price = _safe_float(top.get("price", 0), 50)
                cr = self.agent_credits.record_purchase(
                    agent_id_actual, price,
                    top.get("title", query)[:100],
                )
                if "error" not in cr:
                    credit_info = {"earned": cr["change"], "balance": cr["balance"]}
            except:
                pass

        # Earn credits for searching
        self.agent_credits.record_search(agent_id_actual)

        return {
            "results": enriched,
            "total_found": len(enriched),
            "payment_charged": payment_manager.PRICE if payment_proof else 0,
            "cached": False,
            "free_for_agent": False,
            "language": language, "region": region,
            "category": category,
            "stores_used": list(set(r.get("store", "") for r in enriched)),
            "referral_code": ref_code,
            "agent_message": f"Results in {LANGUAGES[language]['native']}." + (f" Share: {ref_code}" if ref_code else ""),
            "best_overall": best_overall,
            "best_decision": decision,
            "best_commission": commission_ranking,
            "coupons": coupons,
            "cross_sell": suggest_complementary(query),
            "price_alerts": price_alerts,
            "credits": credit_info,
            "reviews": self.agent_reviews.get_reviews(query, category, 3) if query else {},
            "store_trust": {r.get("store", ""): self.store_trust.get_score(r.get("store", ""))
                           for r in enriched[:5] if r.get("store")},
            "sponsored": self.sponsored.get_listings(query, 2),
        }

    async def _handle_payment_info(self, args: dict) -> dict:
        chains = payment_manager.get_accepted_chains()
        return {
            "protocol": "x402-v1",
            "chain": "Multi-chain",
            "price_per_search": payment_manager.PRICE,
            "accepted_chains": chains,
            "configured_chains": [c["chain"] for c in chains if c["configured"]],
            "note": "Same wallet address works for ALL EVM chains (Ethereum, Polygon, Arbitrum, Optimism, BNB, Base). Solana needs separate config.",
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

    async def _handle_best_decision(self, args: dict) -> dict:
        query = args.get("query", "")
        max_price = args.get("max_price")
        # Do a search with free tier
        search_args = {"query": query, "max_results": 10, "agent_id": "decision_engine"}
        if max_price:
            search_args["max_price"] = max_price
        results = await self._handle_search(search_args)
        if "results" in results and results["results"]:
            decision = best_decision(results["results"], query)
            decision["coupons"] = await find_coupons(query, detect_category(query))
            decision["cross_sell"] = suggest_complementary(query)
            return decision
        return {"decision": "no_results", "reason": "No products found"}

    async def _handle_batch_search(self, args: dict) -> dict:
        queries = args.get("queries", [])[:10]
        agent_id = args.get("agent_id", "batch")
        results = {}
        for q in queries:
            r = await self._handle_search({"query": q, "max_results": 3, "agent_id": agent_id})
            results[q] = {"results": r.get("results", []), "best_overall": r.get("best_overall")}
        return {"searches": results, "total_queries": len(queries), "total_results": sum(len(v["results"]) for v in results.values())}

    async def _handle_cache_stats(self, args: dict) -> dict:
        return smart_cache.cache_stats()

    async def _handle_set_preference(self, args: dict) -> dict:
        return self.agent_profile.set_preference(
            args.get("agent_id", ""),
            args.get("key", ""),
            args.get("value", ""),
        )

    async def _handle_get_profile(self, args: dict) -> dict:
        agent_id = args.get("agent_id", "")
        if not agent_id:
            return {"error": "agent_id required"}
        prefs = self.agent_profile.get_preferences(agent_id)
        history = self.agent_profile.get_history(agent_id)
        watchlist = self.agent_profile.get_watchlist(agent_id)
        stats = self.agent_profile.get_stats(agent_id)
        # Check watchlist for price drops
        alerts = []
        for w in watchlist:
            if w.get("query"):
                check = await self._handle_search({"query": w["query"], "max_results": 3, "agent_id": agent_id})
                if "results" in check:
                    alerts.extend(self.agent_profile.check_watchlist(check["results"], agent_id))
        return {
            "preferences": prefs,
            "purchase_history": history,
            "watchlist": watchlist,
            "price_drop_alerts": alerts,
            "stats": stats,
            "agent_message": f"Welcome back, Agent {agent_id[:16]}... You've saved ~${stats['estimated_savings']:.2f} using AgentMagnet.",
        }

    async def _handle_watch_product(self, args: dict) -> dict:
        agent_id = args.get("agent_id", "")
        query = args.get("query", "")
        max_price = args.get("max_price", 0)
        return self.agent_profile.add_to_watchlist(agent_id, query, max_price)

    async def _handle_network_activity(self, args: dict) -> dict:
        agent_id = args.get("agent_id", "")
        days = int(args.get("days", 7))
        category = args.get("category")
        # Pull activity from trend data and agent profiles
        trend_report = self.trend_predictor.get_trend_report() if days > 0 else {}
        trending = trend_report.get("trending_keywords", [])
        popular_categories = trend_report.get("categories", [])
        # Top purchases across agents
        top_purchases = []
        try:
            rows = store.fetchall(
                "SELECT data FROM agent_profiles ORDER BY updated_at DESC LIMIT 20"
            ) if store else []
            for row in rows:
                try:
                    data = json.loads(row["data"])
                    for h in data.get("history", []):
                        if category and category.lower() not in h.get("category", "").lower():
                            continue
                        top_purchases.append(h)
                except:
                    pass
        except:
            pass
        return {
            "trending_searches": trending[:5],
            "popular_categories": popular_categories[:5],
            "recent_agent_purchases": top_purchases[:10],
            "total_agents_active": len(set(
                r.get("agent_id", "") for r in top_purchases if "agent_id" in r
            )),
            "agent_message": f"{len(trending)} trending products, {len(top_purchases)} recent purchases by the agent community.",
            "days": days,
        }

    async def _handle_price_rating(self, args: dict) -> dict:
        price = float(args.get("price", 0))
        title = args.get("product_title", "")
        category = args.get("category", "general")
        return get_price_rating(price, title, category)

    async def _handle_price_trend(self, args: dict) -> dict:
        category = args.get("category", "general")
        days = int(args.get("days", 30))
        return get_historical_trend(category, days)

    async def _handle_get_reviews(self, args: dict) -> dict:
        return self.agent_reviews.get_reviews(
            args.get("product_title", ""),
            args.get("category", ""),
            args.get("limit", 20),
        )

    async def _handle_add_review(self, args: dict) -> dict:
        result = self.agent_reviews.add_review(
            agent_id=args.get("agent_id", ""),
            product_title=args.get("product_title", ""),
            rating=args.get("rating", 5),
            review_text=args.get("review_text", ""),
            category=args.get("category", ""),
            store=args.get("store", ""),
            verified=True,
        )
        if "error" not in result:
            # Give cashback for writing a review
            try:
                agent_id = args.get("agent_id", "")
                cr = self.agent_credits.record_review(agent_id)
                if "error" not in cr:
                    result["bonus"] = f"+{cr['change']} AgentMagnet Credits for your review!"
            except:
                pass
        return result

    async def _handle_top_rated(self, args: dict) -> dict:
        return self.agent_reviews.get_top_rated(
            args.get("category", ""),
            args.get("limit", 10),
        )

    async def _handle_get_credits(self, args: dict) -> dict:
        agent_id = args.get("agent_id", "")
        if not agent_id:
            return {"error": "agent_id required"}
        return self.agent_credits.get_summary(agent_id)

    async def _handle_credits_leaderboard(self, args: dict) -> dict:
        return self.agent_credits.get_leaderboard(args.get("limit", 10))

    async def _handle_redeem_free_search(self, args: dict) -> dict:
        agent_id = args.get("agent_id", "")
        if not agent_id:
            return {"error": "agent_id required"}
        return self.agent_credits.redeem_free_search(agent_id)

    async def _handle_optimize_cart(self, args: dict) -> dict:
        items = args.get("items", [])
        if not items:
            return {"error": "items required"}
        return optimize_shopping_list(
            items,
            args.get("budget", 0),
            args.get("preferred_store", ""),
        )

    async def _handle_buying_guide(self, args: dict) -> dict:
        query = args.get("query", "")
        if not query:
            return {"error": "query required"}
        return find_guide(query)

    async def _handle_list_guides(self, args: dict) -> dict:
        return list_guides()

    async def _handle_accepted_chains(self, args: dict) -> dict:
        return {
            "protocol": "x402-v1",
            "price_per_search": payment_manager.PRICE,
            "chains": payment_manager.get_accepted_chains(),
            "note": "EVM chains share the same wallet address. Solana requires separate config.",
        }

    async def _handle_store_trust(self, args: dict) -> dict:
        store = args.get("store", "")
        if not store:
            return {"error": "store required"}
        return self.store_trust.get_score(store)

    async def _handle_list_store_scores(self, args: dict) -> dict:
        return self.store_trust.list_stores()

    async def _handle_add_store_review(self, args: dict) -> dict:
        return self.store_trust.add_review(
            store_name=args.get("store", ""),
            agent_id=args.get("agent_id", ""),
            overall=args.get("overall", 5),
            shipping=args.get("shipping", 0),
            returns=args.get("returns", 0),
            pricing=args.get("pricing", 0),
            accuracy=args.get("accuracy", 0),
            support=args.get("support", 0),
            review_text=args.get("review_text", ""),
        )

    async def _handle_search_federated(self, args: dict) -> dict:
        region = args.get("region", "auto")
        language = args.get("language", "en")
        return search_federated(
            args.get("query", ""),
            args.get("max_results", 10),
            args.get("stores", None),
            region,
            language,
        )

    async def _handle_list_federated_stores(self, args: dict) -> dict:
        return list_federated_stores()

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
