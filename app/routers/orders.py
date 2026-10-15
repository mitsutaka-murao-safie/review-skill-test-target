import sqlite3

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import get_current_user
from app.config import settings
from app.db import get_conn, transaction
from app.models import OrderIn, OrderOut
from app.repositories import orders as order_repo
from app.repositories import products as product_repo

router = APIRouter(prefix="/orders", tags=["orders"])

TAX_RATE_PERCENT = 10


def _to_out(conn: sqlite3.Connection, order: sqlite3.Row) -> OrderOut:
    items = [dict(i) for i in order_repo.get_items(conn, order["id"])]
    return OrderOut(**dict(order), items=items)


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    body: OrderIn,
    user: sqlite3.Row = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_conn),
):
    if sum(i.quantity for i in body.items) > settings.max_items_per_order:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "too many items")

    with transaction(conn):
        subtotal = 0
        lines = []
        for item in body.items:
            product = product_repo.get_product(conn, item.product_id)
            if product is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "product not found")
            if not product_repo.decrement_stock(conn, item.product_id, item.quantity):
                raise HTTPException(status.HTTP_409_CONFLICT, "out of stock")
            subtotal += product["price"] * item.quantity
            lines.append((item.product_id, item.quantity, product["price"]))

        total = subtotal + subtotal * TAX_RATE_PERCENT // 100
        order_id = order_repo.insert_order(conn, user["id"], subtotal, total)
        for product_id, quantity, unit_price in lines:
            order_repo.insert_item(conn, order_id, product_id, quantity, unit_price)

    return _to_out(conn, order_repo.get_order(conn, order_id))


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    user: sqlite3.Row = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_conn),
):
    order = order_repo.get_order(conn, order_id)
    if order is None or order["user_id"] != user["id"]:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "order not found")
    return _to_out(conn, order)
