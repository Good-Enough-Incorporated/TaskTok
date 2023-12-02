
from celery import shared_task
from celery.utils.log import get_task_logger
from flask_mail import Message
from datetime import datetime, timedelta
from TaskTok.extensions import flaskMail, celery_worker
from TaskTok.models import TaskReminder, User
from TaskTok.extensions import db
from flask import render_template
logger = get_task_logger(__name__)
@celery_worker.on_after_configure.connect
def setup_beat_tasks(sender, **kwargs):
    """ Function called on celery connect (with --beat enabled)
        This will configure our celery worker to periodically 
        check for overdue or soon to be due tasks
    """
    sender.add_periodic_task(15.0, check_tasks_ready.s(), name="Analyze tasks")

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

@shared_task(bind=True)
def send_task_reminder(self, email_to, subject, message):
    logger.info("Starting send_task_reminder task")
    msg = Message(subject, recipients=[email_to])
    msg.html = message
    try:
        flaskMail.send(msg)
        logger.info("send_email was successful!")
    except Exception as e:
        logger.info("send_email failed! error: %s", e)

@celery_worker.task
def check_tasks_ready():
    print('this will use celery beat to check tasks')
    current_time = datetime.now()
    logger.info(f'[Current Time]: {current_time}')
    #task_list = TaskReminder.query.filter(TaskReminder.task_dueDate >= (current_time-(timedelta(days=30)))).all()
    task_list = TaskReminder.query.filter(TaskReminder.task_dueDate >= (current_time-(timedelta(days=0))), TaskReminder.task_email_sent is False).all()
    logger.info('There are %s tasks ready for email alerts!', len(task_list))
    for task in task_list:
        # we need to construct the email for each task, and queue up our emails
        logger.info(f'Working on {task.id}')
        email_message = render_template('email/taskEmailTemplate.html', username = task.owner_username, task_name=task.task_name, due_date=task.task_dueDate, duedate_offset=task.task_reminderOffSetTime, message=task.task_message)
        user = User.query.filter_by(username=task.owner_username).first()
        subject = f'TaskTok - Reminder for {task.task_name}'
        send_task_reminder.delay(user.email, subject, email_message)
        #TODO: send_task_reminder should update the .email_sent as we can check if it succeeded or failed
        task.update_email_sent(True)
    #send_email.delay('jason.supple.27@gmail.com', "Periodic Email Test", 'Testing periodic tasks')