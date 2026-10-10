"""
Configuration management for Apartment Visit Management System (AVMS).
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'avms-secure-jwt-session-key-dev-default-3849102'
    
    # Database Settings
    DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite').lower()
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.join(BASE_DIR, 'instance', 'avms.db')
    
    # MySQL Settings (used if DB_ENGINE == 'mysql')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'avmsdb')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))

    # Session Security
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1')

    # Security & CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    DB_ENGINE = 'sqlite'
    DATABASE_PATH = ':memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-12345'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
