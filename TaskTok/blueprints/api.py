from flask import Blueprint, jsonify, request
from TaskTok.models import User, TaskReminder
from TaskTok.extensions import db
from flask_jwt_extended import jwt_required, get_jwt, current_user
from TaskTok.schema import UserSchema, TaskSchema
from TaskTok.utilities import email_message, check_emails_overdue
from sqlalchemy.exc import SQLAlchemyError
import datetime
import re

# for testing API issues
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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


@api.route('/addTask', methods=['POST'])
@jwt_required()
def add_task():
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


@api.route('/editTask/<task_id>', methods=['PUT'])
@jwt_required()
def edit_task(task_id):
    logger.debug(f'Editing task with ID: {task_id}')

    user_data = current_user
    task = TaskReminder.query.get(task_id)
    error = []
    status_code = 200  # Default to 200, will be changed to 400 if errors are found

    # Check if the task exists and if it belongs to the current user.
    if task is None or task.owner_username != user_data.username:
        logger.warning(f'Task with ID {task_id} not found or not authorized for user {user_data.username}')
        return jsonify({'Message': 'Task not found or not authorized'}), 404

    # Get updated data from the request.
    data = request.json

    # Check if each field exists in the request data before updating
    if 'task_description' in data:
        new_description = data['task_description']
        logger.debug(f"Updating task description to: {new_description}")
        task.task_description = new_description

    if 'task_dueDate' in data:
        new_due_date = data['task_dueDate']
        if new_due_date:
            due_formatted_date = format_date(new_due_date)
            logger.debug(f"Received new due date: {new_due_date}")
            if due_formatted_date is not None:
                task.task_dueDate = due_formatted_date
                logger.debug(f"Formatted and updated due date to: {due_formatted_date}")
            else:
                error.append("Due date received an invalid date format")
                logger.warning("Invalid date format received for due date")
        else:
            error.append("task_dueDate is required")
            logger.warning("No due date provided")

    if 'task_reminderOffSetTime' in data:
        new_reminder_off_set = data['task_reminderOffSetTime']
        logger.debug(f"Received new reminder offset: {new_reminder_off_set}")
        if new_reminder_off_set:
            offset_formatted_date = format_date(new_reminder_off_set)
            if offset_formatted_date is not None:
                if task.task_dueDate < offset_formatted_date:
                    error.append("Offset must not be after your due date!")
                    logger.warning("Reminder offset is after the due date")
                else:
                    task.task_reminderOffSetTime = offset_formatted_date
            else:
                error.append("Offset time date received an invalid date format")
                logger.warning("Invalid date format received for reminder offset")
        else:
            # Uncomment the next two lines if task_reminderOffSetTime is required
            error.append("task_reminderOffSetTime is required")
            logger.warning("No reminder offset time provided")

    if 'task_emailList' in data:
        new_email_list = data['task_emailList']
        logger.debug(f"Updating email list to: {new_email_list}")
        task.task_emailList = new_email_list

    if 'task_name' in data:
        new_name = data['task_name']
        logger.debug(f"Updating task name to: {new_name}")
        task.task_name = new_name

    # TODO: Validate the inputs here.

    if error:
        status_code = 400
        logger.warning(f"Errors encountered while updating task: {error}")
        return jsonify({'Message': 'Failed to update task', 'Error': error}), status_code

    # Commit the changes to the database
    try:
        db.session.commit()
        logger.info(f"Task with ID {task_id} updated successfully")
        return jsonify({'Message': 'Task updated successfully'}), status_code
    except Exception as e:
        logger.error(f"Failed to update task with ID {task_id}: {e}")
        # Rollback in case of error.
        db.session.rollback()
        return jsonify({'Message': 'Failed to update task', 'Error': str(e)}), 500




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
