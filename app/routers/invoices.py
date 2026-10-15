import os
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse

from app.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("")
def download_invoice(
    filename: str = Query(...),
    user: sqlite3.Row = Depends(get_current_user),
):
    # 請求書ファイルは invoice-<user_id>-<order_id>.pdf の形式で保存されている
    if not filename.startswith(f"invoice-{user['id']}-"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "forbidden")

    path = os.path.join(settings.invoice_dir, filename)
    if not os.path.isfile(path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invoice not found")
    return FileResponse(path, media_type="application/pdf")
