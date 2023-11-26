"""
auth.py serves as the authentication python program
for all auth related functions

routes for /auth, /update_password, etc
"""

from TaskTok.models import User
from flask import Blueprint
from flask import jsonify
from flask.helpers import url_for, request, flash, session
from werkzeug.utils import redirect
from flask import render_template, make_response
from functools import wraps
from flask_jwt_extended import create_access_token, create_refresh_token, \
    jwt_required, get_jwt, current_user, \
    get_jwt_identity, set_access_cookies, \
    set_refresh_cookies, unset_jwt_cookies
from TaskTok.models import NoNoTokens
from TaskTok.extensions import db
from TaskTok.functions import generate_email_token, verify_email_token
from sqlalchemy.exc import OperationalError
from TaskTok.forms import NewUserForm, LoginForm, ResetPasswordForm
from datetime import timedelta
from RemindMeClient.task import send_email

#  ------------ Unused imports: Needs review -----------------
#  from passlib.hash import sha256_crypt
#  from flask.helpers import prepare_send_file_kwargs
#  from flask import current_app, Response
#  import re
#  import datetime
#  import fileinput
# import sys
# import os
# from os.path import exists
#  --------------------------------------------------------------

auth = Blueprint("auth", __name__)

# with app.app_context():
# kc = current_app.config['kc']
callback_URL = f"http://192.168.1.26/kc/callback"


@auth.route('/verify_email/<token>')
def verify_email(token):
    # check the token, if valid lookup the user via email and verify their
    # account
    token_email = verify_email_token(token)

    if not token_email:
        return "Invalid or expired token received."

    non_verified_user = User.search_email_address(email=token_email)
    if non_verified_user is not None:
        if non_verified_user.is_account_verified() is False:
            non_verified_user.verify_email_address()
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
        else:
            return "Email was already verified!"

    else:
        return "Verification failed - Unknown E-Mail"
        # valid token, but couldn't find the user?

    return 'verified email'


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = NewUserForm()
    error = None

    if request.method == "GET":
        return render_template('register.html', form=form)

    if form.validate_on_submit():
        new_user_username = request.form.get('username').lower()
        new_user_password = request.form.get('password')
        new_user_email = request.form.get('email').lower()

        print(f"Username = {new_user_username}")
        user = User.get_user_by_username(username=new_user_username)
        print(user)
        if user is not None:
            # return json if application/json later
            # return jsonify({"Error":"User already exists"}), 403
            error = 'user already exists'
            flash(error, 'error')
            return render_template('register.html', form=form)
        email = User.search_email_address(email=new_user_email)

        if email is not None:
            print('email already exists')
            error = 'Email already exists. Please login with username'
            flash(error, 'error')
            return render_template('register.html', form=form)

        new_user = User(username=new_user_username,
                        email=new_user_email)
        new_user.set_password(password=new_user_password)
        new_user.add()

        token = generate_email_token(new_user.email)
        # generate the email template
        verification_url = url_for(
            'auth.verify_email',
            _external=True,
            token=token)
        email_body = render_template(
            'email/verifyEmail.html',
            verificationLink=verification_url,
            username=new_user.username)

        try:
            send_email.delay(
                new_user.email,
                "TaskTok - Verification Required",
                email_body)
        except Exception as e:
            print(f"An error occured: {e}")
            print(email_body)
            print(
                'Looks like we couldnt send the job to the message broker Are '
                'you running on linux with Redis '
                'installed?')
            print('Anyways, here is the email template I tried sending out '
                  '(for testing)')

        # return jsonify({"Message": f"Created {new_user}"}), 200
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


@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == "GET":
        return redirect(url_for("views.main_page"))

    form_input = request.form
    form = LoginForm(form_input)
    if form.validate_on_submit():
        form_username = request.form.get('username').lower()
        form_password = request.form.get('password')
        remember_me = request.form.get('rememberMe')

        try:
            user = User.get_user_by_username(username=form_username)
        except OperationalError as e:
            print('Failed to authenticate user: %s', e)
            return "TODO: Make this pretty and give an error code for setup " \
                "not complete... Please create your database using flask cli:"\
                " flask createDB | flask makeAdminUser "

        if user and (user.verify_password(password=form_password)):
            # Set expiration time based on whether 'remember me' is checked
            expiration_hours = 720 if remember_me == 'on' else 1
            expiration_time = timedelta(hours=expiration_hours)

            access_token = create_access_token(
                identity=user, expires_delta=expiration_time)
            refresh_token = create_refresh_token(
                identity=user, expires_delta=expiration_time * 2)
            response = redirect(url_for('views.home'))

            max_age_seconds = int(expiration_time.total_seconds())
            set_access_cookies(response, access_token, max_age=max_age_seconds)
            set_refresh_cookies(
                response,
                refresh_token,
                max_age=max_age_seconds * 2)

            return response
        else:
            error = "Invalid username or password."
            flash(error, 'error')
            return render_template('loginPage.html', form=form)
    else:
        if form.password.errors:
            error = form.password.errors[0]
        if form.username.errors:
            error = form.username.errors[0]
        flash(error, 'error')
    return render_template('loginPage.html', form=form)


