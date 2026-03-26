from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db, get_current_user, check_is_admin
from app.db.models import Order, OrderItem, CartItem, Product
from app.schemas.order import OrderResponse, OrderCreate, OrderUpdate

router = APIRouter(tags=["orders"])

@router.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0.0
    products_map = {}
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or not product.is_active:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not available")
        total_amount += float(product.price) * item.quantity
        products_map[item.product_id] = product

    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        payment_method=order_in.payment_method,
        delivery_address=order_in.delivery_address
    )
    db.add(new_order)
    db.flush()

    for item in cart_items:
        product = products_map[item.product_id]
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_per_item=float(product.price)
        )
        db.add(order_item)

    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/orders/", response_model=List[OrderResponse])
def get_my_orders(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Order).filter(Order.user_id == current_user.id).offset(skip).limit(limit).all()

@router.get("/orders/{id}", response_model=OrderResponse)
def get_order(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/admin/orders", response_model=List[OrderResponse])
def admin_get_orders(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1), db: Session = Depends(get_db), admin=Depends(check_is_admin)):
    return db.query(Order).offset(skip).limit(limit).all()

@router.patch("/admin/orders/{id}", response_model=OrderResponse)
def admin_update_order_status(id: int, status_update: OrderUpdate, db: Session = Depends(get_db), admin=Depends(check_is_admin)):
    order = db.query(Order).filter(Order.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order
