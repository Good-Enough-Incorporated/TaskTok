from celery import shared_task
from TaskTok.extensions import flaskMail, celery_worker

from flask_mail import Message

print(f'CELERY IS {celery_worker}')





@shared_task(bind=True)
def send_email(self, email_to, subject, body):
    
    msg = Message(subject, recipients=[email_to])
    # msg.body=body
    msg.html = body
    flaskMail.send(msg)

@shared_task(bind=True)
def test_period_task(self):
    print("I'm running every 30 seconds :)")