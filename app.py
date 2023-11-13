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
import os
import sys


app = create_app()
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 80
app.config['DEBUG'] = True
app.config['INITIALIZED'] = False


@click.group()
def cli():
    pass


@cli.command('checkCeleryStatus')
def checkCeleryStatus():
    celery_status = verifyCeleryWorker()
    status_message = "OK" if celery_status else "NOT OK"
    box_width = max(len(status_message), 20) + 4  # Adjust the width of the box based on the message length

    print("\n" + "╔" + "═" * box_width + "╗")
    print(f"║ CELERY STATUS: {status_message} ".ljust(box_width) + "║")
    print("╚" + "═" * box_width + "╝\n")


@cli.command('checkMessageBrokerStatus')
def checkMessageBrokerStatus():
    host = 'localhost'
    port = 5672
    timeout = 5

    message_broker_status = verifyMessageBrokerOnline(host, port, timeout)

    status_message = "OK" if message_broker_status else "NOT OK"
    box_width = max(len(status_message), 24) + 4
    
    print("\n" + "╔" + "═" * box_width + "╗")
    print(f"║ MESSAGE BROKER STATUS: {status_message} ".ljust(box_width) + "║")
    print("╚" + "═" * box_width + "╝\n")


@cli.command('createAdminUser')
def makeAdminUser():
    with app.app_context():
        print("\nCreating Admin User...\n")
        defaultAcc = User(username="admin", email="admin@tasktok.com")
        defaultAcc.setPassword('superpassword')
        defaultAcc.add()


@cli.command('createAdminTasks')
def AddAdminTasks():
    with app.app_context():
        for tasks in range(10):
            task = taskReminder(owner_username='admin', task_dueDate=datetime.datetime.now(), task_description="Hello, this is the reminder of the example task", task_name="My Task!", task_message="This is the message")
            task.add()


@cli.command('createDB')
def createDB():
    with app.app_context():
        print("\nCreating database and default admin for first run.")
        db.create_all()


# Use this for testing setupError.html page and other error pages based on DB setup issues.
@cli.command('dropDB')
def dropDB():
    with app.app_context():
        print("\nDropping all database tables!")
        db.drop_all()


if __name__ == '__main__':
    # If command line args are provided, assume they're for Click.
    if len(sys.argv) > 1:
        cli()
    # Else, just run Flask.
    else:
        app.run(host='0.0.0.0', port=443, debug=True, ssl_context='adhoc')


