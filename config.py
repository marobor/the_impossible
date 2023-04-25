
DB_NAME = "database.db"


class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = ""
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024
    UPLOAD_FOLDER = r'static\uploads'

    CKEDITOR_PKG_TYPE = 'basic'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = False
    UPLOAD_FOLDER = r'C:'


class TestingConfig(Config):
    TESTING = True
