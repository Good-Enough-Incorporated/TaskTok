import subprocess
import socket

#Check to see if celery workers are running. If not, we'll want to display this somewhere as the 'Email Notification System is not running'
def verifyCeleryWorker():
    try:
        result = subprocess.check_output(['celery','-A', 'RemindMeClient.Client.celery', 'status'])
        return True if result else False
    except subprocess.CalledProcessError as error:
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
    