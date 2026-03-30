# Restaurant Order System API / Системы Заказа Ресторана

[English](#english) | [Русский](#русский)

---

<a name="english"></a>
## English

### Project Overview
This is a robust backend system for a restaurant ordering platform, built with **FastAPI**. It handles everything from user authentication to product categorization, shopping cart management, and order processing.

### ✨ Features
- **User Authentication**: Secure login and registration using JWT (JSON Web Tokens) with token blacklisting support.
- **Role-Based Access**: Specialized permissions for **Admin** and **User** roles.
- **Category Management**: Organize products into customizable categories with image support.
- **Product Management**: Full CRUD operations for menu items, including ingredients, pricing, and discounts.
- **Shopping Cart**: Real-time management of user carts.
- **Order Processing**: Create and track orders with multiple statuses (New, Preparing, Delivering, Completed, Cancelled).
- **Reviews & Ratings**: Customer feedback system for products.
- **Static Assets**: Integration for serving frontend files and images.

### 🛠 Tech Stack
- **Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Migrations**: Alembic
- **Security**: JWT, Argon2 (Passlib)
- **Validation**: Pydantic

### 🚀 Getting Started

#### 1. Prerequisites
- Python 3.8+
- Virtual environment (recommended)

#### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd exam2

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy alembic passlib[argon2] PyJWT python-dotenv python-multipart
```

#### 3. Configuration
Copy the template environment file and update the `SECRET_KEY`:
```bash
cp .env.example .env
```

#### 4. Database Setup
Run migrations to create the database schema:
```bash
alembic upgrade head
```

#### 5. Running the Project
Start the development server:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

### 📖 API Documentation
Once the server is running, you can access the interactive documentation at:
- **Swagger UI**: [http://127.0.0.1:8002/docs](http://127.0.0.1:8002/docs)
- **Redoc**: [http://127.0.0.1:8002/redoc](http://127.0.0.1:8002/redoc)

---

<a name="русский"></a>
## Русский

### Обзор проекта
Это надежная серверная система для платформы заказа еды в ресторане, построенная на **FastAPI**. Она управляет всем: от аутентификации пользователей до категоризации продуктов, управления корзиной и обработки заказов.

### ✨ Возможности
- **Аутентификация пользователей**: Безопасный вход и регистрация с использованием JWT (JSON Web Tokens) и поддержкой черного списка токенов.
- **Ролевой доступ**: Разграничение прав для ролей **Администратор** и **Пользователь**.
- **Управление категориями**: Организация продуктов по настраиваемым категориям с поддержкой изображений.
- **Управление продуктами**: Полный цикл операций (CRUD) для позиций меню, включая ингредиенты, цены и скидки.
- **Корзина покупок**: Управление корзинами пользователей в реальном времени.
- **Обработка заказов**: Создание и отслеживание заказов с различными статусами (Новый, Готовится, Доставляется, Завершен, Отменен).
- **Отзывы и рейтинги**: Система обратной связи от клиентов для каждого продукта.
- **Статические файлы**: Интеграция для раздачи файлов фронтенда и изображений.

### 🛠 Технологический стек
- **Фреймворк**: FastAPI
- **База данных**: SQLite (SQLAlchemy ORM)
- **Миграции**: Alembic
- **Безопасность**: JWT, Argon2 (Passlib)
- **Валидация**: Pydantic

### 🚀 Как начать

#### 1. Предварительные требования
- Python 3.8+
- Виртуальное окружение (рекомендуется)

#### 2. Установка
```bash
# Клонируйте репозиторий
git clone <repository-url>
cd exam2

# Создайте и активируйте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate

# Установите зависимости
pip install fastapi uvicorn sqlalchemy alembic passlib[argon2] PyJWT python-dotenv python-multipart
```

#### 3. Настройка
Скопируйте шаблон файла окружения и обновите `SECRET_KEY`:
```bash
cp .env.example .env
```

#### 4. Настройка базы данных
Запустите миграции для создания схемы базы данных:
```bash
alembic upgrade head
```

#### 5. Запуск проекта
Запустите сервер для разработки:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

### 📖 Документация API
После запуска сервера интерактивная документация доступна по адресам:
- **Swagger UI**: [http://127.0.0.1:8002/docs](http://127.0.0.1:8002/docs)
- **Redoc**: [http://127.0.0.1:8002/redoc](http://127.0.0.1:8002/redoc)
