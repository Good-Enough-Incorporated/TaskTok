
from celery import shared_task
import os
from flask import Flask
from flask_mail import Mail, Message
from TaskTok import app
@shared_task
def send_email():
    #args subject, recipient, body, creationDate
    #from TaskTok.models import taskReminder
    #print(f"[{creationDate}]: Pretending to send an email to *{recipient}* subject= {subject} body = {body}")
    with app.app_context():
        msg = Message("This is a test email", recipients=['jason.supple.27@gmail.com'])
        msg.body="This email was sent using flask-mail and google's smtp relay"
        app.mail.send(msg)


@shared_task(bind=True)
def create_file(self, file, contents):
    with open(file, 'w') as f:
        f.write(contents)

@shared_task
def add(x, y):
    return x + y
