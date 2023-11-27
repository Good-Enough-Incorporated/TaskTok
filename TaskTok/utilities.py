import RemindMeClient.task 

def email_message(email_to, subject, body):
    RemindMeClient.task.send_email.delay(email_to, subject, body)

def check_emails_overdue():
    print('testing function')
    RemindMeClient.task.check_tasks_ready.delay()
