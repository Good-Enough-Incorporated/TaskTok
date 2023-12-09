"""
This module contains the API relatied functions for supporting TaskTok's client side, it returns a json format which
is easily adaptable for clients like js, or any other no html based client.

It includes functions for listing tasks, adding, removing, and completing tasks, as well as other features such
as updating user settings, and the admin statistics.


Functions:
- messageBroker: Gets the current status of the message broker, diplays on admin page.
- celeryStatus: Gets the current status of the celery worker, displays on admin page.
- getServerUtilization: gets the current CPU/RAM utilization, displays on admin apge.
- list_completed_task: Lists all completed tasks for the current user.
- list_noncomplete_task: Lists all non complete tasks for the current user.
- list_all_task: Lists all tasks for the current user.
- list_task_pagination: Lists all tasks for the current user (by pages).
- remove_task: Removes a specific task from the current user.
- complete_task: Marks a task as complete for the current user.
- add_task: Adds a new task for the current user.
- edit_task: Modifies an existing task for the current user.
"""
import re
import os
import datetime
import psutil
from flask import Blueprint, jsonify, request
from TaskTok.functions import verify_celery_worker, verify_message_broker_online
from flask_jwt_extended import jwt_required, get_jwt, current_user
from sqlalchemy.exc import SQLAlchemyError
from TaskTok.models import User, TaskReminder
from TaskTok.extensions import db
from TaskTok.schema import UserSchema, TaskSchema
from TaskTok.utilities import email_message, check_emails_overdue


#  ---------- Unused Imports: Needs review ----------------
#  import subprocess
#  import socket
#  from RemindMeClient import task as cTask
#  from RemindMeClient.task import create_file
#  --------------------------------------------------------
api = Blueprint('api', __name__)


# TODO: Delete, but make sure nothing is still using this test function
@api.route('/sendMail')
@jwt_required()
def send_mail():
    email_message('jason.supple.27@gmail.com', "Test Subject", "Test Body")
    # create_file.delay('test.txt', "hello world")
    return 'send_email celery task created :)'


@api.route('/messageBroker')
def messageBroker():
    """
    Retrieves the current status of the message broker and returns it as JSON. 
    This is used to display the status on the admin page. If the message broker 
    is not online or an exception occurs, it will return the exception message.
    """
    host = 'localhost'
    port = 6379
    timeout = 2
    try:
        results = verify_message_broker_online(host, port, timeout)
    except Exception as e:
        results = e

    print(results)
    return jsonify({'Message': results})


@api.route('/celeryStatus')
def celeryStatus():
    """
    Retrieves the current status of the Celery worker and returns it as JSON. 
    This is intended for display on the admin page. In case of an error, the 
    exception message is returned.
    """
    try:
        results = verify_celery_worker()
    except Exception as e:
        results = e

    print(results)
    return jsonify({'Message': results})


@api.route('/serverUtilization')
def getServerUtilization():
    """
    Gets the current CPU and RAM utilization of the server. The CPU usage is 
    calculated based on the load average over 5 minutes and the total number 
    of CPU cores. The RAM usage is obtained directly. The information is returned 
    as JSON, suitable for display on the admin page.
    """
    cpu_load_1, cpu_load_5, cpu_load_15 = psutil.getloadavg()
    cpu_usage = (cpu_load_5 / os.cpu_count()) * 100

    ram_usage = psutil.virtual_memory()[2]

    return jsonify({'data': {'cpu': cpu_usage, 'ram': ram_usage}})


