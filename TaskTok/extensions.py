# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from celery import Celery

db = SQLAlchemy()
jwtManager = JWTManager()
flaskMail = Mail()
celery_worker = Celery(__name__)

def update_celery(app):
    global celery_worker
    celery_worker.conf.update(app.conf)
    # Additional specific configurations can go here
    return celery_worker
