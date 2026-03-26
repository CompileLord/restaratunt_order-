



Ниже представлено расширенное и профессионально оформленное Техническое Задание (ТЗ) для разработки backend-части платформы заказа еды. Оно адаптировано под стек **FastAPI, SQLAlchemy, SQLite, Pydantic, Alembic и JWT**.

---

# Техническое задание (ТЗ): Backend для онлайн‑платформы заказа еды

## 1. Общая информация и стек технологий
**Название проекта:** REST API для онлайн‑платформы заказа еды.
**Цель проекта:** Создать надежный, быстрый и масштабируемый backend для управления каталогом блюд, корзиной, заказами и пользователями.

**Технологический стек:**
*   **Фреймворк:** FastAPI (Python 3.10+)
*   **База данных:** SQLite (для MVP и разработки с возможностью легкого перехода на PostgreSQL)
*   **ORM:** SQLAlchemy 2.0 (async/sync)
*   **Миграции:** Alembic
*   **Валидация и сериализация:** Pydantic V2
*   **Аутентификация:** JWT (JSON Web Tokens), пароли хэшируются через Passlib (bcrypt)

---

## 2. Архитектура проекта (Структура папок)

Проект строится по принципам чистой архитектуры, разделяя роуты, бизнес-логику и работу с БД.

```text
food_delivery_api/
├── alembic/                # Файлы миграций базы данных
├── alembic.ini             # Конфигурация Alembic
├── app/
│   ├── main.py             # Точка входа приложения (создание FastAPI app)
│   ├── api/                # Роутеры (Endpoints)
│   │   ├── dependencies.py # Зависимости (например, get_db, get_current_user)
│   │   ├── routers/        # Разделение роутов по доменам
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── categories.py
│   │   │   ├── products.py
│   │   │   ├── cart.py
│   │   │   ├── orders.py
│   │   │   └── reviews.py
│   ├── core/               # Ядро (Конфигурации, безопасность)
│   │   ├── config.py       # Pydantic BaseSettings (чтение .env)
│   │   └── security.py     # Логика хэширования паролей и создания JWT
│   ├── db/                 # Настройки БД
│   │   ├── database.py     # Инициализация engine и sessionmaker
│   │   └── base.py         # Подключение всех моделей для Alembic
│   ├── models/             # SQLAlchemy модели (таблицы в БД)
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── ...
│   ├── schemas/            # Pydantic модели (схемы запросов и ответов)
│   │   ├── user.py
│   │   ├── product.py
│   │   └── ...
│   └── crud/               # Изолированная логика работы с БД (Create, Read, Update, Delete)
│       ├── crud_user.py
│       ├── crud_product.py
│       └── ...
├── requirements.txt
└── .env                    # Секретные ключи, URL БД
```

---

## 3. Схемы Базы Данных (SQLAlchemy Модели)

Все модели наследуются от `Base` (DeclarativeBase).

### 3.1. `User` (Пользователи)
*   `id`: Integer, Primary Key, AutoIncrement
*   `email`: String(255), Unique, Indexed, Not Null
*   `hashed_password`: String, Not Null
*   `full_name`: String, Not Null
*   `phone`: String(20), Unique, Nullable
*   `role`: Enum ('user', 'admin'), Default: 'user'
*   `created_at`: DateTime, Default: func.now()

### 3.2. `Category` (Категории)
*   `id`: Integer, PK
*   `name`: String(100), Unique, Not Null
*   `description`: Text, Nullable

### 3.3. `Product` (Блюда)
*   `id`: Integer, PK
*   `name`: String(150), Indexed, Not Null
*   `description`: Text, Not Null
*   `price`: Float (или Integer в копейках), Not Null
*   `image_url`: String(255), Nullable
*   `ingredients`: Text, Nullable
*   `category_id`: Integer, ForeignKey('category.id')
*   `is_active`: Boolean, Default: True (для скрытия из меню вместо удаления)
*   `discount_percent`: Integer, Default: 0

