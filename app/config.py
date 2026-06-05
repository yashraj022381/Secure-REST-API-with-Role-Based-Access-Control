import os
from datetime import timedelta


class BaseConfig:

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secre-change-in-production")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)


    BCRYPT_LOG_ROUNDS = 12

    ITEMS_PER_PAGE = 20



class DevelopmentConfig(BaseConfig):

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL",
        "postgresql://postgres:YOUR_PASSWORD@localhost:5432/secure_api_dev"
    )
    SQLALCHEMY_ECHO = True
    BCRYPT_LOG_ROUNDS = 4

    

class TestingConfig(BaseConfig):
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite///:memory:"
    BCRYPT_LOG_ROUNDS = 4
    WTF_CSRF_ENABLED = False

    

class ProductionConfig(BaseConfig):

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"


    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueErrror("❌ SECRET_KEY environment variable is not set!")

config_map{
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
