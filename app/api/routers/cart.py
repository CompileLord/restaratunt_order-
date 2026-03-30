from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.api.dependencies import get_db, get_current_user
from app.db.models import CartItem, Product
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse

router = APIRouter(prefix="/cart", tags=["cart"])

@router.get("/", response_model=List[CartItemResponse])
def get_cart(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(CartItem).options(joinedload(CartItem.product)).filter(CartItem.user_id == current_user.id).all()

@router.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_cart(item: CartItemCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == item.product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    existing_item = db.query(CartItem).filter(CartItem.user_id == current_user.id, CartItem.product_id == item.product_id).first()
    if existing_item:
        existing_item.quantity += item.quantity
        if existing_item.quantity <= 0:
            db.delete(existing_item)
            db.commit()
            return CartItemResponse(id=0, user_id=current_user.id, product_id=item.product_id, quantity=0, product={"id": product.id, "title": product.title, "price": float(product.price), "image_url": product.image_url})
        db.commit()
        db.refresh(existing_item)
        return existing_item

    new_item = CartItem(user_id=current_user.id, **item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/{item_id}", response_model=CartItemResponse)
def update_cart_item(item_id: int, item_update: CartItemUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if item_update.quantity <= 0:
        db.delete(item)
        db.commit()
        return None

    item.quantity = item_update.quantity
    db.commit()
    db.refresh(item)
    return item

@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return None

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(item_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(item)
    db.commit()
    return None
