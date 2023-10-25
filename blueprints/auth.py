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
from models import User
from os.path import exists
from flask import Blueprint
from flask import jsonify
from passlib.hash import sha256_crypt
from flask.helpers import _prepare_send_file_kwargs, url_for, request, flash, session
from werkzeug.utils import redirect
from flask import render_template, current_app, Response
from functools import wraps
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, current_user

from extensions import db


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
def loginUser():
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


@auth.route('/loginOld', methods=['GET'])
def login():
    """ Initiate authentication """
    print(f"Current Callback_URI={kc.callback_uri}")
    #kc.callback_uri = 'http://192.168.1.26/kc/callback'
    try:
        url, state = kc.login()
        session['state'] = state
        return redirect(url)
    except:
        return f"Unable to redirect to Keycloak"


@auth.route('/getCurrentUser')
@jwt_required()
def getJWTInfo():
    
    return jsonify({"message": "useraccount", "user_details": {"username": current_user.username, "email": current_user.email}})







@auth.route('/logout')
def logout():
    if 'access_token' in session:
        try:
            logout_response = kc.logout(access_token=session['access_token'], refresh_token=session['refresh_token'])
            #session.clear()  # Clear the user session
            #session["logged_in"] = False
            return "logged out"
        except Exception as e:
            #logging.error("Error during logout: %s", str(e))
            return jsonify({"error": "Logout failed"}), 500
    else:
        #logging.warning("No refresh token found in session")
        return jsonify({"error": "No session found"}), 400





def loginOld():
    """
    route to login our guests.
    """
    homeurl = url_for("views.home")
    nav = [{"name": "Home", "url": homeurl}]
    password_correct_flag = False
    login_required = False
    error = None
    session.pop("_flashes", None)

    if request.args.get("next") is not None:
        login_required = True

    if request.method == "POST":

        if session.get("is_loggedin", None) is True:
            login_required = True
            print(request.args.get("next"))
            return redirect(request.args.get("next"))
        else:
            login_username = request.form.get("username")
            login_password = request.form.get("password")
            error = None
            if len(login_username) == 0:
                error = "Please enter your username"
            if len(login_password) == 0:
                if error is not None:
                    error = error + " and password"
                else:
                    error = "Please enter your password"
            if error is None:
                # if user gives us a valid username/password,
                # check if there are any user accounts(passfile exists), then validate login.

                if not exists(os.path.join(sys.path[0], "passfile")):
                    error = "No accounts found. Please register first!"
                else:
                    # do login check
                    print("checking login")
                    print(login_password)
                if validate_password(
                    os.path.join(sys.path[0], "passfile"),
                    login_username,
                    login_password,
                ):
                    print("running refactored password def")
                    print("Password correct!")
                    password_correct_flag = True
                    session["is_loggedin"] = True
                    session["username"] = login_username

            if error is None:
                if password_correct_flag:
                    flash("You've entered the correct password... redirecting.")
                    if request.args.get("next") is None:
                        # if user went directly to /auth,
                        #  there's no next to redirect them to...
                        # so go to / page
                        return redirect(url_for("views.home"))
                    return redirect(request.args.get("next"))
                else:
                    flash("Incorrect username/password. Please try again.")
                    # lets log it for security reasons
                    with open(os.path.join(sys.path[0], "failed_login.txt"), "a") as f:
                        log_string = (
                            "["
                            + str(datetime.datetime.now())
                            + "] "
                            + "failed login from IP:"
                            + request.remote_addr
                        )
                        f.writelines(log_string)
                        f.writelines("\n")

    if error is not None:
        flash(error)
    print("before returning, login_required= " + str(error))
    return render_template(
        "auth.html",
        pythondatetime=datetime.datetime.now(),
        nav=nav,
        request=request,
        login_required=login_required,
    )

