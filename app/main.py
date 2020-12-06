from app import assignment
from flask import Blueprint, render_template, current_app

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html',
                           assignments=current_app.config['ASSIGNMENTS'])
