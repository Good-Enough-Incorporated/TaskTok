import subprocess
import socket
from uuid import uuid4
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import os


#  ----------- Unused Imports: Needs review ---------------
#  from dotenv import load_dotenv
#  --------------------------------------------------------

# Check to see if celery workers are running. If not, we'll want to display this somewhere as the 'Email Notification
# System is not running'
def verify_celery_worker():
    try:
        result = subprocess.check_output(['celery', '-A', 'RemindMeClient.Client.celery', 'status'])
        # print(f"OUTPUT RESULT: {result}")
        return True if result else False
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def verify_message_broker_online(host, port, timeout):
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
    timed_serializer = URLSafeTimedSerializer(os.environ.get('EMAIL_VERIFICATION_SECRET'))
    token_id = str(uuid4())
    token_data = {"email":email,"jti":token_id}
    return timed_serializer.dumps(token_data, salt=os.environ.get('SECURITY_PASSWORD_SALT'))


def verify_email_token(token_data, expiration=1800):
    timed_serializer = URLSafeTimedSerializer(os.environ.get('EMAIL_VERIFICATION_SECRET'))
    try:
        token_data = timed_serializer.loads(token_data, salt=os.environ.get('SECURITY_PASSWORD_SALT'), max_age=expiration)
        return token_data
    except SignatureExpired:
        return False
    except BadSignature:
        return False