@api.route('/addTask', methods=['POST'])
@jwt_required()
def add_task():
    """
    Adds a new task for the current user. It expects JSON input containing 
    task details such as name, description, due date, reminder offset time, 
    email list, and email message. Performs basic validation on input fields. 
    Returns JSON indicating success or failure, including error messages for failures.
    """
    # get the current user's information
    user_data = current_user

    # Validate and get data from request
    data = request.json
    task_name = data.get('task_name')
    task_description = data.get('task_description')
    task_due_date = data.get('task_dueDate')
    task_reminder_off_set = data.get('task_reminderOffSetTime')
    task_email_list = data.get('task_emailList')
    task_email_message = data.get('task_email_message')

    # Basic validation
    if not all([task_name, task_description, task_due_date, task_reminder_off_set]):
        return jsonify({'Message': 'add_failed', 'Error': 'Missing required fields.'}), 400

    #  Checking if task_name is an empty string.
    if not isinstance(task_name, str) or task_name.strip() == "":
        return jsonify({'Message': 'add_failed', 'Error': 'Invalid task name.'}), 400

    # VChecking if task_description is an empty string.
    if not isinstance(task_description, str) or task_description.strip() == "":
        return jsonify({'Message': 'add_failed', 'Error': 'Invalid task description.'}), 400

    # TODO: Email validation goes here.

    print(task_due_date)
    print(task_reminder_off_set)

    formatted_due_date = format_date(task_due_date)
    formatted_reminder_off_set = format_date(task_reminder_off_set)

    print(formatted_due_date)
    print(formatted_reminder_off_set)
    try:
        # task_due_date = datetime.datetime.strptime(task_due_date, f'%Y-%m-%dT%H:%M:%S')
        # task_reminder_off_set = datetime.datetime.strptime(task_reminder_off_set, f'%Y-%m-%dT%H:%M:%S')

        if task_reminder_off_set > task_due_date:
            return jsonify({'Message': 'add_failed', 'Error': 'Reminder Offset must be before the due date.'}), 400

        task = TaskReminder(
            owner_username=user_data.username,
            task_dueDate=formatted_due_date,
            task_description=task_description,
            task_reminderOffSetTime=formatted_reminder_off_set,
            task_message=task_email_message,
            task_emailList=task_email_list,
            task_name=task_name
        )
        db.session.add(task)
        db.session.commit()

        task_array = [task]
        task_string = TaskSchema().dump(task_array, many=True)

        return jsonify({"Message": "add_success", "TaskList": task_string}), 200

    except ValueError:
        return jsonify({'Message': 'add_failed', 'Error': "Invalid DateTime format received."}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'Message': 'add_failed', 'Error': str(e)}), 500


@api.route('/listNonCompleteTask')
@jwt_required()
def list_noncomplete_task():
    """
    Lists all non-completed tasks for the current user. Returns a JSON list 
    of tasks, serialized using TaskSchema.
    """
    user_data = current_user
    task_list = TaskReminder.find_noncomplete_task_by_username(username=user_data.username)
    task_list_string = TaskSchema().dump(task_list, many=True)
    print(type(task_list_string))
    return jsonify({"TaskList": task_list_string}), 200


@api.route('/listCompletedTask')
@jwt_required()
def list_completed_task():
    """
    Lists all completed tasks for the current user. Returns a JSON list of 
    tasks, serialized using TaskSchema.
    """
    user_data = current_user
    task_list = TaskReminder.find_completed_task_by_username(username=user_data.username)
    task_list_string = TaskSchema().dump(task_list, many=True)
    print(type(task_list_string))
    return jsonify({"TaskList": task_list_string}), 200


@api.route('/listAllTask')
@jwt_required()
def list_all_task():
    """
    Lists all tasks for the current user, regardless of their completion status. 
    Returns a JSON list of tasks, serialized using TaskSchema.
    """
    user_data = current_user
    task_list = TaskReminder.find_task_by_username(username=user_data.username)
    task_list_string = TaskSchema().dump(task_list, many=True)
    print(type(task_list_string))
    return jsonify({"TaskList": task_list_string}), 200


@api.route('/listTaskPagination')
@jwt_required()
def list_task_pagination():
    """
    Lists tasks for the current user, with pagination. The page number and 
    limit per page can be specified as query parameters. Returns paginated 
    tasks in JSON format, including total task count.
    """
    user_data = current_user

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit  # Calculate offset for SQL query

    paginated_tasks = TaskReminder.find_task_by_username_pagination(username=user_data.username, page=page,
                                                                    pageSize=limit)
    task_list_serialized = TaskSchema().dump(paginated_tasks.items, many=True)

    return jsonify({

        "TaskList": task_list_serialized,
        "totalTasks": paginated_tasks.total

    }), 200


@api.route('/removeTask/<task_id>')
@jwt_required()
def remove_task(task_id):
    """
    Removes a specific task, identified by its task ID, for the current user. 
    Performs a check to ensure that the task belongs to the user. Returns JSON 
    indicating success or failure of the operation.
    """
    # Get the current user, check to make sure the supplied taskID belongs to them
    print("beginning removeTask")
    user_data = current_user
    current_task = TaskReminder.query.get(task_id)
    if current_task is not None and user_data.username == current_task.owner_username:
        print(f"[api/removeTask] {user_data.username} is the owner, removing task {task_id}")
        try:
            current_task.remove()
            print("ending removeTask")
            return jsonify({'Message': "remove_success", "task_id": task_id})
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return jsonify({'Message': "remove_fail", 'Error': str(e), "task_id": task_id})
    else:
        return jsonify({'Message': "remove_fail", 'Error': f'Task [{task_id}] was not found, or permission denied'})


@api.route('/completeTask/<task_id>', methods=["GET"])
@jwt_required()
def complete_task(task_id):
    """
    Marks a specific task, identified by its task ID, as complete for the current 
    user. Checks for task existence and ownership before updating. Returns JSON 
    indicating the result of the operation.
    """
    
    current_task = TaskReminder.query.get(task_id)

    if current_task is None:
        return jsonify({'Message': 'Task not found or not authorized'}), 404

    if current_task.task_completed is True:  # if recurring, make sure we allow this
        return jsonify({'Message': "Task was already marked complete!"})
    else:
        try:
            current_task.set_task_complete()
            return jsonify({'Message': "successfully marked complete.", "task_id": task_id})
        except Exception as e:
            print(e)
            return jsonify({'Message': "Failed to mark task as complete.", "task_id": task_id})


