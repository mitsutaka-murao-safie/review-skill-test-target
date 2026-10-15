import sqlite3
from datetime import datetime, timezone
from typing import List, Optional


def insert_order(
    conn: sqlite3.Connection, user_id: int, subtotal: int, total: int
) -> int:
    cur = conn.execute(
        "INSERT INTO orders (user_id, status, subtotal, total, created_at) "
        "VALUES (?, 'placed', ?, ?, ?)",
        (user_id, subtotal, total, datetime.now(timezone.utc).isoformat()),
    )
    return cur.lastrowid


def insert_item(
    conn: sqlite3.Connection, order_id: int, product_id: int, quantity: int, unit_price: int
) -> None:
    conn.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
        "VALUES (?, ?, ?, ?)",
        (order_id, product_id, quantity, unit_price),
    )


def get_order(conn: sqlite3.Connection, order_id: int) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()


def get_items(conn: sqlite3.Connection, order_id: int) -> List[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
    ).fetchall()
