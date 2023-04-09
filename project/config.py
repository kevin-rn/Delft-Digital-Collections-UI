import os
from pathlib import Path


class BaseConfig:
    """Base configuration"""
    BASE_DIR = Path(__file__).parent.parent

    TESTING = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}