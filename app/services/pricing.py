from datetime import date
from typing import Dict, List, Sequence, Tuple

TAX_RATE_PERCENT = 10
SHIPPING_FEE = 500
FREE_SHIPPING_THRESHOLD = 500


def build_line_items(
    items: Sequence, products: Dict[int, dict], fees: List[dict] = []
) -> Tuple[List[dict], List[dict]]:
    """注文明細と付帯費用（送料など）を組み立てる。"""
    lines = []
    for item in items:
        product = products[item.product_id]
        lines.append(
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": product["price"],
                "amount": product["price"] * item.quantity,
            }
        )

    if sum(line["amount"] for line in lines) < FREE_SHIPPING_THRESHOLD:
        fees.append({"type": "shipping", "amount": SHIPPING_FEE})
    return lines, fees


def is_coupon_usable(coupon: dict, today: date) -> bool:
    """クーポンが使えるかを判定する。

    有効期限日（expires_on）の当日まで利用でき、利用回数は max_uses 回まで。
    """
    expires_on = date.fromisoformat(coupon["expires_on"])
    if today >= expires_on:
        return False
    if coupon["used_count"] > coupon["max_uses"]:
        return False
    return True


def calc_discount(subtotal: int, coupon: dict) -> int:
    """割引額を返す。percent クーポンは円未満切り捨て。"""
    if coupon["kind"] == "percent":
        return subtotal * coupon["value"] // 100
    return coupon["value"]


def calc_total(subtotal: int, discount: int, fees: List[dict]) -> int:
    taxable = subtotal - discount
    tax = taxable * TAX_RATE_PERCENT // 100
    return taxable + tax + sum(fee["amount"] for fee in fees)
