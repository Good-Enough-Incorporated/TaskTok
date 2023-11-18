"""
auth.py serves as the authentication python program
for all auth related functions

routes for /auth, /updatepassword, etc
"""

from flask import Blueprint, jsonify, request, flash, render_template, redirect, url_for, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp
from flask_jwt_extended import (create_access_token, create_refresh_token, 
                                jwt_required, get_jwt_identity, set_access_cookies, 
                                set_refresh_cookies, unset_jwt_cookies)
from sqlalchemy.exc import OperationalError
from functools import wraps
from TaskTok.models import User, NoNoTokens
from TaskTok.extensions import db
from TaskTok.functions import generate_email_token, verify_email_token
import re

auth = Blueprint("auth", __name__)

#with app.app_context():
#kc = current_app.config['kc']
CALLBACK_URL = f"http://192.168.1.26/kc/callback"
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$)")



class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=4, max=12),
        Regexp('^(?=.*[a-zA-Z])[a-zA-Z0-9]*$', message='Username must contain at least one letter.')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    submit = SubmitField('Sign Up')

def is_email_valid(email):
    return EMAIL_REGEX.match(email)

def create_user(username, email, password):
    new_user = User(username=username, email=email)
    new_user.setPassword(password)
    new_user.add()
    return new_user

def get_user_by_username(username):
    try:
        return User.getUserByUsername(username=username)
    except OperationalError:
        raise Exception("Database setup not complete. Don't forget to create your database ;)")


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
            try: 
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
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
        newuser_email = request.form.get('email').lower()
        newuser_password = request.form.get('password')

        if get_user_by_username(newUser_username):
            flash('Username already exists. Please login', 'error')
            return render_template('register.html', form=form)
        

        if not is_email_valid(newuser_email):
            flash('Invalid email format', 'error')
            return render_template('register.html', form=form)
        
        new_user = create_user(newUser_username, newuser_email, newuser_password)
        # send verification  email with the token generated.
        token = generate_email_token(new_user.email)

        flash("Account Created! Please verify your email.", 'success')
        return redirect(url_for('auth.register'))
    else:
        # Checking form errors and handling them.
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'error')
        
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
            return redirect(url_for("auth.login", next=request.url))
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
