import sys
import os
from pathlib import Path

# Add project root to path so we can import app modules
path_to_exam2 = Path(__file__).resolve().parent.parent.parent
if str(path_to_exam2) not in sys.path:
    sys.path.insert(0, str(path_to_exam2))

from app.db.database import SessionLocal, engine
from app.db.models import User, Role, Category, Product, AbstractBase
from app.core.security import hash_password

def seed_data():
    db = SessionLocal()
    try:
        # Create schema if it doesn't exist (just in case)
        AbstractBase.metadata.create_all(bind=engine)

        # 1. Create Admin
        admin_email = "admin_new@main.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            hashed_pw = hash_password("admin_pass123")
            admin = User(
                email=admin_email,
                password=hashed_pw,
                full_name="New Super Admin",
                phone="0987654321",
                role=Role.ADMIN
            )
            db.add(admin)
            db.flush()
            print(f"Created new admin: {admin_email} / admin_pass123")
        else:
            print("Admin already exists.")

        # 2. Create 6 Categories
        categories_data = [
            {"title": "Italian", "description": "Delicious pasta and pizza", "image_url": "https://images.unsplash.com/photo-1498579150354-977475b7e8b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            {"title": "Japanese", "description": "Authentic sushi and ramen", "image_url": "https://images.unsplash.com/photo-1553621042-f6e147245754?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            {"title": "Mexican", "description": "Tacos, burritos and more", "image_url": "https://images.unsplash.com/photo-1565299507177-b0ac66763828?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            {"title": "Indian", "description": "Spicy curries and naan bread", "image_url": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            {"title": "American", "description": "Burgers, fries and comfort food", "image_url": "https://images.unsplash.com/photo-1550547660-d9450f859349?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            {"title": "Healthy", "description": "Fresh salads and grain bowls", "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
        ]

        cats = []
        for c_data in categories_data:
            cat = db.query(Category).filter(Category.title == c_data["title"]).first()
            if not cat:
                cat = Category(**c_data)
                db.add(cat)
                db.flush()
            cats.append(cat)
        
        print(f"Seeded {len(cats)} categories.")

        # 3. Create 7 Products
        products_data = [
            # 1 Italian
            {"title": "Margherita Pizza", "description": "Classic Neapolitan pizza with fresh mozzarella and basil", "price": 14.99, "category_id": cats[0].id, "image_url": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            # 2 Japanese
            {"title": "Spicy Tuna Roll", "description": "Fresh tuna, spicy mayo, cucumber, wrapped in rice and nori", "price": 12.50, "category_id": cats[1].id, "image_url": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            # 3 Mexican
            {"title": "Beef Street Tacos", "description": "Three authentic street tacos with grilled beef, cilantro, and onion", "price": 9.99, "category_id": cats[2].id, "image_url": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            # 4 Indian
            {"title": "Chicken Tikka Masala", "description": "Roasted marinated chicken chunks in spiced curry sauce", "price": 16.00, "category_id": cats[3].id, "image_url": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            # 5 American
            {"title": "Double Cheeseburger", "description": "Two juicy beef patties with cheddar cheese, lettuce, and tomato", "price": 11.50, "category_id": cats[4].id, "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            # 6 Healthy
            {"title": "Quinoa Green Salad", "description": "Nutrient-packed salad with quinoa, kale, avocado, and lemon vinaigrette", "price": 13.00, "category_id": cats[5].id, "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
            # 7 Italian (Extra)
            {"title": "Spaghetti Carbonara", "description": "Traditional Roman pasta dish with eggs, cheese, pancetta, and black pepper", "price": 15.50, "category_id": cats[0].id, "image_url": "https://images.unsplash.com/photo-1612874742237-6526221588e3?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"},
        ]

        prods = 0
        for p_data in products_data:
            prod = db.query(Product).filter(Product.title == p_data["title"]).first()
            if not prod:
                prod = Product(**p_data)
                db.add(prod)
                prods += 1
        
        db.commit()
        print(f"Seeded {prods} new products.")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
