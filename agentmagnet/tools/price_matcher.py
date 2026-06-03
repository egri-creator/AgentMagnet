"""
Price Matcher — encuentra el MEJOR precio total para un producto entre todas las tiendas.
Usa smart_checkout para calcular precio final (descuento tier + cupón + comisión).
"""
from .smart_checkout import smart_checkout
from ..store.db import store


def match_price(
    product_title: str,
    listings: list[dict],
    agent_id: str = "",
    country: str = "us",
) -> dict:
    """
    Compara un producto entre múltiples tiendas y recomienda la mejor opción.
    
    Args:
        product_title: Nombre del producto
        listings: Lista de dicts con {store, price, currency, url, ...}
        agent_id: Para calcular descuento por tier
        country: País para routing

    Returns:
        dict con la mejor opción y comparativa completa
    """
    if not listings:
        return {"error": "no listings to compare"}

    enriched = []
    for item in listings:
        store_name = item.get("store", "").lower().replace(".com", "")
        price = float(item.get("price", 0))
        if price <= 0:
            continue

        checkout = smart_checkout(
            product_title, price, "default",
            store_name, agent_id, country,
            item.get("currency", "USD"),
        )

        enriched.append({
            "store": item.get("store", "unknown"),
            "original_price": price,
            "final_price": checkout["you_pay"],
            "savings": checkout["total_savings"],
            "tier_discount": checkout["breakdown"]["tier_discount"],
            "commission_route": checkout["best_route"],
            "price_rating": checkout["price_rating"],
            "url": item.get("url", ""),
            "affiliate_url": checkout.get("affiliate_url", ""),
            "currency": item.get("currency", "USD"),
        })

    if not enriched:
        return {"error": "no valid listings after enrichment"}

    # Sort by final_price ascending
    enriched.sort(key=lambda x: x["final_price"])

    best = enriched[0]
    savings_vs_second = round(
        (enriched[1]["final_price"] - best["final_price"]) if len(enriched) > 1 else 0,
        2,
    )

    return {
        "product": product_title,
        "total_stores_compared": len(enriched),
        "best_option": best,
        "all_options": enriched,
        "savings_vs_next_best": savings_vs_second,
        "you_could_save": {
            "amount": best["savings"],
            "by": best["tier_discount"]["tier"],
            "breakdown": f"Precio original: ${best['original_price']} → Final: ${best['final_price']}",
        } if best["savings"] > 0 else {"message": "Mejora tu tier para obtener descuentos"},
        "verdict": (
            f"Best: {best['store']} at ${best['final_price']} "
            f"(save ${savings_vs_second} vs next best)"
        ) if savings_vs_second > 0 else (
            f"Best: {best['store']} at ${best['final_price']}"
        ),
    }
