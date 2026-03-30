from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatusSchema(str, Enum):
    NEW = "new"
    PREPARING = "preparing"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentMethodSchema(str, Enum):
    CASH = "cash"
    CARD = "card"
    CASH_UPPER = "CASH"
    CARD_UPPER = "CARD"


class OrderCreate(BaseModel):
    payment_method: PaymentMethodSchema
    delivery_address: str


class OrderItemSchema(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_per_item: float

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatusSchema
    total_amount: float
    payment_method: PaymentMethodSchema
    delivery_address: str

    model_config = ConfigDict(from_attributes=True)


class OrderUpdate(BaseModel):
    status: OrderStatusSchema

