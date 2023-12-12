"""
This module, `utilities.py`, provides utility functions that facilitate
certain operations such as sending emails and checking overdue emails.
These functions are designed to invoke asynchronous tasks using Celery.
This separation of concerns helps avoid circular imports by moving 
specific Celery task invocations out of the main application flow 
and into a dedicated utilities module.
"""
import RemindMeClient.tasks 

def email_message(email_to, subject, body):
    """
    Sends an email message by invoking the 'send_email' task asynchronously using Celery.
    This function abstracts the Celery task call to send emails, thereby
    simplifying email sending operations in the application.

    :param email_to: The recipient's email address.
    :param subject: The subject of the email.
    :param body: The body content of the email.
    """
    RemindMeClient.tasks.send_email.delay(email_to, subject, body)

def check_emails_overdue():
    """
    Checks for overdue emails by invoking the 'check_tasks_ready' task asynchronously using Celery.
    This function is intended for use in periodic checks or triggers
    to determine if there are any pending tasks or emails that need to be addressed.
    """
    RemindMeClient.tasks.check_tasks_ready.delay()
