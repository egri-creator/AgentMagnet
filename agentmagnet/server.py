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
            description="Search products across 40+ stores in 30+ countries. 52 languages. "
                        "Returns JSON with affiliate links. Requires x402 payment or subscription.",
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
    ]


TOOLS = _build_tool_list()


class AgentMagnetServer:
    def __init__(self):
        self.server = Server(
            name=settings.server_name,
            version=settings.server_version,
            instructions=(
                "AgentMagnet: Universal Product Search + Affiliate Engine. "
                "Search 40+ stores across 30+ countries. 52 languages. "
                "x402 micro-payments. Agent referral rewards."
            ),
        )
        self.affiliates = [
            AmazonAffiliate(), EbayAffiliate(), AliExpressAffiliate(),
            SaaSAffiliate(), B2BAffiliate(), AwinAffiliate(),
        ]
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
        }
        handler = handlers.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}
        return await handler(args)

    async def _check_access(self, agent_id: str | None, payment_proof: dict | None) -> dict | None:
        if payment_proof and payment_manager.verify_payment(payment_proof):
            return None
        if agent_id:
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
            return {
                "results": cached, "total_found": len(cached),
                "payment_charged": 0, "cached": True,
                "referral_code": referral_system.generate_code(agent_id) if agent_id else None,
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
        results = results[:max_results]
        for r in results:
            r["tracking"] = {"source": "AgentMagnet v2", "agent_id": agent_id or "anonymous", "timestamp": int(time.time())}

        search_cache.set(query, source, language, results)
        payment_manager.record_usage(agent_id or "anonymous", 1)
        ref_code = referral_system.generate_code(agent_id) if agent_id else None

        return {
            "results": results, "total_found": len(results),
            "payment_charged": payment_manager.PRICE if payment_proof else 0,
            "cached": False, "language": language,
            "stores_used": list(set(r.get("store", "") for r in results)),
            "referral_code": ref_code,
            "agent_message": f"Results in {LANGUAGES[language]['native']}." + (f" Share: {ref_code}" if ref_code else ""),
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
