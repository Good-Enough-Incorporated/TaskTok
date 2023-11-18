import subprocess
import socket
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
import os
#Check to see if celery workers are running. If not, we'll want to display this somewhere as the 'Email Notification System is not running'
def verifyCeleryWorker():
    try:
        result = subprocess.check_output(['celery','-A', 'RemindMeClient.Client.celery', 'status'])
        #print(f"OUTPUT RESULT: {result}")
        return True if result else False
    except Exception as error:
        return False
    


def verifyMessageBrokerOnline(host, port, timeout):
    try:
        # Create a socket object
        s = socket.create_connection((host, port), timeout=timeout)
        
        # If the connection was successful, close the socket and return True
        print("Successfully connected to port 5672!")
        s.close()
        return True
    except socket.error as e:
        # If the connection attempt fails, print an error message
        print("Failed to connect to port 5672:")
        print(str(e))
        return False

def generate_email_token(email):
    timedSerializer = URLSafeTimedSerializer(os.environ.get('EMAIL_VERIFICATION_SECRET'))
    return timedSerializer.dumps(email, salt=os.environ.get('SECURITY_PASSWORD_SALT'))

def verify_email_token(token,expiration=1800):
    timedSerializer = URLSafeTimedSerializer(os.environ.get('EMAIL_VERIFICATION_SECRET'))
    try:
        email = timedSerializer.loads(token, salt=os.environ.get('SECURITY_PASSWORD_SALT'), max_age=expiration)
    except:
        return False
    return email