### 3.4. `CartItem` (Корзина)
*   `id`: Integer, PK
*   `user_id`: Integer, ForeignKey('user.id')
*   `product_id`: Integer, ForeignKey('product.id')
*   `quantity`: Integer, Default: 1

### 3.5. `Order` (Заказы)
*   `id`: Integer, PK
*   `user_id`: Integer, ForeignKey('user.id')
*   `status`: Enum ('new', 'preparing', 'delivering', 'completed', 'cancelled'), Default: 'new'
*   `total_amount`: Float, Not Null
*   `payment_method`: Enum ('cash', 'card'), Not Null
*   `delivery_address`: Text, Not Null
*   `created_at`: DateTime, Default: func.now()

### 3.6. `OrderItem` (Позиции в заказе)
*   `id`: Integer, PK
*   `order_id`: Integer, ForeignKey('order.id')
*   `product_id`: Integer, ForeignKey('product.id')
*   `quantity`: Integer, Not Null
*   `price_per_item`: Float, Not Null (сохраняем цену на момент покупки)

### 3.7. `Review` (Отзывы)
*   `id`: Integer, PK
*   `user_id`: Integer, ForeignKey('user.id')
*   `product_id`: Integer, ForeignKey('product.id')
*   `rating`: Integer (1-5), Not Null
*   `comment`: Text, Nullable
*   `created_at`: DateTime, Default: func.now()

---

## 4. Схемы Pydantic (Примеры)

Используются для валидации данных, приходящих от клиента, и форматирования ответов.

```python
# schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    category_id: int
    image_url: Optional[str] = None
    ingredients: Optional[str] = None
    discount_percent: int = Field(default=0, ge=0, le=100)

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    
    model_config = {"from_attributes": True} # Замена orm_mode=True в Pydantic v2
```

---

## 5. Полное описание Endpoints (API Маршруты)

### 5.1. Аутентификация (`/auth`)
| Метод | Эндпоинт | Доступ | Описание |
| :--- | :--- | :--- | :--- |
| **POST** | `/auth/register` | Все | Регистрация нового пользователя (Body: `UserCreate`) |
| **POST** | `/auth/login` | Все | Получение JWT токена (Body: OAuth2PasswordRequestForm, Возвращает `access_token`) |

### 5.2. Пользователи (`/users`)
| Метод | Эндпоинт | Доступ | Описание |
| :--- | :--- | :--- | :--- |
| **GET** | `/users/me` | Auth | Получить информацию о себе |
| **PUT** | `/users/me` | Auth | Обновить профиль (телефон, имя) |
| **GET** | `/users/` | Admin | Получить список всех пользователей (с пагинацией) |
| **PATCH**| `/users/{id}/role` | Admin | Изменить роль пользователя |

### 5.3. Категории (`/categories`)
| Метод | Эндпоинт | Доступ | Описание |
| :--- | :--- | :--- | :--- |
| **GET** | `/categories/` | Все | Список категорий |
| **POST** | `/categories/` | Admin | Создать категорию |
| **PUT** | `/categories/{id}` | Admin | Обновить категорию |
| **DELETE**| `/categories/{id}` | Admin | Удалить категорию |

### 5.4. Блюда / Каталог (`/products`)
| Метод | Эндпоинт | Доступ | Описание |
| :--- | :--- | :--- | :--- |
| **GET** | `/products/` | Все | Список блюд. *Query-параметры:* `category_id`, `search` (по имени), `min_price`, `max_price`, `sort_by` |
| **GET** | `/products/{id}` | Все | Подробная информация о блюде |
| **POST** | `/products/` | Admin | Добавить новое блюдо |
| **PUT** | `/products/{id}` | Admin | Изменить данные блюда |
| **DELETE**| `/products/{id}`| Admin | Деактивировать (или удалить) блюдо |

### 5.5. Корзина (`/cart`)
| Метод | Эндпоинт | Доступ | Описание |
| :--- | :--- | :--- | :--- |
| **GET** | `/cart/` | Auth | Получить содержимое корзины пользователя |
| **POST** | `/cart/` | Auth | Добавить блюдо в корзину (Body: `product_id`, `quantity`) |
| **PUT** | `/cart/{item_id}`| Auth | Изменить количество блюда в корзине |
| **DELETE**| `/cart/{item_id}`| Auth | Удалить блюдо из корзины |
| **DELETE**| `/cart/clear` | Auth | Полностью очистить корзину |