@api.route('/editTask/<task_id>', methods=['PUT'])
@jwt_required()
def edit_task(task_id):
    """
    Modifies an existing task for the current user. The task is identified by 
    its task ID. Expects JSON input for the fields to be updated. Performs validation 
    on input data and returns JSON indicating success or failure, including error messages.
    """
    user_data = current_user
    task = TaskReminder.query.get(task_id)
    error = []
    status_code = 200  # Default to 200, will be changed to 400 if errors are found.

    # Check if the task exists and if it belongs to the current user.
    if task is None or task.owner_username != user_data.username:
        return jsonify({'Message': 'Task not found or not authorized'}), 404

    # Get updated data from the request.
    data = request.json
    new_due_date = data.get('task_dueDate')
    new_reminder_off_set = data.get('task_reminderOffSetTime')

    # Validate and format due date.
    due_formatted_date = None
    if new_due_date:
        due_formatted_date = format_date(new_due_date)
        if due_formatted_date is None:
            error.append("Due date received an invalid date format")
    else:
        error.append("task_dueDate is required")

    # Validate and format reminder offset time.
    offset_formatted_date = None
    if new_reminder_off_set:
        offset_formatted_date = format_date(new_reminder_off_set)
        if offset_formatted_date is None:
            error.append("Offset time date received an invalid date format")
    else:
        error.append("task_reminderOffSetTime is required")

    # Check if offset is not after the due date.
    if due_formatted_date and offset_formatted_date and offset_formatted_date > due_formatted_date:
        error.append("Offset must not be after your due date!")

    # Update task if no errors.
    if not error:
        if new_due_date:
            task.task_dueDate = due_formatted_date
        if new_reminder_off_set:
            task.task_reminderOffSetTime = offset_formatted_date
        if 'task_description' in data:
            task.task_description = data['task_description']
        if 'task_emailList' in data:
            task.task_emailList = data['task_emailList']
        if 'task_name' in data:
            task.task_name = data['task_name']

        # Commit the changes to the database.
        try:
            db.session.commit()
            return jsonify({'Message': 'Task updated successfully', 'task_id': task_id}), status_code
        except Exception as e:
            # Rollback in case of error.
            db.session.rollback()
            error.append(str(e))

    # Return errors if any.
    return jsonify({'Message': 'Failed to update task', 'Error': error}), 400 if error else status_code


# TODO: Do not believe we're using these last three functions
####
@api.route('/getTask/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """
    Fetches a single task by its ID for the current user. Checks for task existence 
    and ownership. Returns the task data as JSON, serialized using TaskSchema.
    """
    task = TaskReminder.query.get(task_id)

    if task is None:
        return jsonify({'Message': 'Task not found'}), 404

    if task.owner_username != current_user.username:
        return jsonify({'Message': 'Unauthorized'}), 401

    task_data = TaskSchema().dump(task)
    return jsonify({"Task": task_data}), 200


# Return users, /api/get_users?page=1&per_page=5 as an example
@api.route('/get_users', methods=['GET'])
@jwt_required()
def get_users():
    """
    Fetches a list of users with pagination. Intended for admin users. The page 
    number and items per page can be specified as query parameters. Returns user 
    data in JSON format.
    """
    jwt_info = get_jwt()
    if jwt_info.get('is_admin'):

        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=3, type=int)

        users = User.query.paginate(
            page=page,
            per_page=per_page
        )
        json_users = UserSchema().dump(users, many=True)
        return jsonify({
            "users": json_users
        }), 200
    else:
        return jsonify({"message": "User unauthorized"}), 401


def format_date(string_date):
    """
    Converts a date string into a datetime object. Supports two date string formats: 
    'MM/DD/YYYY HH:MM' and ISO format 'YYYY-MM-DDTHH:MM:SS'. Returns a datetime object 
    or None if the input string does not match the expected format.
    """
    pattern = r"^(0?[1-9]|1[0-2])\/(0?[1-9]|[12][0-9]|3[01])\/(20\d{2})\s([01]?[0-9]|2[0-3]):([0-5][0-9])$"
    match = re.match(pattern, string_date)
    try:
        if match:
            return datetime.datetime.strptime(string_date, f'%m/%d/%Y %H:%M')
        else:
            return datetime.datetime.strptime(string_date, f'%Y-%m-%dT%H:%M:%S')
    except Exception as e:
        print(f'Failed to parse date {e}')
####### TODO: see statement above ^
