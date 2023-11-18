from flask import Blueprint, jsonify, request
from TaskTok.models import User, taskReminder
from flask_jwt_extended import jwt_required, get_jwt, current_user
import datetime
from TaskTok.schema import UserSchema, TaskSchema
from RemindMeClient.task import send_email, create_file
from RemindMeClient import task as cTask
import datetime
import subprocess
import socket
api = Blueprint('api', __name__)


@api.route('/sendMail')
@jwt_required()
def sendMail():
    send_email.delay('jason.supple.27@gmail.com', "Test Subject", "Test Body")
    #create_file.delay('test.txt', "hello world")
    return 'send_email celery task created :)'

@api.route('/addTask')
@jwt_required()
def addTask():
    #get the current user's information
    userData = current_user
    
    task = taskReminder(owner_username=userData.username, task_dueDate=datetime.datetime.now(), task_description="Hello, this is the reminder of the example task", task_name="My Task!", task_message="This is the message")
    task.add()
    return jsonify({"Message": "Added task to the database", "UserData": userData.username} )

@api.route('/listTask')
@jwt_required()
def listTask():
    #TODO: Probably need to returned a paged list for a lot of tasks
    userData = current_user
    taskList = taskReminder.findTaskByUsername(username= userData.username)
    taskList_string = TaskSchema().dump(taskList, many=True)
    return jsonify({"TaskList": taskList_string}),200

    #create_file.delay("test.txt", "another test!")
    
    return "Ran test task!"
@api.route('/removeTask/<taskID>')
@jwt_required()
def removeTask(taskID):
    #Get the current user, check to make sure the supplied taskID belongs to them
    #TODO: Need to make sure <taskID> is safe
    print("beginning removeTask")
    userData = current_user
    currentTask = taskReminder.query.get(taskID)
    if currentTask is not None and userData.username == currentTask.owner_username:
        print(f"[api/removeTask] {userData.username} is the owner, removing task {taskID}")
        try:
            currentTask.remove()
            print("ending removeTask")
            return jsonify({'Message': "remove_success"})
        except Exception as e:
            #TODO:Log the removal error
            print("ending removeTask")
            return jsonify({'Message': "remove_fail"})
        
@api.route('/editTask/<taskID>', methods=['PUT'])
@jwt_required()
def editTask(taskID):
    userData = current_user
    task = taskReminder.query.get(taskID)

    # Checking if the task exists and belongs to the current user.
    if task is None or task.owner_username != userData.username:
        return jsonify({'Message': 'Task not found or not authorized'}), 404
    
    # Get the updated data from the request.
    data = request.json
    new_description = data.get('task_description')

        

        


@api.route('/')
def get_tasks():
    
    return "something"

#Return users, /api/get_users?page=1&per_page=5 as an example
@api.route('/get_users',methods=['GET'])
@jwt_required()
def get_users():
    jwtInfo = get_jwt()
    if jwtInfo.get('is_admin') == True:
       
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=3, type=int)
    
        users = User.query.paginate(
            page=page,
            per_page = per_page
        )
        jsonUsers = UserSchema().dump(users,many=True)
        return jsonify({
            "users": jsonUsers
        }),200
    else:
        return jsonify({"message": "User unauthorized"}),401



