
from TaskTok.extensions import flaskMail, celery_worker
from celery import shared_task
from flask_mail import Message


@celery_worker.on_after_configure.connect
def setup_beat_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, check_tasks_ready.s(), name="Analyze tasks")

@shared_task(bind=True)
def send_email(self, email_to, subject, body):
    print('hello')
    msg = Message(subject, recipients=[email_to])
    msg.body=body
    msg.html = body
    flaskMail.send(msg)

@celery_worker.task
def check_tasks_ready():
    print('this will use celery beat to check tasks')