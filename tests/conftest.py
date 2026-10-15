import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db import connect, init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_path", str(tmp_path / "test.db"))
    conn = connect()
    init_db(conn)
    conn.executescript(
        """
        INSERT INTO users (id, email, name, api_token, is_admin) VALUES
            (1, 'alice@example.com', 'Alice', 'token-alice', 0),
            (2, 'bob@example.com', 'Bob', 'token-bob', 0),
            (3, 'admin@example.com', 'Admin', 'token-admin', 1);
        INSERT INTO products (id, name, price, stock) VALUES
            (1, 'Notebook', 500, 10),
            (2, 'Pen', 120, 100);
        INSERT INTO coupons (code, kind, value, max_uses, used_count, expires_on) VALUES
            ('OFF10', 'percent', 10, 100, 0, '2099-12-31'),
            ('YEN300', 'fixed', 300, 100, 0, '2099-12-31'),
            ('EXPIRED', 'percent', 10, 100, 0, '2000-01-01');
        """
    )
    conn.commit()
    conn.close()
    from app.main import app

    with TestClient(app) as c:
        yield c


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
