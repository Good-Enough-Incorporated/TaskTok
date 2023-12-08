from .extensions import db
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
    first_name = db.Column(db.String(), unique=False, nullable=True)
    last_name = db.Column(db.String(), unique=False, nullable=True)
    email_notification_emailed = db.Column(db.Boolean(), default=True, unique=False)
    password = db.Column(db.Text())
    is_confirmed = db.Column(db.Boolean(), default=False, unique=False)
    confirmed_date = db.Column(db.DateTime())
    timezone = db.Column(db.String(), nullable=False, unique=False, default="US/Eastern")
    daylight_savings = db.Column(db.Boolean(), default = False, unique=False)

    def __repr__(self):
        return f"<User {self.username}>"
    
    def update_username(self, username):
        self.username = username
        db.session.commit()
    
    def update_email(self, email):
        self.email = email
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def verify_email_address(self):
        self.is_confirmed = True
        self.confirmed_date = datetime.now()

    def is_account_verified(self):
        if self.is_confirmed:
            return True
        else:
            return False

    @classmethod
    def get_user_by_username(cls, username):
        print('getUserByUsername called with parameters %s %s' % (cls, username))
        return cls.query.filter_by(username=username).first()

    @classmethod
    def search_email_address(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first()

    @classmethod
    def get_user_count(cls):
        return cls.query.count()

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
    created_at = db.Column(db.DateTime(), default= datetime.utcnow)

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

class EmailTokens(db.Model):
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



class TaskReminder(db.Model):
    @staticmethod
    def generate_uuid():
        return str(uuid4())

    __tablename__ = "taskreminder"
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid4()))
    owner_username = db.Column(db.String(120), nullable=False)
    task_emailList = db.Column(db.JSON, nullable=True)
    task_reminderOffSetTime = db.Column(db.DateTime, nullable=True)
    task_dueDate = db.Column(db.DateTime, nullable=False)
    task_description = db.Column(db.String(255), nullable=False)
    task_name = db.Column(db.String(255), nullable=False)
    task_message = db.Column(db.String(255), nullable=False)
    task_is_recurring = db.Column(db.Boolean(), default=False, unique=False)
    task_archived = db.Column(db.Boolean(), default=False, unique=False)
    task_completed = db.Column(db.Boolean(), default=False, unique=False)
    task_completed_date = db.Column(db.DateTime, nullable=True)
    task_email_sent = db.Column(db.Boolean(), default=False, unique=False)
    task_email_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<taskReminder {self.task_description}>"

    # add task to the database
    def add(self):
        db.session.add(self)
        db.session.commit()

    # remove task from the database
    def remove(self):
        db.session.delete(self)
        db.session.commit()

    def update_email_sent(self, update):
        print("Setting task to email_sent: True")
        self.task_email_sent = update
        db.session.commit()

    def task_email_date(self, date):
        self.email_date = date
        db.session.commit()

    def set_task_complete(self):
        self.task_completed = True
        self.task_completed_date = datetime.now()
        db.session.commit()

    @classmethod
    def find_task_by_username(cls, username):
        print(f'looking for {username} tasks')
        return cls.query.filter_by(owner_username=username).all()
    
    @classmethod
    def find_completed_task_by_username(cls, username):
        print(f'looking for {username}s completed tasks')
        return cls.query.filter_by(owner_username=username, task_completed=True).all()

    @classmethod 
    def find_noncomplete_task_by_username(cls, username):
        print(f'looking for {username}s non-completed tasks')
        return cls.query.filter_by(owner_username=username, task_completed=False).all()
    
    @classmethod
    def find_task_by_username_pagination(cls, username, page, pageSize):
        query =  cls.query.filter_by(owner_username=username)
        paginated_query = query.paginate(page=page, per_page=pageSize)
        return paginated_query

    
