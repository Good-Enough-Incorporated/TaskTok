from TaskTok.Server import create_app
from flask import Flask, jsonify, request
from flask.cli import with_appcontext, FlaskGroup
from TaskTok.extensions import db, jwtManager
from TaskTok.models import User, NoNoTokens
from TaskTok.schema import UserSchema
from RemindMeClient import task
from TaskTok.functions import verifyCeleryWorker
from TaskTok.functions import verifyMessageBrokerOnline
import os
app = create_app()
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 80
app.config['DEBUG'] = True
app.config['INITIALIZED'] = False


@app.cli.command('checkCeleryStatus')
def checkCeleryStatus():
    print(f"*************CELERY STATUS: {verifyCeleryWorker()}*************************")

@app.cli.command('checkMessageBrokerStatus')
def checkMessageBrokerStatus():
    print(f"*********************MESSAGE_BROKER STATUS: {verifyMessageBrokerOnline(host='localhost', port=5672, timeout=5)}***************")


@app.cli.command('makeAdminUser')
def makeAdminUser():
    defaultAcc = User(username="admin", email="admin@tasktok.com")
    defaultAcc.setPassword('superpassword')
    defaultAcc.add()

@app.cli.command('createDatabase')
def createDatabase():
    print("Creating database and default admin for first run.")
    db.create_all()


if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=80, debug=True)


