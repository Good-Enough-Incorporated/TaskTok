
from celery import shared_task
from celery.utils.log import get_task_logger
from flask_mail import Message
from datetime import datetime
from TaskTok.extensions import flaskMail, celery_worker
from TaskTok.models import TaskReminder as task
from TaskTok.extensions import db
logger = get_task_logger(__name__)
@celery_worker.on_after_configure.connect
def setup_beat_tasks(sender, **kwargs):
    """ Function called on celery connect (with --beat enabled)
        This will configure our celery worker to periodically 
        check for overdue or soon to be due tasks
    """
    sender.add_periodic_task(60.0, check_tasks_ready.s(), name="Analyze tasks")

@shared_task(bind=True)
def send_email(self, email_to, subject, body):
    logger.info("Starting send_email task")
    logger.info('email_to: [%s], subject: [%s, body: [%s]', email_to, subject, body)
    msg = Message(subject, recipients=[email_to])
    msg.body=body
    msg.html = body
    try:
        flaskMail.send(msg)
        logger.info("send_email was successful!")
    except Exception as e:
        logger.info("send_email failed! error: %s", e)

@celery_worker.task
def check_tasks_ready():
    print('this will use celery beat to check tasks')
    current_time = datetime.now()
    task_list = task.query.filter(task.task_dueDate >= current_time).all().all()
    logger.info('There are %s tasks ready for email alerts!', task_list.count)
    #send_email.delay('jason.supple.27@gmail.com', "Periodic Email Test", 'Testing periodic tasks')