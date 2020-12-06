import os
from datetime import datetime

import docker

basedir = os.path.abspath(os.path.dirname(__file__))


def always_full_total(logs):
    return 100


assignments = {
    'test-proj': {
        'grader_image': 'sicp-test-proj-env',
        'required_files': {
            'hw06.scm': '/usr/src/test-proj'
        },
        'ddl': datetime(2020, 12, 6, 23, 59, 59),
        'timeout': 10,
        'score_extractor': always_full_total,
    }
}


def check_assignment_config(assignment):
    required_attrs = ['grader_image', 'required_files',
                      'ddl', 'timeout', 'score_extractor']
    for attr in required_attrs:
        if attr not in assignment:
            raise ValueError(
                f"Config Error: required attribute '{attr}' not found.")

    client = docker.client.from_env()
    try:
        client.images.get(assignment['grader_image'])
    finally:
        client.close()


class Config:
    APP_NAME = 'grade-server'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hard to guess string')
    ASSIGNMENTS = assignments

    @staticmethod
    def init_app(app):
        # Self-check before initiating any app.
        Config.self_check()

    @staticmethod
    def self_check():
        for assigment in Config.ASSIGNMENTS.values():
            check_assignment_config(assigment)


class DevelopmentConig(Config):
    DEBUG = True
    DATABASE = os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    DATABASE = os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    DATABASE = os.path.join(basedir, 'data.sqlite')


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
