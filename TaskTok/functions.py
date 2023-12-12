"""
This module provides utility functions for various system checks and operations
related to Celery workers, message brokers, and email token generation and verification.
It includes functions to verify the operational status of Celery workers and message brokers,
and to manage secure tokens for email-related processes using the itsdangerous library.
"""
import os
import subprocess
import socket
from uuid import uuid4
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature



#  ----------- Unused Imports: Needs review ---------------
#  from dotenv import load_dotenv
#  --------------------------------------------------------

# Check to see if celery workers are running. If not, we'll want to display this somewhere as the 'Email Notification
# System is not running'
def verify_celery_worker():
    """
    Checks if the Celery worker is running by executing a subprocess command.
    This function is useful for verifying the operational status of Celery
    workers in the system.

    :return: True if the Celery worker is running, False otherwise.
    """
    try:
        result = subprocess.check_output(['celery', '-A', 'RemindMeClient.Client.celery_worker', 'status'])
        # print(f"OUTPUT RESULT: {result}")
        return True if result else False
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def verify_message_broker_online(host, port, timeout):
    """
    Attempts to establish a socket connection to the message broker to verify its
    operational status. This function is particularly useful for checking the
    connectivity with the message broker service.

    :param host: The hostname of the message broker.
    :param port: The port on which the message broker is listening.
    :param timeout: The timeout period for the connection attempt.
    :return: True if the connection to the message broker is successful, False otherwise.
    """
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
    """
    Generates a secure token for email verification purposes. This function
    uses the itsdangerous URLSafeTimedSerializer to create a
    time-limited token, which includes the email and a unique identifier.

    :param email: The email address to be included in the token.
    :return: A securely generated token.
    """
    timed_serializer = URLSafeTimedSerializer(os.environ.get('EMAIL_VERIFICATION_SECRET'))
    token_id = str(uuid4())
    token_data = {"email":email,"jti":token_id}
    return timed_serializer.dumps(token_data, salt=os.environ.get('SECURITY_PASSWORD_SALT'))


def verify_email_token(token_data, expiration=1800):
    """
    Verifies a given token for email operations. It checks the token's
    validity and ensures it hasn't expired, using the itsdangerous URLSafeTimedSerializer.

    :param token_data: The token data to verify.
    :param expiration: The expiration time in seconds for the token (default is 1800 seconds).
    :return: The token data if verification is successful, False if the token is expired or invalid.
    """
    timed_serializer = URLSafeTimedSerializer(os.environ.get('EMAIL_VERIFICATION_SECRET'))
    try:
        token_data = timed_serializer.loads(token_data, salt=os.environ.get('SECURITY_PASSWORD_SALT'), max_age=expiration)
        return token_data
    except SignatureExpired:
        return False
    except BadSignature:
        return False
