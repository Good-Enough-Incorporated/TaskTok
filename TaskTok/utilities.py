import RemindMeClient.tasks 

def email_message(email_to, subject, body):
    RemindMeClient.tasks.send_email.delay(email_to, subject, body)

def check_emails_overdue():
    print('testing function')
    RemindMeClient.tasks.check_tasks_ready.delay()
