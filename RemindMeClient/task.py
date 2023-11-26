from celery import shared_task




#  --------  Old imports / not used: Need review --------
# import os
# from flask import Flask
# -------------------------------------------------------

@shared_task(bind=True)
def send_email(self, email_to, subject, body):
    from TaskTok.extensions import flaskMail
    from flask_mail import Message
    msg = Message(subject, recipients=[email_to])
    # msg.body=body
    msg.html = body
    flaskMail.send(msg)


@shared_task(bind=True)
def create_file(file, contents):
    with open(file, 'w') as f:
        f.write(contents)


@shared_task
def add(x, y):

    return x + y
