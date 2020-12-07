
from datetime import datetime

from flask import Blueprint, render_template, request, current_app

from . import db
from .docker_cli import get_docker_cli
from .docker_utils import grade
from .models import Assignment, Score, Student

assignment = Blueprint("assignment", __name__, url_prefix='/assignment')


@assignment.route('/<aname>/submit', methods=['POST'])
def submit(aname):
    assignment = Assignment.query.filter_by(aname=aname).first()
    if not assignment:
        return f"Assignment '{aname}' doesn't exist.", 400

    if datetime.now() > assignment.ddl:
        return 'Sorry, you have exceeded the deadline, ' + \
            f'which is {assignment.ddl}.', 200

    if 'stuid' not in request.form:
        return 'Student ID not found.', 400
    stuid = request.form['stuid']
    if not Student.has_student(stuid):
        return f'Invalid student ID: {stuid}.', 200

    required_files = assignment.required_files
    print(required_files)
    for required_file in required_files:
        if required_file.filename not in request.files:
            return f"Missing {required_file.filename} in submission.", 400

    cli = get_docker_cli()
    grader = None
    try:
        grader = cli.containers.create(assignment.grader_image)
        result = grade(grader, request.files,
                       required_files, assignment.timeout)
    except Exception as e:
        return str(e), 500
    finally:
        if grader:
            try:
                grader.remove(force=True)
            except Exception:
                pass

    score_extractor = current_app.config['SCORE_EXTRACTORS'][assignment.score_extractor]
    score = score_extractor(result)
    Score.add_or_update_score(assignment.aid, stuid, score)

    return result, 200


@assignment.route('/<aname>/status', methods=['GET'])
def status(aname):
    assignment = Assignment.query.filter_by(aname=aname).first()
    if not assignment:
        return f"Assignment '{aname}' doesn't exist.", 400

    return render_template('assignment/status.html', aname=aname, scores=assignment.scores)
