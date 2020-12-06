from flask import Flask

from config import config

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    from . import db
    db.init_app(app)

    from . import docker_cli
    docker_cli.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .assignment import assignment as assigmnent_blueprint
    app.register_blueprint(assigmnent_blueprint)

    return app


    