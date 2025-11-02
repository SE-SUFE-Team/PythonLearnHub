from . import db

class User(db.Model):
          __tablename__ = 'users'
          id = db.Column(db.Integer, primary_key = True)
          username = db.Column(db.String(80), nullable = False)  # 用户名允许重复
          email = db.Column(db.String(120), unique = True, nullable = False)
          password_hash = db.Column(db.String(120), nullable=False)

          def __repr__(self):
            return f'<User {self.username}>'