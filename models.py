from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    __tablename__ = "user"  # 指定資料表名稱
    # 1. 主鍵 id
    id: Mapped[int] = mapped_column(primary_key=True)
    # 2. 使用者名稱，必填
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    # 4. 電子郵件，必填
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    # 3. 密碼，必填
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    def __init__(self, username: str, password: str, email: str):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class Restaurant(db.Model):
    __tablename__ = "restaurant"  # 指定資料表名稱
    # 6. 主鍵 id
    id: Mapped[int] = mapped_column(primary_key=True)
    # 7. 餐廳名稱，必填
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # 8. 圖片網址，可為空
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # 9. 簡短描述，可為空
    short_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # 10. 是否已上架，預設 false
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    # 11. 建立時間，預設為現在
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __init__(
        self,
        name: str,
        image_url: str | None = None,
        short_description: str | None = None,
        is_published: bool = False,
    ):
        self.name = name
        self.image_url = image_url
        self.short_description = short_description
        self.is_published = is_published
        self.created_at = datetime.now()
