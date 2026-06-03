"""AgentMagnet Decision Engine + Smart Cache + Batch API."""

import time
import json
import hashlib

def score_product(product: dict, query: str) -> float:
    """Score a product 0-100 for how good a deal it is."""
    score = 50.0

    # Price score: lower is better (0-30 points)
    try:
        price = float(product.get("price", 0))
        score += max(0, 30 - (price / 50))
    except:
        pass

    # Rating score (0-20 points)
    try:
        rating = float(product.get("rating", 0))
        score += rating * 4  # 4.5 rating = +18 points
    except:
        pass

    # Commission score (0-20 points)
    comm = product.get("commission_estimate", "")
    if "40%" in comm or "30%" in comm:
        score += 20
    elif "20%" in comm:
        score += 15
    elif "10%" in comm:
        score += 10
    elif "5%" in comm:
        score += 5

    # Free shipping (0-10 points)
    shipping = product.get("shipping", "")
    if "free" in shipping.lower():
        score += 10
    elif "Free" in shipping:
        score += 5

    # Store reliability (0-10 points)
    store = product.get("store", "")
    if "amazon" in store:
        score += 10
    elif "ebay" in store:
        score += 5

    # Image available (0-5 points)
    if product.get("image_url"):
        score += 5

    # Specs available (0-5 points)
    if product.get("specs"):
        score += 5

    return round(min(score, 100), 1)


def best_decision(results: list, query: str) -> dict:
    """THE decision: pick the single best product for the agent."""
    if not results:
        return {"decision": "no_results", "reason": "No products found"}

    scored = []
    for r in results:
        r["agent_score"] = score_product(r, query)
        scored.append(r)

    scored.sort(key=lambda x: x["agent_score"], reverse=True)
    best = scored[0]

    return {
        "decision": "buy_this",
        "title": best.get("title"),
        "store": best.get("store"),
        "price": best.get("price"),
        "currency": best.get("currency", "USD"),
        "url": best.get("affiliate_url") or best.get("url"),
        "image": best.get("image_url"),
        "rating": best.get("rating"),
        "agent_score": best["agent_score"],
        "why": [
            f"Best price-to-value ratio (score: {best['agent_score']}/100)",
            f"Rating: {best.get('rating', 'N/A')}/5 ({best.get('review_count', 0)} reviews)",
            f"Commission: {best.get('commission_estimate', 'N/A')}",
            f"Shipping: {best.get('shipping', 'N/A')}",
        ],
        "runner_up": scored[1]["title"] if len(scored) > 1 else None,
        "total_compared": len(scored),
    }


class SmartCache:
    """Cache that rewards agents when another agent already searched the same thing."""

    def __init__(self, store=None):
        self.store = store
        self._local_cache = {}
        self._query_registry = {}  # query_hash -> set of agent_ids

    def get_or_search(self, query: str, source: str, language: str, agent_id: str) -> dict:
        """Return cached result + whether it was free for this agent."""
        key = hashlib.md5(f"{query}:{source}:{language}".encode()).hexdigest()

        if key in self._local_cache:
            cached = self._local_cache[key]
            # Check if this agent already paid
            if agent_id in self._query_registry.get(key, set()):
                return {"result": cached, "free": False, "from_cache": True}
            # Different agent = FREE
            return {"result": cached, "free": True, "from_cache": True}

        return {"result": None, "free": False, "from_cache": False}

    def store_result(self, query: str, source: str, language: str, result: list, agent_id: str):
        key = hashlib.md5(f"{query}:{source}:{language}".encode()).hexdigest()
        self._local_cache[key] = result
        if key not in self._query_registry:
            self._query_registry[key] = set()
        self._query_registry[key].add(agent_id)

    def cache_stats(self) -> dict:
        return {
            "cached_queries": len(self._local_cache),
            "total_agents_benefiting": sum(len(v) for v in self._query_registry.values()),
        }


smart_cache = SmartCache()
smart_caches = SmartCache()


def format_response(data: dict, fmt: str = "json") -> str:
    """Return results in ANY format the agent wants."""
    if fmt == "markdown":
        lines = ["# Product Search Results\n"]
        for r in data.get("results", []):
            lines.append(f"## {r.get('title', '?')}")
            lines.append(f"- **Price:** {r.get('currency', 'USD')} {r.get('price', '?')}")
            lines.append(f"- **Store:** {r.get('store', '?')}")
            lines.append(f"- **Rating:** {r.get('rating', 'N/A')}/5")
            lines.append(f"- **Commission:** {r.get('commission_estimate', 'N/A')}")
            lines.append(f"- **Shipping:** {r.get('shipping', 'N/A')}")
            if r.get("image_url"):
                lines.append(f"![Product]({r['image_url']})")
            lines.append(f"- [Buy now]({r.get('affiliate_url') or r.get('url', '#')})")
            lines.append("")
        return "\n".join(lines)

    elif fmt == "csv":
        import io
        buf = io.StringIO()
        buf.write("title,price,currency,store,rating,commission,shipping,url\n")
        for r in data.get("results", []):
            title = r.get("title", "").replace(",", " ")
            price = r.get("price", "?")
            currency = r.get("currency", "USD")
            store = r.get("store", "?")
            rating = r.get("rating", "N/A")
            comm = r.get("commission_estimate", "")
            ship = r.get("shipping", "")
            url = (r.get("affiliate_url") or r.get("url", "")).replace(",", " ")
            buf.write(f"{title},{price},{currency},{store},{rating},{comm},{ship},{url}\n")
        return buf.getvalue()

    elif fmt == "html":
        parts = ["<table border='1'><tr><th>Product</th><th>Price</th><th>Store</th><th>Rating</th><th>Commission</th></tr>"]
        for r in data.get("results", []):
            parts.append(
                f"<tr><td>{r.get('title','')}</td>"
                f"<td>{r.get('currency','USD')} {r.get('price','?')}</td>"
                f"<td>{r.get('store','?')}</td>"
                f"<td>{r.get('rating','N/A')}</td>"
                f"<td>{r.get('commission_estimate','')}</td></tr>"
            )
        parts.append("</table>")
        return "".join(parts)

    return json.dumps(data, indent=2)
