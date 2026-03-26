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
    __tablename__ = "products"
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    image_url: Mapped[str] = mapped_column(Text, nullable=True)
    ingredients: Mapped[str] = mapped_column(Text, nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    discount_percent: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    category = relationship("Category", back_populates="products")

class CartItem(AbstractBase):
    __tablename__ = "cart_items"
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)

class OrderStatus(Enum):
    NEW = "new"
    PREPARING = "preparing"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"

class Order(AbstractBase):
    __tablename__ = "orders"
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.NEW)
    total_amount: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(nullable=False)
    delivery_address: Mapped[str] = mapped_column(Text, nullable=False)

class OrderItem(AbstractBase):
    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_item: Mapped[float] = mapped_column(Numeric(precision=10, scale=2), nullable=False)

class Review(AbstractBase):
    __tablename__ = "reviews"
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)







