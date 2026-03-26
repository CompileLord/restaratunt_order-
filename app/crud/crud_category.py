from sqlalchemy.orm import Session, joinedload, selectinload
from app.db.models import User, Category, Product




def create_category(db: Session, title:str, image_url: str, description: str = None):
    category = Category(title=title, description=description, image_url=image_url)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

def check_available_category(db: Session, title: str):
    found_category = db.query(Category).filter(Category.title==title).first()
    return found_category is not None

def update_product(db: Session, category_id: int, new_title: str, new_description: str, new_image_url: str):
    category = db.query(Category).filter(Category.id==category_id).first()
    category.title = new_title
    category.description = new_description
    category.image_url = new_image_url
    db.commit()
    db.refresh(category)
    return category

def get_by_id_category(db: Session, category_id: int):
    category = db.query(Category).options(selectinload(Category.products)).filter(Category.id==category_id).first()
    return category

def get_all_categories(db: Session):
    return db.query(Category).all()




