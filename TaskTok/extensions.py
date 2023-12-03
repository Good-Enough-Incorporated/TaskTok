# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask import url_for
from celery import Celery
from dotenv import load_dotenv
import os
db = SQLAlchemy()
jwtManager = JWTManager()
flaskMail = Mail()
load_dotenv()
celery_worker = None


side_nav_menu_items = [
    {'title': 'Home', 'url': 'views.home'},
    {'title': 'Admin', 'url': 'views.admin'},
    {'title': 'Settings', 'url': 'views.userSettings'},
    {'title': 'Sign Out', 'url': 'auth.logout'},
]

def update_celery(app):
    global celery_worker
    celery_worker = app
    celery_worker.autodiscover_tasks(['RemindMeClient'])

def generate_links():
    generated_urls = []
    
    
    for item in side_nav_menu_items:
        new_entry = item.copy()
        new_entry['url'] = url_for(item['url'])
        generated_urls.append(new_entry)
        
    return generated_urls

    