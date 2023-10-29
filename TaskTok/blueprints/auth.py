"""
auth.py serves as the authentication python program
for all auth related functions

routes for /auth, /updatepassword, etc
"""
import re
import datetime
import fileinput
import sys
import os
from TaskTok.models import User
from os.path import exists
from flask import Blueprint
from flask import jsonify
from passlib.hash import sha256_crypt
from flask.helpers import _prepare_send_file_kwargs, url_for, request, flash, session
from werkzeug.utils import redirect
from flask import render_template, current_app, Response
from functools import wraps
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, current_user, get_jwt_identity, set_access_cookies, set_refresh_cookies
from TaskTok.models import NoNoTokens
from TaskTok.extensions import db


auth = Blueprint("auth", __name__)

#with app.app_context():
#kc = current_app.config['kc']
callback_URL = f"http://192.168.1.26/kc/callback"



@auth.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == "GET":
        count = User.getUserCount()
        return jsonify({"UserCount" : f"{count}"})




    registrationUserData = request.get_json()
    user = User.getUserByUsername(username=registrationUserData.get('username'))

    if user is not None:        
        return jsonify({"Error":"User already exists"}), 403
    
    
    new_user = User(username= registrationUserData.get('username'),
                email= registrationUserData.get('email')    )
    new_user.setPassword(password=registrationUserData.get('password'))
    new_user.add()
    return jsonify({"Message": f"Created {new_user}"}), 200

    
@auth.route('/login',methods=['POST'] )
def login():
    formUsername = request.form.get('username')
    formPassword = request.form.get('password')
    #attempt to find the user passed by the login endpoint
    user = User.getUserByUsername(username=formUsername)
    if user and (user.verifyPassword(password=formPassword)):
        accessToken = create_access_token(identity=user)#was username
        refreshToken = create_refresh_token(identity=user)#was username
        response = redirect(url_for('views.home'))
        set_access_cookies(response, accessToken)
        set_refresh_cookies(response, refreshToken)
        
        return response
    else: 
        return jsonify(
            {
                "message": "invalid username or password"
            }
        ),403

@auth.route('/loginAPIUser',methods=['POST'] )
def loginAPIUser():
    requestInformation = request.get_json()
    #attempt to find the user passed by the login endpoint
    user = User.getUserByUsername(username=requestInformation.get('username'))
    if user and (user.verifyPassword(password=requestInformation.get('password'))):
        accessToken = create_access_token(identity=user)#was username
        refreshToken = create_refresh_token(identity=user)#was username

        return jsonify(
            {
                "message": "User authenticated!",
                "tokens" : {
                    "AccessToken": accessToken,
                    "RefreshToken": refreshToken
                }            
            }
        ), 200
    else: 
        return jsonify(
            {
                "message": "invalid username or password"
            }
        ),403

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@auth.route('/getCurrentUser')
@jwt_required()
def getCurrentUser():
    
    return jsonify({"message": "useraccount", "user_details": {"username": current_user.username, "email": current_user.email}})



@auth.route('/refreshAccessToken')
@jwt_required(refresh=True)
def refreshAccessToken():
    #token may be expired, so we can't use current_user
    #therefore, we use get_jwt_identity() to get the username
    username = get_jwt_identity()
    #create_access_token needs to User object, not just the username, so query the user
    userObject = User.query.get(username)
    #create a new access token.
    accessToken = create_access_token(identity=userObject)
    return jsonify({"message": accessToken})



@auth.route('/logout')
@jwt_required()
def logout():
   jwt = get_jwt()
   jti = jwt['jti']
   blockedToken = NoNoTokens(jti=jti)
   blockedToken.add()
   return jsonify({"Message": "token_blocked"}),200
