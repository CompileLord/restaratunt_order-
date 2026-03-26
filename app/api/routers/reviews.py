from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db, get_current_user
from app.db.models import Review, Order, OrderItem
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter(prefix="/products", tags=["reviews"])

@router.get("/{id}/reviews", response_model=List[ReviewResponse])
def get_product_reviews(id: int, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1), db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.product_id == id).offset(skip).limit(limit).all()

@router.post("/{id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(id: int, review_in: ReviewCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user_order_ids = [o.id for o in db.query(Order.id).filter(Order.user_id == current_user.id).all()]
    if not user_order_ids:
        raise HTTPException(status_code=403, detail="You have not ordered this product")

    ordered = db.query(OrderItem).filter(OrderItem.order_id.in_(user_order_ids), OrderItem.product_id == id).first()
    if not ordered:
        raise HTTPException(status_code=403, detail="You have not ordered this product")

    new_review = Review(user_id=current_user.id, product_id=id, **review_in.model_dump())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review
