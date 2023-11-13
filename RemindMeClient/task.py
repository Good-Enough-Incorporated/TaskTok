from celery import shared_task
import os
from flask import Flask
from TaskTok.extensions import flaskMail
from flask_mail import Message

@shared_task(bind=True)
def send_email(self, email_to, subject, body):
    #args subject, recipient, body, creationDate
    #from TaskTok.models import taskReminder
    #print(f"[{creationDate}]: Pretending to send an email to *{recipient}* subject= {subject} body = {body}")
        msg = Message(subject, recipients=[email_to])
        msg.body=body
        flaskMail.send(msg)


@shared_task(bind=True)
def create_file(self, file, contents):
    with open(file, 'w') as f:
        f.write(contents)

@shared_task
def add(x, y):
    return x + y