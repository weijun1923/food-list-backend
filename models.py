import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, DateTime, UUID, func, NUMERIC,Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    __tablename__ = "users"  # 指定資料表名稱
    # 1. 主鍵 id
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), nullable=False)
    # 2. 使用者名稱，必填
    username: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True)
    # 4. 電子郵件，必填
    email: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True)
    # 3. 密碼，必填
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __init__(self, username: str, password: str, email: str):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Restaurant(db.Model):
    __tablename__ = "restaurant"  # 指定資料表名稱
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), nullable=False)
    restaurant_name: Mapped[str] = mapped_column(
        String(120), nullable=False, unique=True)  # 餐廳名稱，必填且唯一
    image_key: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        server_default="{}"  # 預設為空陣列
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )
    restaurant_menu: Mapped[list["RestaurantMenu"]] = relationship(
        "RestaurantMenu", back_populates="restaurant", lazy=True
    )
    def __init__(self, restaurant_name: str, image_key: str | None = None):
        self.restaurant_name = restaurant_name
        self.image_key = image_key 


class RestaurantMenu(db.Model):
    __tablename__ = "restaurant_menu"  # 指定資料表名稱
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), nullable=False)
    restaurant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), db.ForeignKey("restaurant.id"), nullable=False)
    restaurant: Mapped["Restaurant"] = relationship(
        "Restaurant", back_populates="restaurant_menu")
    image_keys: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(255)), 
        nullable=True,
        server_default="{}" 
    )
    dish_name: Mapped[str] = mapped_column(
        String(120), nullable=False)
    cuisine: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    rating: Mapped[Decimal] = mapped_column(
        NUMERIC(2, 1), nullable=True, default="0.0")
    menu_category: Mapped[str] = mapped_column(String(50), nullable=False)
    price:Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False
    )

    def __init__(
        self,
        restaurant_id: uuid.UUID,
        dish_name: str,
        cuisine: str,
        menu_category: str,
        image_keys: list[str] | None = None,
        rating: Decimal = Decimal("0.0"),
        price: int = 0
    ):  
        self.restaurant_id = restaurant_id
        self.dish_name = dish_name
        self.cuisine = cuisine
        self.menu_category = menu_category
        self.image_keys = image_keys or []
        self.rating = rating
        self.price = price


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"
    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(self, jti: str, created_at: datetime):
        self.jti = jti
        self.created_at = created_at
