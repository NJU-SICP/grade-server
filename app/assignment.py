from datetime import datetime

from flask import (Blueprint, current_app, redirect,
                   render_template, request, url_for)

from .db import get_db
from .docker_cli import get_docker_cli
from .docker_utils import grade

assignment = Blueprint("assignment", __name__, url_prefix='/assignment')


@assignment.route('/<aname>/submit', methods=['POST'])
def submit(aname):
    assignments = current_app.config['ASSIGNMENTS']
    if aname not in assignments:
        return f'Invalid assignment: {aname}.', 400
    assignment_config = assignments[aname]

    ddl = assignment_config['ddl']
    if datetime.now() > ddl:
        return f'Sorry, you have exceeded the deadline, which is {ddl}.', 200

    if 'stuid' not in request.form:
        return 'Student ID not found.', 400
    stuid = request.form['stuid']
    if not is_valid_stuid(stuid):
        return f'Invalid student ID: {stuid}.', 400

    required_files_map = assignment_config['required_files']
    for required_filename in required_files_map:
        if required_filename not in request.files:
            return f"Missing {required_filename} in submission.", 400

    cli = get_docker_cli()
    grader = None
    try:
        grader = cli.containers.create(assignment_config['grader_image'])
        result = grade(grader, request.files, required_files_map,
                       assignment_config['timeout'])
    except Exception as e:
        return str(e), 500
    finally:
        if grader:
            try:
                grader.remove(force=True)
            except Exception:
                pass

    score = assignment_config['score_extractor'](result)
    save_score(stuid, aname, score)
    return result, 200


def is_valid_stuid(stuid):
    db = get_db()
    return db.execute(
        "select stuid from students where stuid = ?", (stuid,)
    ).fetchone() is not None


def save_score(stuid, aname, score):
    db = get_db()
    if has_score(stuid, aname):
        print("update:", stuid, aname, score)
        db.execute(
            """update scores set score = ?
            where stuid = ? and assignment = ?""",
            (score, stuid, aname))
    else:
        print("insert:", stuid, aname, score)
        db.execute(
            """insert into scores (stuid, assignment, score)
            values (?, ?, ?)""", (stuid, aname, score))
    db.commit()


def has_score(stuid, aname):
    db = get_db()
    return db.execute(
        'select stuid from scores where stuid = ? and assignment = ?',
        (stuid, aname)
    ).fetchone() is not None


@assignment.route('/<aname>/status', methods=['GET'])
def status(aname):
    db = get_db()
    scores = db.execute(
        "select stuid, score from scores where assignment = ?",
        (aname, )).fetchall()
    return render_template('assignment/status.html', aname=aname, scores=scores)
