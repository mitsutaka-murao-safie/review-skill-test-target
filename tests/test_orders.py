from tests.conftest import auth


def test_create_order(client):
    res = client.post(
        "/orders",
        json={"items": [{"product_id": 1, "quantity": 2}, {"product_id": 2, "quantity": 1}]},
        headers=auth("token-alice"),
    )
    assert res.status_code == 201
    body = res.json()
    assert body["subtotal"] == 1120
    assert body["total"] == 1232
    assert len(body["items"]) == 2


def test_create_order_out_of_stock(client):
    res = client.post(
        "/orders",
        json={"items": [{"product_id": 1, "quantity": 11}]},
        headers=auth("token-alice"),
    )
    assert res.status_code == 409
    products = {p["id"]: p for p in client.get("/products").json()}
    assert products[1]["stock"] == 10


def test_get_order_of_other_user_is_hidden(client):
    created = client.post(
        "/orders",
        json={"items": [{"product_id": 1, "quantity": 1}]},
        headers=auth("token-alice"),
    ).json()
    res = client.get(f"/orders/{created['id']}", headers=auth("token-bob"))
    assert res.status_code == 404


def test_create_order_with_coupon(client):
    res = client.post(
        "/orders",
        json={"items": [{"product_id": 1, "quantity": 4}], "coupon_code": "OFF10"},
        headers=auth("token-alice"),
    )
    assert res.status_code == 201
    body = res.json()
    assert body["subtotal"] == 2000
    assert body["discount"] == 200
    assert body["total"] == 1980


def test_create_order_with_expired_coupon(client):
    res = client.post(
        "/orders",
        json={"items": [{"product_id": 1, "quantity": 4}], "coupon_code": "EXPIRED"},
        headers=auth("token-alice"),
    )
    assert res.status_code == 400


def test_cancel_order_restores_stock(client):
    created = client.post(
        "/orders",
        json={"items": [{"product_id": 1, "quantity": 3}]},
        headers=auth("token-alice"),
    ).json()
    res = client.post(f"/orders/{created['id']}/cancel", headers=auth("token-alice"))
    assert res.status_code == 200
    assert res.json()["status"] == "cancelled"
    products = {p["id"]: p for p in client.get("/products").json()}
    assert products[1]["stock"] == 10


def test_list_my_orders(client):
    for _ in range(3):
        client.post(
            "/orders",
            json={"items": [{"product_id": 2, "quantity": 10}]},
            headers=auth("token-alice"),
        )
    res = client.get("/orders", params={"per_page": 2, "page": 1}, headers=auth("token-alice"))
    assert res.status_code == 200
