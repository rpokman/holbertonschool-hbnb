import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    DEBUG = False
    PEPPER = os.getenv('PEPPER', 'default_pepper_value')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hbnb_dev.db'

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
