"""
This module, 'extensions.py', initializes various Flask extensions and utility
functions used across the application. It includes the initialization of
Flask-SQLAlchemy for database operations, Flask-JWT-Extended for JWT management,
Flask-Mail for email functionality, and Celery for background task processing.
The module also defines utility functions for updating Celery with Flask
context and generating navigation links based on predefined items.
"""

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
    """
    Configures the Celery worker with the Flask application context.
    This function is necessary to ensure that Celery tasks have access
    to the Flask app's context, such as configuration and database access.

    :param app: The Flask application instance to be used with the Celery worker.
    """
    global celery_worker
    celery_worker = app
    celery_worker.autodiscover_tasks(['RemindMeClient'])


def generate_links():
    """
    Generates the full URLs for the navigation menu items defined in 'side_nav_menu_items'.
    This function is used to dynamically create the navigation links in the application,
    ensuring that URLs are correctly constructed with Flask's url_for function. Additionally,
    this gives us a single point of updating our site links. (side_nav_menu_items)

    :return: A list of dictionaries, each containing the title and URL for a navigation menu item.
    """

    generated_urls = []
    
    
    for item in side_nav_menu_items:
        new_entry = item.copy()
        new_entry['url'] = url_for(item['url'])
        generated_urls.append(new_entry)
        
    return generated_urls

    