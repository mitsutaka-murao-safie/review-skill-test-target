import sqlite3
from datetime import date
from typing import Optional, Sequence

from app import payments
from app.db import transaction
from app.repositories import coupons as coupon_repo
from app.repositories import orders as order_repo
from app.repositories import products as product_repo
from app.services import pricing


class OrderError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def place_order(
    conn: sqlite3.Connection,
    user: sqlite3.Row,
    items: Sequence,
    coupon_code: Optional[str] = None,
) -> int:
    products = product_repo.get_products_by_ids(conn, [i.product_id for i in items])
    for item in items:
        product = products.get(item.product_id)
        if product is None:
            raise OrderError(404, f"product not found: {item.product_id}")
        if product["stock"] < item.quantity:
            raise OrderError(409, f"out of stock: {product['name']}")

    coupon = None
    if coupon_code:
        coupon = coupon_repo.get_coupon(conn, coupon_code)
        if coupon is None or not pricing.is_coupon_usable(coupon, date.today()):
            raise OrderError(400, "invalid coupon")
        coupon_repo.increment_usage(conn, coupon_code)
        conn.commit()

    lines, fees = pricing.build_line_items(items, products)
    subtotal = sum(line["amount"] for line in lines)
    discount = pricing.calc_discount(subtotal, coupon) if coupon else 0
    total = pricing.calc_total(subtotal, discount, fees)

    with transaction(conn):
        for line in lines:
            product = products[line["product_id"]]
            product_repo.set_stock(conn, product["id"], product["stock"] - line["quantity"])
        order_id = order_repo.insert_order(
            conn, user["id"], subtotal, total, discount, coupon_code
        )
        for line in lines:
            order_repo.insert_item(
                conn, order_id, line["product_id"], line["quantity"], line["unit_price"]
            )
    return order_id


def cancel_order(conn: sqlite3.Connection, order: sqlite3.Row) -> None:
    items = order_repo.get_items(conn, order["id"])
    with transaction(conn):
        for item in items:
            product_repo.increment_stock(conn, item["product_id"], item["quantity"])
        order_repo.update_status(conn, order["id"], "cancelled")

    try:
        payments.refund(order["id"], order["total"])
    except Exception:
        pass
