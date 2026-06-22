"""
Application Configuration
This file contains environment-specific configurations for the Flask application.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask Configuration
    FLASK_ENV = 'production'
    FLASK_APP = 'app.py'
    DEBUG = False
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Database Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///diabetes_predictor.db')
    
    # Model Configuration
    MODEL_PATH = 'diabetes-prediction-rfc-model.pkl'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'
    
    # CORS Configuration
    CORS_ORIGINS = ['*']
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # Supported Languages
    LANGUAGES = {
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'hi': 'हिंदी',
        'zh': '中文'
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SESSION_COOKIE_SECURE = False


# Load configuration based on environment
def get_config():
    """Load appropriate configuration based on FLASK_ENV"""
    flask_env = os.environ.get('FLASK_ENV', 'development')
    
    if flask_env == 'production':
        return ProductionConfig
    elif flask_env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
