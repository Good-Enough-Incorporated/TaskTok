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
from flask import render_template, current_app, Response, make_response
from functools import wraps
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, current_user, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from TaskTok.models import NoNoTokens
from TaskTok.extensions import db
from TaskTok.functions import generate_email_token, verify_email_token
from sqlalchemy.exc import OperationalError
from TaskTok.forms import NewUserForm

auth = Blueprint("auth", __name__)

#with app.app_context():
#kc = current_app.config['kc']
callback_URL = f"http://192.168.1.26/kc/callback"

@auth.route('/verify_email/<token>')
def verify_email(token):
    #check the token, if valid lookup the user via email and verify their account
    tokenEmail = verify_email_token(token)
    
    if tokenEmail == False:
        return "Invalid or expired token received."
    
    nonVerifiedUser = User.searchEmailAddress(email=tokenEmail)
    if nonVerifiedUser is not None:
        if nonVerifiedUser.isAccountVerified() is False: 
            nonVerifiedUser.verifyEmailAddress()
            db.session.commit()
        else: 
            return "Email was already verified!"
        
    else:
        return "Verification failed - Unknown E-Mail"
        #valid token, but couldn't find the user?

    
    return 'verified email'


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = NewUserForm()
    if request.method == "GET":
        return render_template('register.html', form=form)

    #TODO: Enclose this in a validation block
    if form.validate_on_submit():
        newUser_username = request.form.get('username').lower()
        newuser_password = request.form.get('password')
        newuser_email = request.form.get('email').lower()
        print(f"Username = {newUser_username}")
        user = User.getUserByUsername(username=newUser_username)
        print(user)
        if user is not None:        
            #return json if application/json later
            #return jsonify({"Error":"User already exists"}), 403
            print('user already exists')
            error = 'Username already exists. Please login'
            flash(error, 'error')
            return render_template('register.html', form=form)
        #TODO: Need to finish validation for email and password
        new_user = User(username= newUser_username,
                   email = newuser_email    )
        new_user.setPassword(password=newuser_password)
        new_user.add()
        token = generate_email_token(new_user.email)
        print(f"TODO: Email this token to the email supplied. Accept the token a the endpoint /auth/verify_email/{token}")
        #return jsonify({"Message": f"Created {new_user}"}), 200
        print('Account Created!')
        flash("Account Created! Please login.", 'success')
        return redirect(url_for('auth.register'))
    else:
        if form.email.errors:
            error = form.email.errors[0]
        if form.password.errors:
            error = form.password.errors[0]
        if form.username.errors:
            error = form.username.errors[0]
        flash(error, 'error')
    return render_template('register.html', form=form)
    
@auth.route('/login',methods=['GET', 'POST'] )
def login():

    if request.method == "GET":
        return redirect(url_for("views.mainPage"))
    formUsername = request.form.get('username')
    formPassword = request.form.get('password')
    #attempt to find the user passed by the login endpoint
    try:
        user = User.getUserByUsername(username=formUsername)
    except OperationalError as e:
        return "TODO: Make this pretty and give an error code for setup not complete... Please create your database using flask cli: flask createDatabase | flask makeAdminUser"
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
    acceptHeader = request.headers.get('Accept','')
    response = make_response()
    jwt = get_jwt()
    jti = jwt['jti']
    blockedToken = NoNoTokens(jti=jti)
    blockedToken.add()
    if 'application/json' in acceptHeader:
        response.data = jsonify({"Message": "Log Out Successful", "token_info": "token_revoked"})
        response.status_code = 200
        response.content_type = 'application/json'
        
    else:
        response.data = render_template("error/loggedOut.html")
        response.status_code = 200
        response.content_type = 'text/html'
    #set the access token to null, otherwise if they keep going to protected pages, they'll get session expired.
    #this will set up future requests to say not authenticated (or redirect to login)
    #response.set_cookie("access_token_cookie", "", max_age=0)
    unset_jwt_cookies( response=response)
    return response,200
