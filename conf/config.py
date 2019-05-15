import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret'
    DB_HOST = '127.0.0.1'
    DB_USER = 'root'
    DB_PASSWD = ''
    DB_DATABASE = 'webadmin'
    ITEMS_PER_PAGE = 10
    JWT_AUTH_URL_RULE = '/api/auth'
    UPLOAD_FOLDER = 'D://codes/PycharmWorkSpace/temp'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    PRODUCTION = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}