from fastapi import FastAPI

from app.db import connect, init_db
from app.routers import admin, invoices, orders, products

app = FastAPI(title="order-service")
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(invoices.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup() -> None:
    conn = connect()
    try:
        init_db(conn)
    finally:
        conn.close()
