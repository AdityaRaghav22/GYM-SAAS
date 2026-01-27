import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "postgresql://gym_saas_user:xHWJYc8vNh4eITlHEGmKFEq3s5Nqi0vE@dpg-d5s9g615pdvs739h8ds0-a/gym_saas"
    )
