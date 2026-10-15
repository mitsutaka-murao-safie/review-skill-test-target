import sqlite3
from typing import Optional


def get_coupon(conn: sqlite3.Connection, code: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM coupons WHERE code = ?", (code,)).fetchone()


def increment_usage(conn: sqlite3.Connection, code: str) -> None:
    conn.execute(
        "UPDATE coupons SET used_count = used_count + 1 WHERE code = ?", (code,)
    )
