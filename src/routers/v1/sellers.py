from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedSellerBooks

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о продавце (возвращает созданного продавца).
@sellers_router.post(
    "/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED
)  # Модель ответа
async def create_seller(
    seller: IncomingSeller, session: DBSession
):  
    new_seller = Seller(
        first_name=seller.first_name, last_name=seller.last_name, email=seller.email, password=seller.password
    )
    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка, возвращающая всех продавцов
@sellers_router.get(path="/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    # sellers: [{'id': 1, 'first_name': 'Ivan', ...}, {'id': 2, ...}]
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


# Ручка для получения продавца по id
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerBooks)
async def get_seller(seller_id: int, session: DBSession):
    query = select(Seller).options(selectinload(Seller.books)).where(Seller.id == seller_id)
    res = await session.execute(query)
    seller = res.scalars().first()
    return seller


# Ручка для удаления продавца
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)  
    if deleted_seller:
        await session.delete(deleted_seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)  


# Ручка для обновления данных о книге
@sellers_router.put("/{seller_id}")
async def update_seller(seller_id: int, new_data: ReturnedSeller, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)