import hmac
import sqlite3

from fastapi import Depends, Header, HTTPException, status

from app.db import get_conn


def get_current_user(
    authorization: str = Header(...),
    conn: sqlite3.Connection = Depends(get_conn),
) -> sqlite3.Row:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid authorization header")

    row = conn.execute(
        "SELECT * FROM users WHERE api_token = ?", (token,)
    ).fetchone()
    if row is None or not hmac.compare_digest(row["api_token"], token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    return row


def require_admin(user: sqlite3.Row = Depends(get_current_user)) -> sqlite3.Row:
    if not user["is_admin"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "admin only")
    return user
