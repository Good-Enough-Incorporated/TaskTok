
from celery import shared_task
import os
@shared_task
def send_email():
    #args subject, recipient, body, creationDate
    #from TaskTok.models import taskReminder
    #print(f"[{creationDate}]: Pretending to send an email to *{recipient}* subject= {subject} body = {body}")
    print("This is a test.")


@shared_task(bind=True)
def create_file(self, file, contents):
    with open(file, 'w') as f:
        f.write(contents)

@shared_task
def add(x, y):
    return x + y
