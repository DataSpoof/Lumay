def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_read_item(client):
    response = client.post(
        "/items",
        json={"name": "Notebook", "description": "A5 dotted", "price": 4.5},
    )
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Notebook"
    assert created["in_stock"] is True

    response = client.get(f"/items/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_list_items_is_paginated(client):
    for i in range(3):
        client.post("/items", json={"name": f"Item {i}", "price": i})

    assert len(client.get("/items").json()) == 3
    assert len(client.get("/items?skip=1&limit=1").json()) == 1


def test_update_item_applies_partial_changes(client):
    item_id = client.post("/items", json={"name": "Pen", "price": 2.0}).json()["id"]

    response = client.put(f"/items/{item_id}", json={"price": 3.5})
    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 3.5
    assert body["name"] == "Pen"


def test_delete_item(client):
    item_id = client.post("/items", json={"name": "Mug"}).json()["id"]

    assert client.delete(f"/items/{item_id}").status_code == 204
    assert client.get(f"/items/{item_id}").status_code == 404


def test_missing_item_returns_404(client):
    assert client.get("/items/999").status_code == 404
    assert client.put("/items/999", json={"name": "x"}).status_code == 404
    assert client.delete("/items/999").status_code == 404


def test_validation_rejects_negative_price(client):
    response = client.post("/items", json={"name": "Bad", "price": -1})
    assert response.status_code == 422
