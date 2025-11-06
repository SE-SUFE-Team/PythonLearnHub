from models import db
from datetime import datetime


class CodeExecution(db.Model):
    """代码执行历史记录"""
    __tablename__ = 'code_executions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    record_type = db.Column(db.Integer, default=0)  # 0=通用历史记录
    executed_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref=db.backref('code_executions', lazy=True))

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'code': self.code,
            'record_type': self.record_type,
            'executed_at': self.executed_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f'<CodeExecution {self.id} user={self.user_id} type={self.record_type}>'
