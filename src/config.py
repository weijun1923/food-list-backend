import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SUPABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True
    }
    
    # 重要：統一 JWT Secret Key 名稱
    JWT_SECRET_KEY = os.getenv("JWT_SECRET")
    JWT_VERIFY_SUB = False
    JWT_ALGORITHM = "HS256"  
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SECURE = True  # 開發環境設為 False
    JWT_ACCESS_COOKIE_NAME = "access_token"   
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    
    # 修正：本地開發使用 "Lax"，生產環境使用 "None"
    JWT_COOKIE_SAMESITE = "None"  # 本地開發時使用 "Lax"
    # JWT_COOKIE_SAMESITE = "None"  # 生產環境且使用 HTTPS 時使用 "None"
    
    # 新增：設定 cookie 的域名和路徑
    JWT_COOKIE_DOMAIN = None  # 本地開發時設為 None
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/"