### 5.6. Заказы (`/orders`)
| Метод | Эндпоинт | Доступ | Описание |
| :--- | :--- | :--- | :--- |
| **POST** | `/orders/` | Auth | Оформить заказ (собирает данные из корзины, Body: `delivery_address`, `payment_method`). Корзина после этого очищается. |
| **GET** | `/orders/` | Auth | История заказов текущего пользователя |
| **GET** | `/orders/{id}` | Auth | Детали конкретного заказа |
| **GET** | `/admin/orders` | Admin | Получить список всех заказов системы (фильтры по статусу) |
| **PATCH**| `/admin/orders/{id}`| Admin | Изменить статус заказа (напр. `new` -> `preparing`) |

### 5.7. Отзывы (`/reviews`)
| Метод | Эндпоинт | Доступ | Описание |
| :--- | :--- | :--- | :--- |
| **GET** | `/products/{id}/reviews`| Все | Получить отзывы к конкретному блюду |
| **POST** | `/products/{id}/reviews`| Auth | Оставить отзыв (только если пользователь заказывал это блюдо) |

---

## 6. Требования к безопасности
1. **Хеширование паролей**: Никакие пароли не хранятся в открытом виде. Использовать `passlib[bcrypt]`.
2. **JWT-токены**:
   - Токен выдается на определенное время (например, 30 минут для `access_token` и 7 дней для `refresh_token` — если требуется реализация refresh).
   - При проверке токена (`get_current_user`) достается `id` пользователя и проверяется его существование в БД.
3. **Разграничение прав (RBAC)**:
   - Зависимость `get_current_admin_user`, которая вызывает `get_current_user` и проверяет `user.role == "admin"`. В случае ошибки возвращает `HTTP 403 Forbidden`.
4. **CORS**: Настроить `CORSMiddleware` в FastAPI для разрешения запросов с frontend-домена.

---

## 7. Логика работы некоторых функций
*   **Оформление заказа:** При POST `/orders/` backend должен:
    1. Найти все `CartItem` для `user_id`.
    2. Проверить актуальность цен в таблице `Product`.
    3. Посчитать `total_amount`.
    4. Создать запись `Order`.
    5. Скопировать `CartItem` в `OrderItem`, сохранив текущую цену блюда в `price_per_item`.
    6. Удалить все записи из `CartItem` для этого пользователя.
*   **Пагинация:** Все списочные GET-запросы (`/products/`, `/orders/`) должны принимать query-параметры `skip: int = 0` и `limit: int = 100`.

---

## 8. Нефункциональные требования
1. **Документация:** FastAPI автоматически генерирует Swagger UI (`/docs`) и ReDoc (`/redoc`). Все роуты должны иметь понятные `summary`, `description` и Pydantic-схемы для ответов (`response_model`).
2. **База данных:** SQLite поддерживает конкурентное чтение, но блокируется при записи. Для MVP этого достаточно. Для продакшена в файле `.env` достаточно будет поменять строку подключения SQLite на PostgreSQL.
3. **Миграции:** Любое изменение структуры таблиц должно производиться только через генерацию новых миграций Alembic (`alembic revision --autogenerate`).

---

## 9. Критерии приёмки (Backend)
1. Код запускается командой `uvicorn app.main:app --reload` без ошибок.
2. База данных и таблицы успешно создаются через `alembic upgrade head`.
3. Все заявленные Endpoint'ы работают в Swagger UI (`/docs`).
4. Авторизация по JWT работает корректно: неавторизованные пользователи получают 401 ошибку при попытке добавить товар в корзину; обычные пользователи получают 403 ошибку при попытке зайти в админские роуты.
5. Реализован полный цикл заказа: Регистрация -> Добавление в корзину -> Оформление заказа -> Просмотр истории -> Изменение статуса админом.