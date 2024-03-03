import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers

# Тест на ручку создания продавца
@pytest.mark.asyncio
async def test_seller_creation(async_client):
    payload = {"first_name": "Ivan", "last_name": "Ivanov", "email": "iivanov@example.com", "password": "secret"}
    resp = await async_client.post("/api/v1/sellers/", json=payload)

    assert resp.status_code == status.HTTP_201_CREATED

    resp_body = resp.json()
    assert resp_body == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "iivanov@example.com",
        "id": resp_body["id"]
    }

# Тест на ручку списка продавцов (его получения)
@pytest.mark.asyncio
async def test_retrieve_all_sellers(db_session, async_client):
    manual_seller1 = sellers.Seller(
        first_name="Petr", last_name="Ivanov", email="pivanov@example.com", password="secret"
    )
    manual_seller2 = sellers.Seller(
        first_name="Ivan", last_name="Ivanov", email="iivanov@example.com", password="supersecret"
    )

    db_session.add_all([manual_seller1, manual_seller2])
    await db_session.flush()

    resp = await async_client.get("/api/v1/sellers/")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()["sellers"]) == 2

    fetched_data = resp.json()
    assert fetched_data == {
        "sellers": [
            {
                "first_name": "Petr",
                "last_name": "Ivanov",
                "email": "pivanov@example.com",
                "id": manual_seller1.id
            },
            {
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "email": "iivanov@example.com",
                "id": manual_seller2.id,
            }
        ]
    }

# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_retrieve_specific_seller(db_session, async_client):
    manual_seller = sellers.Seller(
        first_name="Ivan", last_name="Ivanov", email="iivanov@example.com", password="secret")

    db_session.add(manual_seller)
    await db_session.flush()

    manual_book = books.Book(title="Woe from Mind", author="Alexander Griboyedov", year=1825, count_pages=320, seller_id=manual_seller.id)

    db_session.add(manual_book)
    await db_session.flush()

    resp = await async_client.get(f"/api/v1/sellers/{manual_seller.id}")

    assert resp.status_code == status.HTTP_200_OK

    fetched_data = resp.json()
    assert fetched_data == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "iivanov@example.com",
        "books": [
            {
                "title": "Woe from Mind",
                "author": "Alexander Griboyedov",
                "year": 1825,
                "id": manual_book.id,
                "count_pages": 320,
            }
        ]
    }

# Тест на ручку для удаления продавца
@pytest.mark.asyncio
async def test_remove_seller(db_session, async_client):
    manual_seller = sellers.Seller(
        first_name="Ivan", last_name="Ivanov", email="iivanov@example.com", password="secret"
    )

    db_session.add(manual_seller)
    await db_session.flush()

    resp = await async_client.delete(f"/api/v1/sellers/{manual_seller.id}")

    assert resp.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()


    # Проверка, что продавец удален
    all_sellers = await db_session.execute(select(sellers.Seller))
    all_sellers_list = all_sellers.scalars().all()
    assert len(all_sellers_list) == 0

# Тест на ручку обновления данных о продавце
@pytest.mark.asyncio
async def test_modify_seller(db_session, async_client):
    manual_seller = sellers.Seller(
        first_name="Ivan", last_name="Ivanov", email="iivanov@example.com", password="secret")

    db_session.add(manual_seller)
    await db_session.flush()

    resp = await async_client.put(
        f"/api/v1/sellers/{manual_seller.id}",
        json={"first_name": "Nikolay", "last_name": "Nikolaev", "email": "nnikolaev@example.com"})

    assert resp.status_code == status.HTTP_200_OK

    updated_seller = await db_session.get(sellers.Seller, manual_seller.id)
    assert updated_seller.first_name == "Nikolay"
    assert updated_seller.last_name == "Nikolaev"
    assert updated_seller.email == "nnikolaev@example.com"
