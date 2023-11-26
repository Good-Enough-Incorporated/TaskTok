import RemindMeClient.task 

def email(email_to, subject, body):
    
    RemindMeClient.task.send_email.delay(email_to, subject, body)