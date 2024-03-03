from typing import List

from pydantic import BaseModel

from .books import ReturnedBook

__all__ = [
    "BaseSeller",
    "IncomingSeller",
    "ReturnedSeller",
    "ReturnedAllSellers",
    "ReturnedSellerBooks",
]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str


class IncomingSeller(BaseSeller):
    # У нас уже есть данные по продавцу из базового класса
    password: str


class ReturnedSeller(BaseSeller):
    id: int

    class Config:
        orm_mode = True


class ReturnedSellerBooks(BaseSeller):
    books: List[ReturnedBook]


class ReturnedAllSellers(BaseModel):
    sellers: List[ReturnedSeller]
