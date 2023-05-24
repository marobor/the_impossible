
DB_NAME = "database.db"


class Config(object):
    DEBUG = False
    TESTING = False

    SECRET_KEY = ",¦!©Îç4Kï'@0#yð¼9+,²ñF"
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_NAME}'
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024
    UPLOAD_FOLDER = r'static\uploads'

    CKEDITOR_PKG_TYPE = 'basic'


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = False
    UPLOAD_FOLDER = r'C:\Users\Marek\Documents\studia\3r2s\flaskProject\website\static\uploads'


class TestingConfig(Config):
    TESTING = True
