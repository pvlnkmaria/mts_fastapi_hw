from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import EmailType, PasswordType

from .base import BaseModel
from .books import Book


class Seller(BaseModel):
    __tablename__ = "sellers_table"
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        EmailType, nullable=False
    )  # Используем EmailType для валидации email
    password: Mapped[str] = mapped_column(
        PasswordType(schemes=["pbkdf2_sha512"]), nullable=False
    )  # Используем PasswordType для хранения пароля
    books: Mapped[list["Book"]] = relationship(
        "Book", back_populates="seller", cascade="all, delete-orphan"
    )
