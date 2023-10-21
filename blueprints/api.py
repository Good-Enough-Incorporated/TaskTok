from flask import Blueprint, jsonify, request


api = Blueprint('api', __name__)



@api.route('/')
def get_tasks():
    #db = current_app.extensions['sqlalchemy'].db
    return "something"

