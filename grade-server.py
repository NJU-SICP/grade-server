import os
from datetime import datetime
import json

import click
import docker

from app import create_app, db
from app.models import Assignment, RequiredFile, Student
from config import score_extractors

app = create_app(os.getenv('APP_CONFIG') or 'default')


@app.cli.command()
def init_db():
    """Clear the existing data and create new tables."""
    db.create_all()
    Student.import_teaching_assistant()
    click.echo('Initialized the database.')


@app.cli.command()
@click.argument('file')
def import_students(file):
    """Import enrolled student infomation."""
    Student.import_from_csv(file)


@app.cli.command()
@click.argument('file')
def add_assignment(file):
    """Add an assignment from configuration file."""
    with open(file, 'r', encoding='utf-8') as f:
        obj = json.load(f)

    Assignment.add_or_update_assignment(create_assignment(obj))


@app.cli.command()
@click.argument('file')
def update_assignment(file):
    """Update an assignment from configuration file."""
    with open(file, 'r', encoding='utf-8') as f:
        obj = json.load(f)

    Assignment.add_or_update_assignment(create_assignment(obj))


def create_assignment(obj):
    check_assignment(obj)
    assignment = Assignment(
        aname=obj['name'], grader_image=obj['grader_image'],
        ddl=datetime.strptime(obj['ddl'], '%Y-%m-%d %H:%M:%S'),
        timeout=obj['timeout'], score_extractor=obj['score_extractor'])
    for sub_obj in obj['required_files']:
        required_file = RequiredFile(
            filename=sub_obj['filename'],
            container_path=sub_obj['container_path'])
        assignment.required_files.append(required_file)
    return assignment


def check_assignment(obj):
    required_attrs = ['name', 'grader_image', 'required_files',
                      'ddl', 'timeout', 'score_extractor']
    for attr in required_attrs:
        if attr not in obj:
            raise ValueError(
                f"Config Error: required attribute '{attr}' not found.")

    for required_file in obj['required_files']:
        for attr in ['filename', 'container_path']:
            if attr not in required_file:
                raise ValueError(
                    f"Config Error: required attribute '{attr}' not found.")

    score_extractor = obj['score_extractor']
    if score_extractor not in score_extractors:
        raise ValueError(
            f"Config Error: score extractor '{score_extractor}' not found.")

    client = docker.client.from_env()
    try:
        client.images.get(obj['grader_image'])
    finally:
        client.close()


@app.cli.command()
@click.option('--aname', '-a', help='which assignment.')
@click.argument('file')
def export_scores(aname, file):
    """export scores of an assignment."""
    Assignment.export_scores_to_csv(aname, file)
