import csv

from . import db


class Student(db.Model):
    __tablename__ = 'students'

    stuid = db.Column(db.String(16), primary_key=True)
    stuname = db.Column(db.String, nullable=False)
    scores = db.relationship('Score',
                             backref=db.backref('student'),
                             lazy=True)

    @staticmethod
    def import_teaching_assistant():
        db.session.add(Student(stuid='TAs', stuname='TAs'))
        db.session.commit()

    @staticmethod
    def import_from_csv(file):
        with open(file, 'r', encoding='utf-8') as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                db.session.add(Student(stuid=row[0], stuname=row[1]))
        db.session.commit()

    @staticmethod
    def has_student(stuid):
        return Student.query.filter_by(stuid=stuid).first() is not None


class Assignment(db.Model):
    __tablename__ = 'assignments'

    aid = db.Column(db.Integer, primary_key=True)
    aname = db.Column(db.String, nullable=False)
    grader_image = db.Column(db.String, nullable=False)
    ddl = db.Column(db.DateTime, nullable=False)
    timeout = db.Column(db.Integer, nullable=False)
    score_extractor = db.Column(db.String, nullable=False)
    required_files = db.relationship('RequiredFile',
                                     backref=db.backref('assignment'),
                                     lazy=True,
                                     cascade='all, delete-orphan')
    scores = db.relationship('Score',
                             backref=db.backref('assignment'),
                             lazy=True)

    @staticmethod
    def has_assignment(aname):
        return Assignment.query.filter_by(aname=aname).first() is not None

    @staticmethod
    def add_or_update_assignment(new_assignment):
        assignment = Assignment.query.filter_by(
            aname=new_assignment.aname).first()
        if assignment:
            assignment.ddl = new_assignment.ddl
            assignment.timeout = new_assignment.timeout
            db.session.commit()
        else:
            db.session.add(new_assignment)
            db.session.commit()

    @staticmethod
    def export_scores_to_csv(aname, file):
        assignment = Assignment.query.filter_by(aname=aname).one()
        with open(file, 'w')as f:
            f_csv = csv.writer(f)
            for record in assignment.scores:
                f_csv.writerow([record.stuid, record.score])


class RequiredFile(db.Model):
    __tablename__ = 'required_files'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    container_path = db.Column(db.String, nullable=False)
    aid = db.Column(db.Integer, db.ForeignKey('assignments.aid'),
                    nullable=False)


class Score(db.Model):
    __tablename__ = 'scores'

    aid = db.Column(db.Integer, db.ForeignKey('assignments.aid'),
                    primary_key=True)
    stuid = db.Column(db.Integer, db.ForeignKey('students.stuid'),
                      primary_key=True)
    score = db.Column(db.Integer, nullable=False)

    @staticmethod
    def add_or_update_score(aid, stuid, new_score):
        record = Score.query.filter_by(aid=aid, stuid=stuid).first()
        if record:
            if new_score > record.score:
                record.score = new_score
                db.session.commit()
        else:
            db.session.add(Score(aid=aid, stuid=stuid, score=new_score))
            db.session.commit()
