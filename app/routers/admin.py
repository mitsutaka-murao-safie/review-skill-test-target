import csv
import io
import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.auth import get_current_user, require_admin
from app.db import get_conn
from app.repositories import orders as order_repo
from app.repositories import products as product_repo

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/orders")
def search_orders(
    status: Optional[str] = None,
    email: Optional[str] = None,
    _: sqlite3.Row = Depends(require_admin),
    conn: sqlite3.Connection = Depends(get_conn),
):
    return [dict(r) for r in order_repo.search_orders(conn, status, email)]


@router.get("/orders/export")
def export_orders_csv(
    _: sqlite3.Row = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_conn),
):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["order_id", "email", "status", "product", "quantity", "税抜金額", "税込金額"])

    for order in order_repo.list_all_orders(conn):
        for item in order_repo.get_items(conn, order["id"]):
            product = product_repo.get_product(conn, item["product_id"])
            amount = item["unit_price"] * item["quantity"]
            writer.writerow(
                [
                    order["id"],
                    order["email"],
                    order["status"],
                    product["name"],
                    item["quantity"],
                    amount,
                    int(amount * 1.08),
                ]
            )

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"},
    )
