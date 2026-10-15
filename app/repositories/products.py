import sqlite3
from typing import List, Optional

ALLOWED_SORTS = {
    "price": "price",
    "-price": "price DESC",
    "name": "name",
}


def get_product(conn: sqlite3.Connection, product_id: int) -> Optional[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()


def list_products(conn: sqlite3.Connection, sort: str = "name") -> List[sqlite3.Row]:
    order_by = ALLOWED_SORTS.get(sort, "name")
    return conn.execute(f"SELECT * FROM products ORDER BY {order_by}").fetchall()


def decrement_stock(conn: sqlite3.Connection, product_id: int, quantity: int) -> bool:
    """在庫が足りる場合のみ減らす。減らせたら True。"""
    cur = conn.execute(
        "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
        (quantity, product_id, quantity),
    )
    return cur.rowcount == 1


def increment_stock(conn: sqlite3.Connection, product_id: int, quantity: int) -> None:
    conn.execute(
        "UPDATE products SET stock = stock + ? WHERE id = ?",
        (quantity, product_id),
    )
