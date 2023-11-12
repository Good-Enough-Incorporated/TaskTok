from TaskTok.Server import create_app
from flask import Flask, jsonify, request
from flask.cli import with_appcontext, FlaskGroup
from TaskTok.extensions import db, jwtManager
from TaskTok.models import User, NoNoTokens, taskReminder
from TaskTok.schema import UserSchema
from RemindMeClient import task
from TaskTok.functions import verifyCeleryWorker
from TaskTok.functions import verifyMessageBrokerOnline
import datetime
import os
app = create_app()
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 80
app.config['DEBUG'] = True
app.config['INITIALIZED'] = False

#TODO: Need to move from flask.cli to click
#import Click
@app.cli.command('checkCeleryStatus')
def checkCeleryStatus():
    print(f"*************CELERY STATUS: {verifyCeleryWorker()}*************************")

@app.cli.command('checkMessageBrokerStatus')
def checkMessageBrokerStatus():
    print(f"*********************MESSAGE_BROKER STATUS: {verifyMessageBrokerOnline(host='localhost', port=5672, timeout=5)}***************")


@app.cli.command('createAdminUser')
def makeAdminUser():
    defaultAcc = User(username="admin", email="admin@tasktok.com")
    defaultAcc.setPassword('superpassword')
    defaultAcc.add()

@app.cli.command('createAdminTasks')
def AddAdminTasks():
    for tasks in range(10):
        task = taskReminder(owner_username='admin', task_dueDate=datetime.datetime.now(), task_description="Hello, this is the reminder of the example task", task_name="My Task!", task_message="This is the message")
        task.add()

@app.cli.command('createDatabase')
def createDatabase():
    print("Creating database and default admin for first run.")
    db.create_all()


if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=443, debug=True, ssl_context='adhoc')


