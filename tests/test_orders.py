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
