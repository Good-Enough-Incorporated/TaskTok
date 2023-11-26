from celery import shared_task
from TaskTok.extensions import flaskMail
from flask_mail import Message



#  --------  Old imports / not used: Need review --------
# import os
# from flask import Flask
# -------------------------------------------------------

@shared_task(bind=True)
def send_email(self, email_to, subject, body):
    msg = Message(subject, recipients=[email_to])
    # msg.body=body
    msg.html = body
    flaskMail.send(msg)

