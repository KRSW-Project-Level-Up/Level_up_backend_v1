# config.py

class Config(object):
    SECRET_KEY = 'ba619a2b23632506562cc8a082497a684d4a997a8ef7ce84'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///levelup.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Other general settings

class DevelopmentConfig(Config):
    DEBUG = True
    # Development specific settings

class TestingConfig(Config):
    TESTING = True
    # Testing specific settings

class ProductionConfig(Config):
    DEBUG = False
    # Production specific settings
