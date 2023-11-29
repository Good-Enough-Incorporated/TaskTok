# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from celery import Celery
from dotenv import load_dotenv
import os
db = SQLAlchemy()
jwtManager = JWTManager()
flaskMail = Mail()
load_dotenv()
celery_worker = None


def update_celery(app):
    global celery_worker
    celery_worker = app
    celery_worker.autodiscover_tasks(['RemindMeClient'])
