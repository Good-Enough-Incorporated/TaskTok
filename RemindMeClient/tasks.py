
from TaskTok.extensions import flaskMail, celery_worker
from celery import shared_task
from celery.utils.log import get_task_logger
from flask_mail import Message

logger = get_task_logger(__name__)
@celery_worker.on_after_configure.connect
def setup_beat_tasks(sender, **kwargs):
    print('************************** SETTING UP PERIODIC TASKS **************************************')
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
    send_email.delay('jason.supple.27@gmail.com', "Periodic Email Test", 'Testing periodic tasks')