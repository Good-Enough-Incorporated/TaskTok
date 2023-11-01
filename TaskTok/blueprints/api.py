from flask import Blueprint, jsonify, request
from TaskTok.models import User, taskReminder
from flask_jwt_extended import jwt_required, get_jwt, current_user
import datetime
from TaskTok.schema import UserSchema
from RemindMeClient.task import send_email, create_file
from RemindMeClient import task as cTask
import datetime
api = Blueprint('api', __name__)

@api.route('/addTask')
@jwt_required()
def addTask():
    #get the current user's information
    userData = current_user
    
    task = taskReminder(owner_username=userData.username, task_dueDate=datetime.datetime.now(), task_description="Hello, this is the reminder of the example task", task_name="My Task!", task_message="This is the message")
    task.add()
    return "Added task to the database"

@api.route('/listTask')
def listTask():
    #send_email.delay()
    result = cTask.add.delay(1,2)
    print(result)
    
    #create_file.delay("test.txt", "another test!")
    
    return "Ran test task!"
@api.route('/removeTask')
def removeTask():
    return "removeTask"
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
