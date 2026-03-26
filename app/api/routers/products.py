from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.dependencies import get_db, get_current_user, check_is_admin
from app.db.models import Product
from app.schemas.product import ProductOutSchema, ProductUpdate
from app.utils.services import save_images

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductOutSchema])
def get_products(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter(Product.is_active == True)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if search:
        query = query.filter(Product.title.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    return query.offset(skip).limit(limit).all()

@router.get("/{id}", response_model=ProductOutSchema)
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductOutSchema, status_code=status.HTTP_201_CREATED)
def create_product(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(..., gt=0),
    category_id: int = Form(...),
    ingredients: Optional[str] = Form(None),
    discount_percent: int = Form(0, ge=0, le=100),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin=Depends(check_is_admin)
):
    image_url = save_images(image) if image else None
    db_product = Product(
        title=title,
        description=description,
        price=price,
        category_id=category_id,
        ingredients=ingredients,
        discount_percent=discount_percent,
        image_url=image_url
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{id}", response_model=ProductOutSchema)
def update_product(
    id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category_id: Optional[int] = Form(None),
    ingredients: Optional[str] = Form(None),
    discount_percent: Optional[int] = Form(None, ge=0, le=100),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_admin=Depends(check_is_admin)
):
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if title is not None:
        db_product.title = title
    if description is not None:
        db_product.description = description
    if price is not None:
        db_product.price = price
    if category_id is not None:
        db_product.category_id = category_id
    if ingredients is not None:
        db_product.ingredients = ingredients
    if discount_percent is not None:
        db_product.discount_percent = discount_percent
    if is_active is not None:
        db_product.is_active = is_active
    if image:
        db_product.image_url = save_images(image)

    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(id: int, db: Session = Depends(get_db), current_admin=Depends(check_is_admin)):
    db_product = db.query(Product).filter(Product.id == id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.is_active = False
    db.commit()
    return None
