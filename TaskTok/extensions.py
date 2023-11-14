# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
db = SQLAlchemy()
jwtManager = JWTManager()
flaskMail = Mail()
