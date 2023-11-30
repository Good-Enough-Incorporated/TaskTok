from flask import Blueprint, jsonify, request
from TaskTok.models import User, TaskReminder
from TaskTok.extensions import db
from flask_jwt_extended import jwt_required, get_jwt, current_user
from TaskTok.schema import UserSchema, TaskSchema
from TaskTok.utilities import email_message, check_emails_overdue
from sqlalchemy.exc import SQLAlchemyError
import datetime
import re
#  ---------- Unused Imports: Needs review ----------------
#  import subprocess
#  import socket
#  from RemindMeClient import task as cTask
#  from RemindMeClient.task import create_file
#  --------------------------------------------------------
api = Blueprint('api', __name__)


@api.route('/sendMail')
@jwt_required()
def send_mail():
    email_message('jason.supple.27@gmail.com', "Test Subject", "Test Body")
    # create_file.delay('test.txt', "hello world")
    return 'send_email celery task created :)'


@api.route('/testRoute')
def testRoute():
    # test route, will not be kept
    check_emails_overdue()
    return "testing check_emails_overdue()"


@api.route('/addTask', methods=['PUT'])
@jwt_required()
def add_task():
    # get the current user's information
    user_data = current_user
    # TODO: Need to validate as safe
    data = request.json

    task_name = data.get('task_name')
    task_description = data.get('task_description')
    task_due_date = data.get('task_dueDate')
    task_reminder_off_set = data.get('task_reminderOffSetTime')
    task_email_list = data.get('task_emailList')
    task_email_message = data.get('task_email_message')
    print(task_reminder_off_set)
    print(task_due_date)
    try:

        task_due_date = datetime.datetime.strptime(task_due_date, f'%Y-%m-%dT%H:%M:%S')
        task_reminder_off_set = datetime.datetime.strptime(task_reminder_off_set, f'%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return jsonify({'Message': 'add_failed', 'Error': "Invalid DateTime format received."}), 400

    if task_reminder_off_set > task_due_date:
        return jsonify({'Message': 'add_failed', 'Error': 'Reminder Offset must be before the due date.'}), 400

    task = TaskReminder(owner_username=user_data.username, task_dueDate=task_due_date,
                        task_description=task_description, task_reminderOffSetTime=task_reminder_off_set,
                        task_message=task_email_message, task_emailList=task_email_list, task_name=task_name)
    task.add()
    task_array = [task]
    task_string = TaskSchema().dump(task_array, many=True)
    return jsonify({"Message": "add_success", "TaskList": task_string, 'Error': 'None'}), 200


@api.route('/listTask')
@jwt_required()
def list_task():
    # TODO: Probably need to returned a paged list for a lot of tasks
    user_data = current_user
    task_list = TaskReminder.find_task_by_username(username=user_data.username)
    task_list_string = TaskSchema().dump(task_list, many=True)
    return jsonify({"TaskList": task_list_string}), 200

    # create_file.delay("test.txt", "another test!")


@api.route('/removeTask/<task_id>')
@jwt_required()
def remove_task(task_id):
    # Get the current user, check to make sure the supplied taskID belongs to them
    # TODO: Need to make sure <taskID> is safe
    # TODO: task should be UUID4, throw error message for invalid task type
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



# TODO: Need input validation.
# Waiting for Bootstrap to be setup for full functionality.
@api.route('/editTask/<task_id>', methods=['PUT'])
@jwt_required()
def edit_task(task_id):
    user_data = current_user
    task = TaskReminder.query.get(task_id)
    error = []
    status_code = None
    # Check if the task exists and if it belongs to the current user.
    if task is None or task.owner_username != user_data.username:
        return jsonify({'Message': 'Task not found or not authorized'}), 404

    # Get updated data from the request.
    data = request.json
    new_name = data.get('task_name')
    new_description = data.get('task_description')
    new_due_date = data.get('task_dueDate')
    new_reminder_off_set = data.get('task_reminderOffSetTime')
    new_email_list = data.get('task_emailList')
    # TODO: Validate these inputs as safe
    print(f'OFFSET = {data}')
    # Getting new description.
    if new_description is not None:
        task.task_description = new_description

    # Getting new due date.
    if new_due_date is not None:
        due_formatted_date = format_date(new_due_date)
        if format_date is not None:
            task.task_dueDate = due_formatted_date
        else:
            error.append("Due date received an invalid date format")
            

    if new_reminder_off_set is not None:
        offset_formatted_date = format_date(new_reminder_off_set)
        if format_date is not None:
            if due_formatted_date < offset_formatted_date:
                error.append("Offset must not be after your due date!")
            else:
                print(f'UPDATING OFFSET {new_reminder_off_set}')
                old_reminder_offset_time = task.task_reminderOffSetTime
                task.task_reminderOffSetTime = offset_formatted_date
        else:
            error.append("Offset time date received an invalid date format")
    else:
        print('new_reminder_off_set was None')
            
    

    if new_email_list is not None:
        task.task_emailList = new_email_list


    # Getting new name for task.
    if new_name is not None:
        task.task_name = new_name

    if error:
        status_code = 400
    else:
        status_code = 200
    # Commit the changes to the database
    try:
        db.session.commit()
        return jsonify({'Message': 'Task updated successfully', "Error": error}), status_code
    except Exception:
        # Rollback in case of error.
        db.session.rollback()
        return jsonify({'Message': 'Failed to update task', 'Error': error}), status_code


@api.route('/getTask/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    # Logic to fetch a single task by its ID
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
    pattern = r"^(0?[1-9]|1[0-2])\/(0?[1-9]|[12][0-9]|3[01])\/(20\d{2})\s([01]?[0-9]|2[0-3]):([0-5][0-9])$"
    match = re.match(pattern, string_date)
    try:
        if match:
            return datetime.datetime.strptime(string_date, f'%m/%d/%Y %H:%M')
        else:
            return datetime.datetime.strptime(string_date, f'%Y-%m-%dT%H:%M:%S')
    except Exception as e:
        print(f'Failed to parse date {e}')