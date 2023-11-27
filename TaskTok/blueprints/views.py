"""
views.py serves as the main python program
for all views (except auth related stuff)

routes for /, /order, /info, etc
"""

from flask import Blueprint
from flask import render_template, url_for, request, redirect
from flask_jwt_extended import jwt_required, current_user, get_csrf_token
from TaskTok.forms import LoginForm

#  ----------- Unused imports: Needs review --------------
#  from TaskTok.Server import create_app
# from flask import current_app
# from flask import session
#  import requests

views = Blueprint('views', __name__)
CURRENT_CAR_IMAGE = None


# our root route (home)
@views.route('/', methods=['GET'])
# need optional=True so we can check current_user to see if they're already authenticated.
@jwt_required(optional=True)
def main_page():
    """
    function for the main page. If the user is already authenticated, just send him to /home
    otherwise, make them login first.
    """
    # HEADERS = request.environ.get("SSL_CLIENT_CERT")
    print('im here')
    if current_user:
        print('User already authenticated')
        print('REDIRECTING TO views.home')
        return redirect(url_for('views.home'))

    login_form = LoginForm()
    print('User is not authenticated')
    print('rendering template loginPage')
    return render_template('loginPage.html', form=login_form)


@views.route('/home')
@jwt_required()
def home():
    # check for JWT in cookie
    side_nav_menu_items = [
        {'title': 'Home', 'url': url_for('views.home')},
        {'title': 'Settings', 'url': url_for('views.user_settings')},
        {'title': 'Admin', 'url': url_for('views.home')},
        {'title': 'Sign Out', 'url': url_for('auth.logout')},
    ]
    cookies = {'access_token_cookie': request.cookies.get('access_token_cookie')}
    # response = requests.get(url_for('auth.getCurrentUser',_external=True), cookies=cookies)

    return render_template('home.html', username=current_user.username, sideNavMenuItems=side_nav_menu_items)


@views.route('/user-settings', methods=['GET', "POST"])
@jwt_required()
def user_settings():
    # current_user.username
    # search User object using username
    # User.get_user_by_username(current_user.username)
    # user_email = User.email
    # user_username = User.username
    access_token_cookie = request.cookies.get('access_token_cookie')
    user_csrf_token = get_csrf_token(access_token_cookie)
    if request.method == 'POST':
        print("POST")
        return render_template('settings.html', username='test', email='test@gmail.com', csrf_token=user_csrf_token)
    else:
        print("GET")
    # compare if changed
    return render_template('settings.html', username='test', email='test@gmail.com', csrf_token=user_csrf_token)
