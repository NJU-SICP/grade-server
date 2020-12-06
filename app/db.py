import csv
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(import_students)
    app.cli.add_command(export_scores)


@click.command('import-students')
@click.argument('file')
@with_appcontext
def import_students(file):
    """Import enrolled student infomation."""
    db = get_db()
    with open(file, 'r', encoding='utf-8') as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            db.execute(
                "insert into students (stuid, stuname) values (?, ?)",
                (row[0], row[1]))
    db.commit()


@click.command('export-scores')
@click.option('--aname', '-a', help='which assignment.')
@click.argument('file')
@with_appcontext
def export_scores(aname, file):
    db = get_db()
    with open(file, 'w')as f:
        f_csv = csv.writer(f)
        scores = db.execute(
            'select stuid, score from scores where assignment = ?',
            (aname, )).fetchall()
        f_csv.writerows(scores)
