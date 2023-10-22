from extensions import db
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(), primary_key=True, default = str(uuid4()))
    username = db.Column(db.String(), nullable=False)
    email = db.Column(db.String())
    password = db.Column(db.Text())

    def __repr__(self):
        return f"<User {self.username}>"
    
    def setPassword(self, password):
         self.password = generate_password_hash(password)
    
    def verifyPassword(self,password):
        return check_password_hash(self.password, password)
    
    @classmethod
    def getUserByUsername(cls, username):
        return cls.query.filter_by(username = username).first()
    
    @classmethod
    def getUserCount(cls):
        return (cls.query.count())
    
    def add(self):
        db.session.add(self)
        db.session.commit()

    def remove(self):
        db.session.delete(self)
        db.session.commit()
