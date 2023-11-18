from TaskTok.Server import create_app
from flask import Flask, jsonify, request
from flask.cli import with_appcontext, FlaskGroup
from TaskTok.extensions import db, jwtManager
from TaskTok.models import User, NoNoTokens, taskReminder
from TaskTok.schema import UserSchema
from RemindMeClient import task
from TaskTok.functions import verifyCeleryWorker
from TaskTok.functions import verifyMessageBrokerOnline
import click
import datetime
from flask_mail import Mail, Message
import sys
from TaskTok.extensions import flaskMail

app = create_app()
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 80
app.config['DEBUG'] = True
app.config['INITIALIZED'] = False


@click.group()
def cli():
    pass


@app.cli.command('checkCeleryStatus')
def checkCeleryStatus():
    try:
        celery_status = verifyCeleryWorker()
    except: 
        celery_status = None
        
    status_message = "OK" if celery_status else "NOT OK"
    box_width = max(len(status_message), 20) + 4  # Adjust the width of the box based on the message length

    print("\n" + "╔" + "═" * box_width + "╗")
    print(f"║ CELERY STATUS: {status_message} ".ljust(box_width) + "║")
    print("╚" + "═" * box_width + "╝\n")


@app.cli.command('checkMessageBrokerStatus')
def checkMessageBrokerStatus():
    host = 'localhost'
    port = 5672
    timeout = 5
    try:
        message_broker_status = verifyMessageBrokerOnline(host, port, timeout)
    except:
        message_broker_status = None
    status_message = "OK" if message_broker_status else "NOT OK"
    box_width = max(len(status_message), 24) + 4
    
    print("\n" + "╔" + "═" * box_width + "╗")
    print(f"║ MESSAGE BROKER STATUS: {status_message} ".ljust(box_width) + "║")
    print("╚" + "═" * box_width + "╝\n")


@app.cli.command('createAdminUser')
def makeAdminUser():
    with app.app_context():
        print("\nCreating Admin User...\n")
        defaultAcc = User(username="admin", email="admin@tasktok.com")
        defaultAcc.setPassword('superpassword')
        defaultAcc.add()


@app.cli.command('createAdminTasks')
def AddAdminTasks():
    with app.app_context():
        for tasks in range(10):
            task = taskReminder(owner_username='admin', task_dueDate=datetime.datetime.now(), task_description="Hello, this is the reminder of the example task", task_name="My Task!", task_message="This is the message")
            task.add()


@app.cli.command('createDB')
def createDB():
    with app.app_context():
        print("\nCreating database and default admin for first run.")
        db.create_all()


# Use this for testing setupError.html page and other error pages based on DB setup issues.
@app.cli.command('dropDB')
def dropDB():
    with app.app_context():
        print("\nDropping all database tables!")
        db.drop_all()

@app.cli.command('testSendMail')
def testSendMail():
    
    msg = Message("This is a test email", recipients=['jason.supple.27@gmail.com'])
    msg.body="This email was sent using flask-mail and google's smtp relay"
    flaskMail.send(msg)

if __name__ == '__main__':
    # If command line args are provided, assume they're for Click.
    if len(sys.argv) > 1:
        cli(app)
    # Else, just run Flask.
    else:
     app.run(host='0.0.0.0', port=443, debug=True, ssl_context=('/home/jason/TaskTok/fullchain1.pem','/home/jason/TaskTok/privkey1.pem'))
     #change ssl_context to below when testing locally
     #'adhoc'
     #or for azure
     # '/home/jason/TaskTok/fullchain1.pem','/home/jason/TaskTok/privkey1.pem'
     


