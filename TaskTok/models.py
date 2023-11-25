from .extensions import db, jwtManager
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):

    @staticmethod
    def generate_uuid():
        return str(uuid4())

    __tablename__ = 'users'
    id = db.Column(db.String(), primary_key=True, default=generate_uuid)
    username = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True)
    password = db.Column(db.Text())
    is_confirmed = db.Column(db.Boolean(), default=False, unique=False)
    confirmed_date = db.Column(db.DateTime())

    def __repr__(self):
        return f"<User {self.username}>"

    def setPassword(self, password):
        self.password = generate_password_hash(password)

    def verifyPassword(self, password):
        return check_password_hash(self.password, password)

    def verifyEmailAddress(self):
        self.is_confirmed = True
        self.confirmed_date = datetime.now()

    def isAccountVerified(self):
        if self.is_confirmed == True:
            return True
        else:
            return False

    @classmethod
    def getUserByUsername(cls, username):
        print('getUserByUsername called with parameters %s %s' % (cls, username))
        return cls.query.filter_by(username=username).first()

    @classmethod
    def searchEmailAddress(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def getUserById(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def getUserCount(cls):
        return (cls.query.count())

    # add user to the database
    def add(self):
        db.session.add(self)
        db.session.commit()
    # remove user to the database

    def remove(self):
        db.session.delete(self)
        db.session.commit()


class NoNoTokens(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Token {self.jti}>"
    # add blocked token to the database

    def add(self):
        db.session.add(self)
        db.session.commit()
    # remove blocked token to the database

    def remove(self):
        db.session.delete(self)
        db.session.commit()


class taskReminder(db.Model):
    @staticmethod
    def generate_uuid():
        return str(uuid4())

    __tablename__ = "taskreminders"
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid4()))
    owner_username = db.Column(db.String(120), nullable=False)
    task_emailList = db.Column(db.JSON, nullable=True)
    task_reminderOffSetTime = db.Column(db.DateTime, nullable=True)
    task_dueDate = db.Column(db.DateTime, nullable=False)
    task_description = db.Column(db.String(255), nullable=False)
    task_name = db.Column(db.String(255), nullable=False)
    task_message = db.Column(db.String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<taskReminder {self.task_description}>"
    # add blocked token to the database

    def add(self):
        db.session.add(self)
        db.session.commit()
    # remove blocked token to the database

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def findTaskByUsername(cls, username):
        print(f'looking for {username} tasks')
        return cls.query.filter_by(owner_username=username).all()
