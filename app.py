"""
This module, 'app.py', serves as the entry point for the Flask application.
It imports and configures the Flask app using 'create_app' and sets up
various command-line interface (CLI) commands for database and application management.
This module includes commands for checking the status of Celery workers and message brokers,
creating administrative users and tasks, and managing the database through Flask-Migrate.
It also determines the mode of operation based on command-line arguments, either
running Flask commands or starting the Flask server.
"""

from flask_migrate import upgrade, migrate
from TaskTok import app
import click
import datetime
import sys
from TaskTok.extensions import db
from TaskTok.models import User, TaskReminder
from TaskTok.functions import verify_celery_worker
from TaskTok.functions import verify_message_broker_online




@click.group()
def cli():
    """
    Defines a Click command group for organizing custom Flask CLI
    commands. This function acts as a decorator
    to associate various CLI commands with the Flask application.
    """
    pass


@app.cli.command('checkCeleryStatus')
def check_celery_status():
    """
    CLI command to check the status of the Celery worker.
    It prints a status message indicating whether the
    Celery worker is operational or not.
    """
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
    """
    CLI command to check the status of the message broker (e.g., Redis).
    It tries to establish a connection to the message broker
    and prints a status message indicating its operational status.
    """
    host = 'localhost'
    port = 6379
    timeout = 5
    try:
        message_broker_status = verify_message_broker_online(host, port, timeout)
    except:
        message_broker_status = None
    status_message = "OK" if message_broker_status else "NOT OK"
    box_width = max(len(status_message), 24) + 4

    print("\n" + "╔" + "═" * box_width + "╗")
    print(f"║ MESSAGE BROKER STATUS: {status_message} ".ljust(box_width) + " ║")
    print("╚" + "═" * box_width + "╝\n")


@app.cli.command('createAdminUser')
def make_admin_user():
    """
    CLI command to create an administrative user.
    It uses predefined credentials to create a user with administrative privileges.
    """
    with app.app_context():
        print("\nCreating Admin User...\n")
        default_acc = User(username="admin", email="jason.supple.27@gmail.com")
        default_acc.set_password('superpassword')
        default_acc.add()


@app.cli.command('createAdminTasks')
def add_admin_tasks():
    """
    CLI command to create a set of tasks for the administrative user.
    It generates a predefined number of tasks associated with the admin account.
    """
    with app.app_context():
        count = 1
        
        for tasks in range(10):
            user_task = TaskReminder(owner_username='admin', task_dueDate=datetime.datetime.now(),
                                     task_description=f"Task {count} description",
                                     task_name=f"Task {count}", task_message="BlahBlahBlah")
            user_task.add()
            count+=1


@app.cli.command('createDB')
def create_db():
    """
    CLI command to create the database. It initializes
    the database schema according to the defined models.
    """
    with app.app_context():
        print("\nCreating database and default admin for first run.")
        db.create_all()


# Use this for testing setupError.html page and other error pages based on DB setup issues.


@app.cli.command('dropDB')
def drop_db():
    """
    CLI command to drop all tables in the database. This command is used to clear the database schema.
    """
    with app.app_context():
        print("\nDropping all database tables!")
        db.drop_all()


@app.cli.command('migrateDB')
@click.option('-m', '--message', default='Migration', help="Message for your migration script")
def migrate_db(message):
    """
    CLI command to generate a migration script for the database.
    It creates a migration based on the changes detected in the models.

    :param message: An optional message to describe the migration.
    """
    with app.app_context():
        migrate(message=message)
        print('Database migration generated')

@app.cli.command('upgradeDB')
def upgrade_db():
    """
    CLI command to apply the latest migration to the database.
    It upgrades the database schema to the latest version based on the migration scripts.
    """
    with app.app_context():
        upgrade()
        print('Database upgraded')

if __name__ == "__main__":
    """
    The main execution block to run the Flask application.
    It checks if command-line arguments are provided to execute
    CLI commands or starts the Flask server if no arguments are provided.
    """
    # If command line args are provided, assume they're for Click.
    if len(sys.argv) > 1:
        cli(app)
    # Else, just run Flask.
    else:
        app.run(host='0.0.0.0', port=443, debug=True, use_reloader=True, ssl_context='adhoc')
        # change ssl_context to below when testing locally
        # 'adhoc'
        # or for azure
        # '/home/jason/TaskTok/fullchain1.pem','/home/jason/TaskTok/privkey1.pem'
