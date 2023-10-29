from .extensions import db, jwtManager
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
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
    
    #add user to the database
    def add(self):
        db.session.add(self)
        db.session.commit()
    #remove user to the database
    def remove(self):
        db.session.delete(self)
        db.session.commit()

class NoNoTokens(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(),nullable=False)
    created_at = db.Column(db.DateTime(),default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Token {self.jti}>"
    #add blocked token to the database
    def add(self):
        db.session.add(self)
        db.session.commit()
    #remove blocked token to the database
    def remove(self):
        db.session.delete(self)
        db.session.commit()