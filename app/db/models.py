from sqlalchemy import String, Integer, Text, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum
from app.db.base import AbstractBase

class Role(Enum):
    ADMIN = "admin"
    USER = "user"

class User(AbstractBase):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=True)
    role: Mapped[Role] = mapped_column(default=Role.USER)

class TokenBlacklist(AbstractBase):
    __tablename__ = "token_blacklist"
    token: Mapped[str] = mapped_column(String)


class Category(AbstractBase):
    __tablename__ = "categories"
    title: Mapped[str] = mapped_column(String(100), unique=True)
    image_url: Mapped[str] = mapped_column(String(255), default="static/images/placeholder.png")
    description: Mapped[str] = mapped_column(Text, nullable=True)

    products = relationship("Product", back_populates="category")

class Product(AbstractBase):
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=True)

    category = relationship("Category", back_populates="products")







