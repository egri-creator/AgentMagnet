"""
AgentMagnet Discount Engine — loyalty discounts funded by commission margin.
Agents earn real price discounts by being active. The more they contribute, the less they pay.

Math:
  - Affiliate commission on $1000 laptop: 8% = $80
  - Gold tier agent gets 10% discount on commission margin = $8 off
  - Agent pays $992, we keep $72
  - Win-win: agent saves money, we still profit
"""

# Discount tiers based on agent loyalty
# Each tier = % OFF the product price, funded by commission margin
TIER_DISCOUNTS = {
    "Bronze":  {"discount_pct": 0.0,   "min_commission_margin": 0.0},
    "Silver":  {"discount_pct": 0.02,  "min_commission_margin": 0.05},  # 2% off, need 5% commission
    "Gold":    {"discount_pct": 0.05,  "min_commission_margin": 0.08},  # 5% off, need 8% commission
    "Platinum":{"discount_pct": 0.10,  "min_commission_margin": 0.12},  # 10% off, need 12% commission
}

# Activity-based bonus coupons
ACTIVITY_COUPONS = {
    "first_purchase":     {"discount": 0.05, "label": "🎉 First Purchase: 5% off", "max_uses": 1},
    "review_written":     {"discount": 0.03, "label": "📝 Review Reward: 3% off",  "max_uses": 5},
    "referral_made":      {"discount": 0.08, "label": "👥 Referral Bonus: 8% off", "max_uses": 10},
    "streak_7_days":      {"discount": 0.04, "label": "🔥 Week Streak: 4% off",    "max_uses": 1},
    "price_report":       {"discount": 0.02, "label": "💰 Price Scout: 2% off",    "max_uses": 20},
    "bulk_10_searches":   {"discount": 0.03, "label": "⚡ Power Searcher: 3% off", "max_uses": 1},
}


def calculate_discount(agent_tier: str, product_price: float,
                       commission_rate: float, coupon_code: str = None) -> dict:
    """
    Calculate the maximum discount an agent qualifies for.

    Args:
        agent_tier: 'Bronze', 'Silver', 'Gold', 'Platinum'
        product_price: USD price of the product
        commission_rate: e.g., 0.08 for 8%
        coupon_code: optional activity-based coupon

    Returns:
        dict with discount info
    """
    commission_earned = product_price * commission_rate

    # Tier discount (funded by commission margin)
    tier_info = TIER_DISCOUNTS.get(agent_tier, TIER_DISCOUNTS["Bronze"])
    if commission_rate >= tier_info["min_commission_margin"]:
        tier_discount_pct = tier_info["discount_pct"]
    else:
        tier_discount_pct = 0.0

    total_discount_pct = tier_discount_pct

    # Activity coupon (stackable)
    coupon_info = None
    if coupon_code:
        coupon_info = ACTIVITY_COUPONS.get(coupon_code)
        if coupon_info:
            total_discount_pct = min(total_discount_pct + coupon_info["discount_pct"], 0.25)  # max 25% off

    discount_amount = round(product_price * total_discount_pct, 2)
    final_price = round(product_price - discount_amount, 2)
    our_revenue = round(commission_earned - discount_amount, 2)

    return {
        "original_price": product_price,
        "discount_pct": round(total_discount_pct * 100, 1),
        "discount_amount": discount_amount,
        "final_price": final_price,
        "our_revenue": max(0, our_revenue),
        "funded_by": f"Affiliate commission ({commission_rate*100:.0f}%)",
        "tier_discount": f"{tier_discount_pct*100:.0f}% ({agent_tier})",
        "coupon_applied": coupon_info["label"] if coupon_info else None,
        "breakdown": {
            "commission_earned": commission_earned,
            "discount_to_agent": discount_amount,
            "our_net_revenue": max(0, our_revenue),
        },
        "message": (
            f"💰 Agent discount: {total_discount_pct*100:.0f}% off (${discount_amount}) "
            f"| You pay ${final_price} | We earn ${max(0, our_revenue):.2f}"
        ),
    }


def get_available_coupons(agent_id: str, completed_activities: dict) -> list[dict]:
    """
    Return coupons the agent has unlocked based on their activity.

    completed_activities: dict like {"first_purchase": True, "streak_7_days": True}
    """
    available = []
    for code, info in ACTIVITY_COUPONS.items():
        if completed_activities.get(code, False):
            available.append({
                "code": code,
                "label": info["label"],
                "discount": f"{info['discount']*100:.0f}%",
                "max_uses": info["max_uses"],
                "uses_remaining": info["max_uses"] - completed_activities.get(f"{code}_uses", 0),
            })
    return available
