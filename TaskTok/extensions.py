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
celery_worker = Celery(__name__, broker=os.environ.get('broker_url'),backend=os.environ.get('result_backend'))
