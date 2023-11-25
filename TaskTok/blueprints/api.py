from flask import Blueprint, jsonify, request
from TaskTok.models import User, taskReminder
from TaskTok.extensions import db
from flask_jwt_extended import jwt_required, get_jwt, current_user
from TaskTok.schema import UserSchema, TaskSchema
from RemindMeClient.task import send_email
from sqlalchemy.exc import SQLAlchemyError
import datetime

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
    send_email.delay('jason.supple.27@gmail.com', "Test Subject", "Test Body")
    # create_file.delay('test.txt', "hello world")
    return 'send_email celery task created :)'


@api.route('/addTask')
@jwt_required()
def add_task():
    # get the current user's information
    user_data = current_user

    task = taskReminder(owner_username=user_data.username, task_dueDate=datetime.datetime.now(),
                        task_description="Hello, this is the reminder of the example task", task_name="My Task!",
                        task_message="This is the message")
    task.add()
    return jsonify({"Message": "Added task to the database", "UserData": user_data.username})


@api.route('/listTask')
@jwt_required()
def list_task():
    # TODO: Probably need to returned a paged list for a lot of tasks
    user_data = current_user
    task_list = taskReminder.findTaskByUsername(username=user_data.username)
    task_list_string = TaskSchema().dump(task_list, many=True)
    return jsonify({"TaskList": task_list_string}), 200

    # create_file.delay("test.txt", "another test!")


@api.route('/removeTask/<taskID>')
@jwt_required()
def remove_task(task_id):
    # Get the current user, check to make sure the supplied taskID belongs to them
    # TODO: Need to make sure <taskID> is safe
    print("beginning removeTask")
    user_data = current_user
    current_task = taskReminder.query.get(task_id)
    if current_task is not None and user_data.username == current_task.owner_username:
        print(f"[api/removeTask] {user_data.username} is the owner, removing task {task_id}")
        try:
            current_task.remove()
            print("ending removeTask")
            return jsonify({'Message': "remove_success"})
        except SQLAlchemyError as e:
            print(f"Database error occurred: {e}")
            return jsonify({'Message': "remove_fail", 'Error': str(e)})


# TODO: Need input validation. Waiting for Bootstrap to be setup for full functionality.
@api.route('/editTask/<task_id>', methods=['PUT'])
@jwt_required()
def edit_task(task_id):
    user_data = current_user
    task = taskReminder.query.get(task_id)

    # Check if the task exists and if it belongs to the current user.
    if task is None or task.owner_username != user_data.username:
        return jsonify({'Message': 'Task not found or not authorized'}), 404

    # Get updated data from the request.
    data = request.json
    new_name = data.get('task_name')
    new_description = data.get('task_description')
    new_due_date = data.get('task_dueDate')
    new_reminder_off_set = data.get('task_reminderOffSet')
    new_email_list = data.get('task_emailList')
    # TODO: Validate these inputs as safe

    # Getting new description.
    if new_description is not None:
        task.task_description = new_description

    # Getting new due date.
    if new_due_date is not None:
        try:
            print(f"DUE DATE = {new_due_date}")
            task.task_dueDate = datetime.datetime.strptime(new_due_date, f'%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return jsonify({'Message': 'Invalid date format'}), 400

    if new_reminder_off_set is not None:
        try:
            task.task_reminderOffSetTime = datetime.datetime.strptime(new_reminder_off_set, f'%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return jsonify({'Message': 'Invalid date format'}), 400

    if new_email_list is not None:
        task.task_emailList = new_email_list

    # Getting new name for task.
    if new_name is not None:
        task.task_name = new_name

    # Commit the changes to the database
    try:
        db.session.commit()
        return jsonify({'Message': 'Task updated successfully'}), 200
    except Exception as e:
        # Rollback in case of error.
        db.session.rollback()
        return jsonify({'Message': 'Failed to update task', 'Error': str(e)}), 500


@api.route('/')
def get_tasks():
    return "something"


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
