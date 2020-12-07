import csv

from . import db


class Student(db.Model):
    __tablename__ = 'students'

    stuid = db.Column(db.String(16), primary_key=True)
    stuname = db.Column(db.String(64), nullable=False)
    scores = db.relationship('Score',
                             backref=db.backref('student'),
                             lazy=True)

    def is_enrolled(self):
        return Student.query.filter_by(
            stuid=self.stuid, stuname=self.stuname).first() is not None

    def __str__(self):
        return f'Student(id={self.stuid}, name={self.stuname})'

    @staticmethod
    def import_teaching_assistant():
        db.session.add(Student(stuid='TAs', stuname='TAs'))
        db.session.commit()

    @staticmethod
    def find_student(students, stuid):
        for student in students:
            if student.stuid == stuid:
                return student
        return None

    @staticmethod
    def import_from_csv(file):
        students = Student.query.all()
        with open(file, 'r', encoding='utf-8') as f:
            f_csv = csv.reader(f)
            for row in f_csv:
                student = Student.find_student(students, row[0])
                if not student:
                    db.session.add(Student(stuid=row[0], stuname=row[1]))
                elif student.stuname != row[1]:
                    student.stuname = row[1]
        db.session.commit()


class RequiredFile(db.Model):
    __tablename__ = 'required_files'

    aid = db.Column(db.Integer, db.ForeignKey('assignments.aid'),
                    primary_key=True)
    filename = db.Column(db.String(128), primary_key=True)
    container_path = db.Column(db.String(128), primary_key=True)


class Assignment(db.Model):
    __tablename__ = 'assignments'

    aid = db.Column(db.Integer, primary_key=True)
    aname = db.Column(db.String(64), nullable=False)
    grader_image = db.Column(db.String(64), nullable=False)
    ddl = db.Column(db.DateTime, nullable=False)
    timeout = db.Column(db.Integer, nullable=False)
    score_extractor = db.Column(db.String(64), nullable=False)
    required_files = db.relationship('RequiredFile',
                                     backref=db.backref('assignment'),
                                     lazy=True,
                                     cascade='all, delete-orphan')
    scores = db.relationship('Score',
                             backref=db.backref('assignment'),
                             lazy=True)

    @staticmethod
    def add_or_update_assignment(new_assignment):
        assignment = Assignment.query.filter_by(
            aname=new_assignment.aname).first()
        if assignment:
            assignment.grader_image = new_assignment.grader_image
            assignment.ddl = new_assignment.ddl
            assignment.timeout = new_assignment.timeout
            assignment.score_extractor = new_assignment.score_extractor
            RequiredFile.query.filter_by(aid=assignment.aid).delete()
            for required_file in new_assignment.required_files:
                db.session.add(RequiredFile(
                    aid=assignment.aid,
                    filename=required_file.filename,
                    container_path=required_file.container_path
                ))
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
