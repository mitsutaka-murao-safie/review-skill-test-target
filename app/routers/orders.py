import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app import notifications
from app.auth import get_current_user
from app.config import settings
from app.db import get_conn
from app.models import OrderIn, OrderOut
from app.repositories import orders as order_repo
from app.services import order_service
from app.services.order_service import OrderError

router = APIRouter(prefix="/orders", tags=["orders"])


def _to_out(conn: sqlite3.Connection, order: sqlite3.Row) -> OrderOut:
    items = [dict(i) for i in order_repo.get_items(conn, order["id"])]
    return OrderOut(**dict(order), items=items)


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: OrderIn,
    user: sqlite3.Row = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_conn),
):
    if sum(i.quantity for i in body.items) > settings.max_items_per_order:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "too many items")

    try:
        order_id = order_service.place_order(conn, user, body.items, body.coupon_code)
    except OrderError as e:
        raise HTTPException(e.status_code, e.message)

    order = order_repo.get_order(conn, order_id)
    await notifications.notify_order_placed(dict(user), order_id, order["total"])
    return _to_out(conn, order)


@router.get("", response_model=List[OrderOut])
def list_my_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: str = "newest",
    user: sqlite3.Row = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_conn),
):
    offset = page * per_page
    orders = order_repo.list_orders_for_user(conn, user["id"], sort, per_page, offset)
    return [_to_out(conn, o) for o in orders]


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


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(
    order_id: int,
    user: sqlite3.Row = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_conn),
):
    order = order_repo.get_order(conn, order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "order not found")

    order_service.cancel_order(conn, order)
    return _to_out(conn, order_repo.get_order(conn, order_id))
