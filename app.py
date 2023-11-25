from TaskTok.Server import create_app
from TaskTok.extensions import db
from TaskTok.models import User, TaskReminder
from TaskTok.functions import verify_celery_worker
from TaskTok.functions import verify_message_broker_online
from flask_mail import Message
import click
import datetime
import sys

#  -------------- Unused Imports: Needs review --------------
#  from flask import Flask, jsonify, request
#  from flask import render_template
#  from flask.cli import with_appcontext, FlaskGroup
#  from TaskTok.schema import UserSchema
#  from RemindMeClient import task
#  from TaskTok.extensions import jwtManager, flaskMail
#  from TaskTok.models import NoNoTokens
#  ----------------------------------------------------------

app = create_app()
app.config['HOST'] = '0.0.0.0'
app.config['PORT'] = 80
app.config['DEBUG'] = True
app.config['INITIALIZED'] = False


@click.group()
def cli():
    pass


@app.cli.command('checkCeleryStatus')
def check_celery_status():
    try:
        celery_status = verify_celery_worker()
    except:
        celery_status = None

    status_message = "OK" if celery_status else "NOT OK"
    box_width = max(len(status_message), 20) + 4  # Adjust the width of the box based on the message length

    print("\n" + "╔" + "═" * box_width + "╗")
    print(f"║ CELERY STATUS: {status_message} ".ljust(box_width) + "║")
    print("╚" + "═" * box_width + "╝\n")


@app.cli.command('checkMessageBrokerStatus')
def check_message_broker_status():
    host = 'localhost'
    port = 5672
    timeout = 5
    try:
        message_broker_status = verify_message_broker_online(host, port, timeout)
    except:
        message_broker_status = None
    status_message = "OK" if message_broker_status else "NOT OK"
    box_width = max(len(status_message), 24) + 4

    print("\n" + "╔" + "═" * box_width + "╗")
    print(f"║ MESSAGE BROKER STATUS: {status_message} ".ljust(box_width) + "║")
    print("╚" + "═" * box_width + "╝\n")


@app.cli.command('createAdminUser')
def make_admin_user():
    with app.app_context():
        print("\nCreating Admin User...\n")
        default_acc = User(username="admin", email="admin@tasktok.com")
        default_acc.set_password('superpassword')
        default_acc.add()


@app.cli.command('createAdminTasks')
def add_admin_tasks():
    with app.app_context():
        for tasks in range(10):
            user_task = TaskReminder(owner_username='admin', task_dueDate=datetime.datetime.now(),
                                     task_description="Hello, this is the reminder of the example task",
                                     task_name="My Task!", task_message="This is the message")
            user_task.add()


@app.cli.command('createDB')
def create_db():
    with app.app_context():
        print("\nCreating database and default admin for first run.")
        db.create_all()


# Use this for testing setupError.html page and other error pages based on DB setup issues.


@app.cli.command('dropDB')
def drop_db():
    with app.app_context():
        print("\nDropping all database tables!")
        db.drop_all()


@app.cli.command('testSendMail')
def test_send_mail():
    with app.app_context():
        msg = Message("This is a test email", recipients=['jason.supple.27@gmail.com'])
        msg.body = "This email was sent using flask-mail and google's smtp relay"
        app.mail.send(msg)


if __name__ == '__main__':
    # If command line args are provided, assume they're for Click.
    if len(sys.argv) > 1:
        cli(app)
    # Else, just run Flask.
    else:
        app.run(host='0.0.0.0', port=443, debug=True, ssl_context='adhoc')
        # change ssl_context to below when testing locally
        # 'adhoc'
        # or for azure
        # '/home/jason/TaskTok/fullchain1.pem','/home/jason/TaskTok/privkey1.pem'
