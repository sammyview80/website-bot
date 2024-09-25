from dotenv import load_dotenv
import os
import redis

load_dotenv()

class ApplicationConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url('redis://localhost:6379')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    # SESSION_COOKIE_SECURE = True
    # SESSION_COOKIE_HTTPONLY = True
    # SESSION_COOKIE_SAMESITE = 'None'
    # SESSION_COOKIE_DOMAIN = None
    # SESSION_COOKIE_PATH = '/'
    