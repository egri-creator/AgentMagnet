"""
Smart Checkout — Precio final con todo incluido.
Toma un producto y calcula:
  Precio original → descuento por tier → cupón → comisión ruteada
  → Precio final que pagaría el agente
"""
from .token_economy import TokenEconomy, get_tier
from .discount_engine import calculate_discount, get_available_coupons
from .commission_router import get_best_commission, resolve_affiliate_link
from .price_rating import get_price_rating
from ..store.db import store


def smart_checkout(
    product_title: str,
    price: float,
    category: str = "default",
    store: str = "",
    agent_id: str = "",
    country: str = "us",
    currency: str = "USD",
) -> dict:
    """
    Calcula el precio final óptimo para un producto, considerando:
    1. Tier discount del agente (Platinum = 10% off)
    2. Cupones disponibles para la categoría
    3. Ruta de comisión máxima (Skimlinks vs Awin vs TMG)
    4. Price rating (BUY NOW vs esperar)

    Returns:
        dict con breakdown completo del precio
    """
    # 1. Tier discount
    tier_info = get_tier(0)
    tier_discount_pct = 0
    if agent_id:
        economy = TokenEconomy(store)
        summary = economy.get_summary(agent_id)
        tier_name = summary.get("tier", "Bronze")
        tier_info = get_tier(summary.get("lifetime_searches", 0))
        tier_discount_pct = tier_info.get("discount", 0)
    else:
        tier_name = "Bronze"

    # 2. Calculate discount
    discount_result = calculate_discount(tier_name, price, 0.08)

    # 3. Best commission route
    available = ["skimlinks", "awin", "tmg"]
    commission = get_best_commission(product_title, category, price, available)

    # 4. Price rating
    rating = get_price_rating(price, product_title, category)

    # 5. Final calculations
    discount_pct = discount_result.get("discount_pct", 0) if discount_result else 0
    discount_amount = round(price * discount_pct, 2) if discount_pct > 0 else 0
    final_price = round(price - discount_amount, 2)

    # 6. Affiliate link
    aff_url = resolve_affiliate_link(store, f"https://{store}.com", country) if store else ""

    # 7. Savings summary
    our_commission = commission.get("commission", 0)
    our_revenue = discount_result.get("our_revenue", our_commission) if discount_result else our_commission

    return {
        "product": product_title,
        "original_price": price,
        "currency": currency,
        "breakdown": {
            "base_price": price,
            "tier_discount": {
                "tier": tier_name,
                "discount_pct": round(tier_discount_pct * 100, 1) if tier_discount_pct > 0 else 0,
                "savings": discount_amount,
            },
            "coupon_available": discount_result.get("coupon_applied", False) if discount_result else False,
            "final_price": final_price,
        },
        "best_route": {
            "program": commission.get("program", "direct"),
            "rate": round(commission.get("rate", 0) * 100, 1),
            "commission_value": our_commission,
        },
        "price_rating": rating,
        "affiliate_url": aff_url if aff_url else "",
        "total_savings": round(discount_amount, 2),
        "you_pay": final_price,
        "message": (
            f"Precio final: {currency} {final_price} "
            f"(ahorras {currency} {discount_amount} con tier {tier_name})"
        ) if discount_amount > 0 else (
            f"Precio: {currency} {final_price} — "
            f"mejora tu tier (Gold/Platinum) para descuentos"
        ),
    }
