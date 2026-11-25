
import pytest

from tinydb import TinyDB, Query

from app import app
import app.products.views as product_views


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Створюємо окрему тимчасову базу.
    test_db = TinyDB(
        tmp_path / "test_products.json",
        encoding="utf-8",
    )

    test_table = test_db.table("products")

    # Підміняємо справжню таблицю тільки
    # на час виконання тесту.
    monkeypatch.setattr(
        product_views,
        "products_table",
        test_table,
    )

    # Вимикаємо CSRF лише в тестовому клієнті.
    monkeypatch.setitem(
        app.config,
        "WTF_CSRF_ENABLED",
        False,
    )

    monkeypatch.setitem(
        app.config,
        "TESTING",
        True,
    )

    with app.test_client() as test_client:
        yield test_client, test_table

    test_db.close()


def sample_product():
    return {
        "name": "Тестовий ноутбук",
        "content": "Ноутбук для тестування CRUD",
        "price": "15000.50",
        "category": "техніка",
        "quantity": "5",
    }


def create_product(client):
    return client.post(
        "/product/add",
        data=sample_product(),
        follow_redirects=True,
    )


# CREATE
def test_create_product(client):
    test_client, table = client

    response = create_product(test_client)

    assert response.status_code == 200
    assert len(table.all()) == 1

    product = table.all()[0]

    assert product["name"] == "Тестовий ноутбук"
    assert product["price"] == 15000.50
    assert product["quantity"] == 5
    assert product["id"] == 1
    assert product["created_at"]


# READ: список товарів
def test_read_products(client):
    test_client, table = client

    create_product(test_client)

    response = test_client.get("/product")

    assert response.status_code == 200
    assert "Тестовий ноутбук".encode() in response.data


# READ: один товар
def test_read_product_details(client):
    test_client, table = client

    create_product(test_client)

    response = test_client.get("/product/1")

    assert response.status_code == 200
    assert "Ноутбук для тестування CRUD".encode() in response.data


# UPDATE
def test_update_product(client):
    test_client, table = client

    create_product(test_client)

    original = table.all()[0].copy()

    updated_data = sample_product()
    updated_data["name"] = "Оновлений ноутбук"
    updated_data["price"] = "12000.00"

    response = test_client.post(
        "/product/1/edit",
        data=updated_data,
        follow_redirects=True,
    )

    assert response.status_code == 200

    updated = table.get(Query().id == 1)

    assert updated["name"] == "Оновлений ноутбук"
    assert updated["price"] == 12000.00

    # id і дата створення не змінюються.
    assert updated["id"] == original["id"]
    assert updated["created_at"] == original["created_at"]


# DELETE
def test_delete_product(client):
    test_client, table = client

    create_product(test_client)

    response = test_client.post(
        "/product/1/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert len(table.all()) == 0


# VALIDATION: коротка назва
def test_invalid_short_name(client):
    test_client, table = client

    data = sample_product()
    data["name"] = "AB"

    response = test_client.post(
        "/product/add",
        data=data,
    )

    assert response.status_code == 200
    assert len(table.all()) == 0


# VALIDATION: від'ємна ціна
def test_invalid_negative_price(client):
    test_client, table = client

    data = sample_product()
    data["price"] = "-50.00"

    response = test_client.post(
        "/product/add",
        data=data,
    )

    assert response.status_code == 200
    assert len(table.all()) == 0


# VALIDATION: від'ємна кількість
def test_invalid_negative_quantity(client):
    test_client, table = client

    data = sample_product()
    data["quantity"] = "-2"

    response = test_client.post(
        "/product/add",
        data=data,
    )

    assert response.status_code == 200
    assert len(table.all()) == 0


# VALIDATION: понад два знаки після коми
def test_invalid_price_precision(client):
    test_client, table = client

    data = sample_product()
    data["price"] = "15.999"

    response = test_client.post(
        "/product/add",
        data=data,
    )

    assert response.status_code == 200
    assert len(table.all()) == 0


# NOT FOUND
def test_product_not_found(client):
    test_client, table = client

    response = test_client.get(
        "/product/99999"
    )

    assert response.status_code == 404
