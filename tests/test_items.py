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


def test_update_rejects_explicit_null_on_required_fields(client):
    """Regression: these reached the DB as NOT NULL violations and gave a 500."""
    item_id = client.post("/items", json={"name": "Lamp", "price": 9.0}).json()["id"]

    for field in ("name", "price", "in_stock"):
        response = client.put(f"/items/{item_id}", json={field: None})
        assert response.status_code == 422, f"{field} should be rejected"

    # The item is untouched by the rejected updates.
    body = client.get(f"/items/{item_id}").json()
    assert body["name"] == "Lamp"
    assert body["price"] == 9.0


def test_update_can_clear_the_nullable_description(client):
    item_id = client.post(
        "/items", json={"name": "Lamp", "description": "brass"}
    ).json()["id"]

    response = client.put(f"/items/{item_id}", json={"description": None})
    assert response.status_code == 200
    assert response.json()["description"] is None


def test_empty_update_is_a_no_op(client):
    created = client.post("/items", json={"name": "Chair", "price": 20.0}).json()

    response = client.put(f"/items/{created['id']}", json={})
    assert response.status_code == 200
    assert response.json()["name"] == "Chair"
    assert response.json()["price"] == 20.0


def test_timestamps_are_utc_aware(client):
    """SQLite stores naive datetimes; responses must still carry an offset."""
    body = client.post("/items", json={"name": "Clock"}).json()

    for field in ("created_at", "updated_at"):
        assert body[field].endswith("Z") or "+00:00" in body[field], body[field]


def test_update_bumps_updated_at_but_not_created_at(client):
    created = client.post("/items", json={"name": "Desk", "price": 1.0}).json()

    updated = client.put(f"/items/{created['id']}", json={"price": 2.0}).json()

    assert updated["created_at"] == created["created_at"]
    assert updated["updated_at"] >= created["updated_at"]


def test_pagination_past_the_end_returns_empty(client):
    client.post("/items", json={"name": "Only"})

    assert client.get("/items?skip=50").json() == []


def test_validation_rejects_blank_name_and_overlong_fields(client):
    assert client.post("/items", json={"name": ""}).status_code == 422
    assert client.post("/items", json={"name": "x" * 121}).status_code == 422
    assert (
        client.post("/items", json={"name": "ok", "description": "d" * 501}).status_code
        == 422
    )


def test_list_query_params_are_validated(client):
    assert client.get("/items?skip=-1").status_code == 422
    assert client.get("/items?limit=0").status_code == 422
    assert client.get("/items?limit=501").status_code == 422
