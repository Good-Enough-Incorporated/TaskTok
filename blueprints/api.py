from flask import Blueprint, jsonify, request
from models import User
from schema import UserSchema
api = Blueprint('api', __name__)



@api.route('/')
def get_tasks():
    
    return "something"

#Return users, /api/get_users?page=1&per_page=5 as an example
@api.route('/get_users',methods=['GET'])
def get_users():
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
