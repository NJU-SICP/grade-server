import os
import re
import random

basedir = os.path.abspath(os.path.dirname(__file__))


def ok_extractor(result):
    p = re.compile(r"Score:\s*\n\s*Total:.*")
    score_str = p.findall(result)[0].split()[2]
    return int(round(float(score_str)))


def random_extractor(result):
    return random.randint(0, 100)


score_extractors = {
    'ok_extractor': ok_extractor,
    'random_extractor': random_extractor
}


class Config:
    APP_NAME = 'grade-server'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hard to guess string')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SCORE_EXTRACTORS = score_extractors

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class UnixConfig(ProductionConfig):

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'unix': UnixConfig,
    'default': DevelopmentConig
}
