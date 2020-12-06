import docker

from flask import g


def get_docker_cli():
    if 'docker_cli' not in g:
        g.docker_cli = docker.from_env()
    return g.docker_cli


def close_docker_cli(e=None):
    docker_cli = g.pop('docker_cli', None)

    if docker_cli is not None:
        docker_cli.close()


def init_app(app):
    app.teardown_appcontext(close_docker_cli)
