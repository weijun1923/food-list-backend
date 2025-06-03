import os
from datetime import timedelta
from typing import Optional

basedir = os.path.abspath(os.path.dirname(__file__))



class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-key"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres.akaotykfvgucqeafbffv:ads101250101@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key"
    JWT_VERIFY_SUB = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION        = ["cookies"]     # 只從 cookie 讀寫 JWT
    JWT_COOKIE_CSRF_PROTECT   = True            # 開 CSRF 防護
    JWT_COOKIE_SAMESITE = "None"         # CSRF 防護設定
    JWT_COOKIE_SECURE = False         # 是否使用 HTTPS，開發時可設為 False
