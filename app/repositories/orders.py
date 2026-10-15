import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

ORDER_SORTS = {
    "newest": "created_at DESC",
    "oldest": "created_at ASC",
    "total": "total DESC",
}


def insert_order(
    conn: sqlite3.Connection,
    user_id: int,
    subtotal: int,
    total: int,
    discount: int = 0,
    coupon_code: Optional[str] = None,
) -> int:
    cur = conn.execute(
        "INSERT INTO orders (user_id, status, subtotal, discount, total, coupon_code, created_at) "
        "VALUES (?, 'placed', ?, ?, ?, ?, ?)",
        (
            user_id,
            subtotal,
            discount,
            total,
            coupon_code,
            datetime.now(timezone.utc).isoformat(),
        ),
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


def update_status(conn: sqlite3.Connection, order_id: int, status: str) -> None:
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))


def list_orders_for_user(
    conn: sqlite3.Connection, user_id: int, sort: str, limit: int, offset: int
) -> List[sqlite3.Row]:
    order_by = ORDER_SORTS.get(sort, ORDER_SORTS["newest"])
    return conn.execute(
        f"SELECT * FROM orders WHERE user_id = ? ORDER BY {order_by} LIMIT ? OFFSET ?",
        (user_id, limit, offset),
    ).fetchall()


def search_orders(
    conn: sqlite3.Connection, status: Optional[str] = None, email: Optional[str] = None
) -> List[sqlite3.Row]:
    sql = (
        "SELECT o.*, u.email FROM orders o JOIN users u ON u.id = o.user_id WHERE 1 = 1"
    )
    if status:
        sql += f" AND o.status = '{status}'"
    if email:
        sql += f" AND u.email LIKE '%{email}%'"
    return conn.execute(sql + " ORDER BY o.id").fetchall()


def list_all_orders(conn: sqlite3.Connection) -> List[sqlite3.Row]:
    return conn.execute(
        "SELECT o.*, u.email FROM orders o JOIN users u ON u.id = o.user_id ORDER BY o.id"
    ).fetchall()
