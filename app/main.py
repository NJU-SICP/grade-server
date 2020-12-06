from app import assignment
from flask import Blueprint, render_template, current_app

main = Blueprint('main', __name__)


@main.route('/')
def index():
    anames = [ name for name in current_app.config['ASSIGNMENTS']]
    return render_template('index.html', anames=anames)
