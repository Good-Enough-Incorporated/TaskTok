"""
This module, `models.py`, defines the database models for the application.
It includes classes representing different entities such as users, tokens,
and tasks. Each class corresponds to a table in the database and includes fields
that represent the table columns with their respective data types. The module
also provides methods for various operations like adding, removing, updating
records, and performing specific queries related to each model.
"""
from datetime import datetime
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class User(db.Model):
    """
    Represents a user in the database. Includes attributes for user identification and authentication, such as username, email, password, and verification status. Additional fields include first and last name, timezone, and daylight savings preferences.
    """
    @staticmethod
    def generate_uuid():
        """
        Generates a unique UUID string for user identification.
        :return: A unique UUID string.
        """
        return str(uuid4())

    __tablename__ = 'user'
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
        """
        Represents the User object as a string.
        :return: A string representation of the User object.
        """
        return f"<User {self.username}>"
    
    def update_username(self, username):
        """
        Updates the username of the user and commits the change to the database.
        :param username: The new username to be set for the user.
        """
        self.username = username
        db.session.commit()
    
    def update_email(self, email):
        """
        Updates the email of the user and commits the change to the database.
        :param email: The new email to be set for the user.
        """
        self.email = email
        db.session.commit()

    def set_password(self, password):
        """
        Sets the user's password by hashing it and storing the hash in the database.
        :param password: The plaintext password to be hashed and set.
        """
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        """
        Verifies a given password against the user's stored password hash.
        :param password: The plaintext password to be verified.
        :return: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password, password)

    def verify_email_address(self):
        """
        Marks the user's email as verified and sets the confirmation date to the current time.
        """
        self.is_confirmed = True
        self.confirmed_date = datetime.now()

    def is_account_verified(self):
        """
        Checks if the user's account is verified.
        :return: True if the account is verified, False otherwise.
        """
        if self.is_confirmed:
            return True
        else:
            return False

    @classmethod
    def get_user_by_username(cls, username):
        """
        Retrieves a user by their username.
        :param username: The username of the user to be retrieved.
        :return: The User object if found, None otherwise.
        """
        print('getUserByUsername called with parameters %s %s' % (cls, username))
        return cls.query.filter_by(username=username).first()

    @classmethod
    def search_email_address(cls, email):
        """
        Searches for a user by their email address.
        :param email: The email address to search for.
        :return: The User object if found, None otherwise.
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_user_by_id(cls, user_id):
        """
        Retrieves a user by their unique ID.
        :param user_id: The ID of the user to be retrieved.
        :return: The User object if found, None otherwise.
        """
        return cls.query.filter_by(id=user_id).first()

    @classmethod
    def get_user_count(cls):
        """
        Counts the number of users in the database.
        :return: The number of users.
        """
        return cls.query.count()

    # add user to the database
    def add(self):
        """
        Adds the user to the database and commits the session.
        """
        db.session.add(self)
        db.session.commit()

    # remove user to the database
    def remove(self):
        """
        Removes the user from the database and commits the session.
        """
        db.session.delete(self)
        db.session.commit()


class NoNoTokens(db.Model):
    """
    Represents blocked tokens in the database, used for managing JWT token invalidation.
    """
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), default= datetime.utcnow)

    def __repr__(self) -> str:
        """
        Represents the NoNoTokens object as a string.
        :return: A string representation of the NoNoTokens object.
        """
        return f"<Token {self.jti}>"

    # add blocked token to the database
    def add(self):
        """
        Adds the blocked token to the database and commits the session.
        """
        db.session.add(self)
        db.session.commit()

    # remove blocked token to the database
    def remove(self):
        """
        Removes the blocked token to the database and commits the session.
        """
        db.session.delete(self)
        db.session.commit()

class EmailTokens(db.Model):
    """
    Represents blocked tokens in the database, used for managing email token invalidation.
    """
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Token {self.jti}>"

    # add blocked token to the database
    def add(self):
        """
        Adds the email token to the database and commits the session.
        """
        db.session.add(self)
        db.session.commit()

    # remove blocked token to the database
    def remove(self):
        """
        Removes the email token from the database and commits the session.
        """
        db.session.delete(self)
        db.session.commit()



class TaskReminder(db.Model):
    """
    Represents a task reminder in the database. It includes fields for task management, ownership, and tracking of reminders and task completion.
    """
    @staticmethod
    def generate_uuid():
        """
        Generates a unique UUID string for task identification.
        """
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
        """
        Adds the task to the database and commits the session.
        """
        db.session.add(self)
        db.session.commit()

    # remove task from the database
    def remove(self):
        """
        Removes the task from the database and commits the session.
        """
        db.session.delete(self)
        db.session.commit()

    def update_email_sent(self, update):
        """
        Updates the status of the email sent for the task.

        :param update: The updated status to be set.
        """
        print("Setting task to email_sent: True")
        self.task_email_sent = update
        db.session.commit()

    def task_email_date(self, date):
        """
        Sets the date when the email for the task was sent.

        :param date: The date to be set for the email sent.
        """
        self.email_date = date
        db.session.commit()

    def set_task_complete(self):
        """
        Marks the task as complete and sets the completion date.
        """
        self.task_completed = True
        self.task_completed_date = datetime.now()
        db.session.commit()

    @classmethod
    def find_task_by_username(cls, username):
        """
        Finds all tasks associated with a given username.

        :param username: The username for which to find tasks.
        :return: A list of tasks associated with the given username.
        """
        print(f'looking for {username} tasks')
        return cls.query.filter_by(owner_username=username).all()

    @classmethod
    def find_completed_task_by_username(cls, username):
        """
        Finds all completed tasks for a given username.

        :param username: The username for which to find completed tasks.
        :return: A list of completed tasks associated with the given username.
        """
        print(f'looking for {username}s completed tasks')
        return cls.query.filter_by(owner_username=username, task_completed=True).all()

    @classmethod 
    def find_noncomplete_task_by_username(cls, username):
        """
        Finds all non-completed tasks for a given username.

        :param username: The username for which to find non-completed tasks.
        :return: A list of non-completed tasks associated with the given username.
        """
        print(f'looking for {username}s non-completed tasks')
        return cls.query.filter_by(owner_username=username, task_completed=False).all()

    @classmethod
    def find_task_by_username_pagination(cls, username, page, pageSize):
        """
        Finds tasks associated with a given username with pagination.

        :param username: The username for which to find tasks.
        :param page: The page number for pagination.
        :param pageSize: The number of items per page.
        :return: A paginated query object containing the tasks.
        """
        query =  cls.query.filter_by(owner_username=username)
        paginated_query = query.paginate(page=page, per_page=pageSize)
        return paginated_query