@auth.route('/loginAPIUser', methods=['POST'])
def login_api_user():
    request_information = request.get_json()
    # attempt to find the user passed by the login endpoint
    user = User.get_user_by_username(username=request_information.get('username'))
    if user and (user.verify_password(password=request_information.get('password'))):
        access_token = create_access_token(identity=user)  # was username
        refresh_token = create_refresh_token(identity=user)  # was username

        return jsonify(
            {
                "message": "User authenticated!",
                "tokens": {
                    "AccessToken": access_token,
                    "RefreshToken": refresh_token
                }
            }
        ), 200
    else:
        return jsonify(
            {
                "message": "invalid username or password"
            }
        ), 403


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@auth.route('/getCurrentUser')
@jwt_required()
def get_current_user():
    return jsonify({"message": "useraccount", "user_details": {
        "username": current_user.username, "email": current_user.email}})


@auth.route('/refreshAccessToken')
@jwt_required(refresh=True)
def refresh_access_token():
    # token may be expired, so we can't use current_user
    # therefore, we use get_jwt_identity() to get the username
    username = get_jwt_identity()
    # create_access_token needs to User object, not just the username, so
    # query the user
    user_object = User.query.get(username)
    # create a new access token.
    access_token = create_access_token(identity=user_object)
    return jsonify({"message": access_token})


@auth.route('/logout')
@jwt_required()
def logout():
    accept_header = request.headers.get('Accept', '')
    response = make_response()
    jwt = get_jwt()
    jti = jwt['jti']
    blocked_token = NoNoTokens(jti=jti)
    blocked_token.add()
    if 'application/json' in accept_header:
        response.data = jsonify(
            {"Message": "Log Out Successful", "token_info": "token_revoked"})
        response.status_code = 200
        response.content_type = 'application/json'

    else:
        response.data = render_template("error/loggedOut.html")
        response.status_code = 200
        response.content_type = 'text/html'
    # set the access token to null, otherwise if they keep going
    # to protected pages, they'll get session expired.
    # this will set up future requests to say not authenticated
    # (or redirect to login)
    # response.set_cookie("access_token_cookie", "", max_age=0)
    unset_jwt_cookies(response=response)

    return response, 200


@auth.route('/forgotPassword', methods=['GET', 'POST'])
def forgot_password():
    form = ResetPasswordForm()
    error = None
    if request.method == 'POST':
        
        email = request.form.get('email')
        #check if the email actually exists in our db
        user = User.search_email_address(email=email)
        if user is not None:
            token = generate_email_token(email=email)
            verification_url = url_for(
            'auth.reset_password',
            _external=True,
            token=token)
            print(verification_url)
            email_body = render_template('email/resetPasswordEmail.html', token=token, username=user.username, verificationLink=verification_url, form=form) 
            print('sending email')
            send_email.delay(
                email,
                "TaskTok - Password Reset",
                email_body)
            flash("If an account with this email is found, we'll send a link with instructions on how to reset your password", 'error')
            return render_template('forgotPassword.html')
        print("i didn't find this account")
    return render_template('forgotPassword.html')

@auth.route('/resetPassword/<token>', methods=['GET','POST'])
def reset_password(token):

    token_email = verify_email_token(token)
    if not token_email:
        return "Invalid or expired token received."
    non_verified_user = User.search_email_address(email=token_email)
    # we need to provide the token in a hidden text field so the user submits their token 
    # with their POST 
    form = ResetPasswordForm(request.form)
    error = None
    
    print('At resetPassword route')
    if request.method == 'POST':
        print('POST')
        if form.validate_on_submit():
            print("Validating on submit")
            password = request.form.get('password')
            password_confirm = request.form.get('password_confirm')
            token_email = verify_email_token(token)
            user = User.search_email_address(email=token_email)
            user.set_password(password)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)
            flash('Your password was successfully reset!')
        else:
            if form.password.errors:
                error = form.password.errors[0]
            if form.confirm_password.errors:
                error = form.confirm_password.errors[0]
            flash(error, 'error')

    return render_template("resetPassword.html", token=token, form=form, login_url = url_for('auth.login'))
