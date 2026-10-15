import sqlite3
from typing import List

from fastapi import APIRouter, Depends

from app.db import get_conn
from app.models import ProductOut
from app.repositories import products as product_repo

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductOut])
def list_products(sort: str = "name", conn: sqlite3.Connection = Depends(get_conn)):
    return [dict(r) for r in product_repo.list_products(conn, sort)]
