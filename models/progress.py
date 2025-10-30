from . import db
from datetime import datetime


class Progress(db.Model):
    __tablename__ = 'progress'

    # Add uniqueness constraint to prevent duplicate (user_id, module_id) rows
    __table_args__ = (
        db.UniqueConstraint('user_id', 'module_id', name='uix_user_module'),
    )
    progress_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 模块编号
    module_id = db.Column(db.String(20), nullable=True)
    # 浏览覆盖率（0~1）
    browse_coverage = db.Column(db.Float, nullable=True)
    # 学习时长（分钟）
    study_time = db.Column(db.Float, nullable=True)
    # 习题完成度（0~1）
    quiz_completion = db.Column(db.Float, nullable=True)
    # 综合进度值（0~1），非空
    progress_value = db.Column(db.Float, nullable=False)
    # 最后更新时间
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Progress {self.progress_id} user={self.user_id} module={self.module_id} value={self.progress_value}>'
