"""
This module contains the Celery tasks for sending emails and periodic checking of tasks in TaskTok.
It includes functions for sending general emails, sending task reminders, and periodically checking for tasks
that are due or overdue.

Functions:
- setup_beat_tasks: Configures periodic tasks for the Celery worker.
- send_email: Sends an email with the specified content.
- send_task_reminder: Sends a task reminder email.
- check_tasks_ready: Checks for tasks that are due or overdue and queues reminder emails.
"""
from datetime import datetime, timedelta
from celery import shared_task
from celery.utils.log import get_task_logger
from flask_mail import Message
from flask import render_template
from TaskTok.extensions import flaskMail, celery_worker
from TaskTok.models import TaskReminder, User

logger = get_task_logger(__name__)
@celery_worker.on_after_configure.connect
def setup_beat_tasks(sender, **kwargs):
    """
    Configures periodic tasks for the Celery worker. It sets up a task that runs every 15 seconds
    to check for overdue or soon to be due tasks in TaskTok.

    Args:
        sender: The Celery app instance that is sending the configuration.
        **kwargs: Additional keyword arguments.

        note: this only runs with --beat option enabled for the celery worker
    """
    sender.add_periodic_task(15.0, check_tasks_ready.s(), name="Analyze tasks")

@shared_task(bind=True)
def send_email(self, email_to, subject, body):
    """
    Sends an email with the specified subject and body to the given recipient.

    Args:
        email_to (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The body content of the email (can be plain text or HTML).

    The function logs success or failure information.
    """
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
def send_task_reminder(self, email_to, subject, message, task_id):
    """
    Sends a task reminder email for a specific task.

    Args:
        email_to (str): The email address of the recipient.
        subject (str): The subject line of the email.
        message (str): The HTML content of the email.
        task_id (int): The ID of the task for which the reminder is being sent.

    Updates the `task_email_sent` status of the task upon successful email sending.
    Logs information about the success or failure of the email sending.
    """
    logger.info("Starting send_task_reminder task")
    msg = Message(subject, recipients=[email_to])
    msg.html = message
    try:
        flaskMail.send(msg)
        logger.info("send_task_reminder was successful! for %s", task_id)
        current_task = TaskReminder.query.filter(TaskReminder.id == task_id).first()
        # update the task_email_sent only if a successful email
        # our periodic task will continue to attempt to send this out
        # (smtp down, or other network issues)
        current_task.update_email_sent(True)

    except Exception as e:
        logger.info("send_email failed! error: %s", e)

@celery_worker.task
def check_tasks_ready():
    """
    Periodically checks for tasks that are due or overdue in TaskTok and queues reminder
    emails for them.

    Retrieves all tasks that are due or overdue and have not yet been sent an email
    reminder. For each of these tasks,
    it constructs a customized reminder email and queues it for sending.

    tasks will repeat (for failures) until send_task_reminder sets task_email_sent to True 
    """
    current_time = datetime.now()
    logger.info('[Current Time]: %s', current_time)
    
    task_list_all = TaskReminder.query.all()
    task_list = TaskReminder.query.filter(
        TaskReminder.task_dueDate <= (current_time-timedelta(days=0)),
        TaskReminder.task_email_sent == False).all() #SQLAlchemy must use ==, not is False

    logger.info('There are %s tasks in total', len(task_list_all)  )
    logger.info('There are %s tasks ready for email alerts!', len(task_list))
    for task in task_list:
        # we need to construct the email for each task, and queue up our emails
        logger.info('Working on %s', task.id)
        # construct the customized email to the recipient
        # TODO: add their email list to recipients
        email_message = render_template(
            'email/taskEmailTemplate.html',
            username = task.owner_username,
            task_name=task.task_name,
            due_date=task.task_dueDate,
            duedate_offset=task.task_reminderOffSetTime,
            message=task.task_message)

        user = User.query.filter_by(username=task.owner_username).first()
        subject = f'TaskTok - Reminder for {task.task_name}'
        send_task_reminder.delay(user.email, subject, email_message, task.id)
    #send_email.delay('jason.supple.27@gmail.com', "Periodic Email Test", 'Testing periodic tasks')
