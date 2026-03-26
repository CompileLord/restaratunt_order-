from sqlalchemy.orm import Session, joinedload, selectinload
from app.db.models import User, Category, Product


def create_product(title: str, price: float, image_url: str, db: Session, category: int, discount_percent: int = None, description: str = None):
    new_product = Product(title=title, price=price, image_url=image_url, discount_percent=discount_percent, description=description, category_id = category)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

def check_available_product(db: Session, title: str):
    product_found = db.query(Product).filter(Product.title==title).first()
    return product_found if product_found else None

def get_by_id(product_id, db: Session):
    product = db.query(Product).filter(Product.id==product_id).first()
    return product

def get_all_products(db: Session):
    products = db.query(Product).all()
    return products


def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id==product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return "Success"
    return None

def update_product(new_title: str, new_price: float, new_image_url: str, new)
        

