from flask import Blueprint, render_template, current_app

from .models import Assignment

main = Blueprint('main', __name__)


@main.route('/')
def index():
    assignments = Assignment.query.order_by(Assignment.aid).all()
    return render_template('index.html',
                           assignments=assignments)
