from models import db
from datetime import datetime


class Problem(db.Model):
    __tablename__ = 'problems'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(20))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    submissions = db.relationship('Submission', backref='problem', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'difficulty': self.difficulty,
            'description': self.description
        }


class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20))  # AC, WA, TLE, RE, CE
    passed_cases = db.Column(db.Integer, default=0)
    total_cases = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    execution_time = db.Column(db.Float)
    submitted_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'problem_id': self.problem_id,
            'code': self.code,
            'status': self.status,
            'passed_cases': self.passed_cases,
            'total_cases': self.total_cases,
            'error_message': self.error_message,
            'execution_time': self.execution_time,
            'submitted_at': self.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        }
