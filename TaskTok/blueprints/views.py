"""
views.py serves as the main python program
for all views (except auth related stuff)

routes for /, /order, /info, etc
"""

from flask import Blueprint
from flask import render_template, url_for, request, redirect
from flask_jwt_extended import jwt_required, current_user, get_csrf_token
from TaskTok.forms import LoginForm
from TaskTok.extensions import side_nav_menu_items
#  ----------- Unused imports: Needs review --------------
#  from TaskTok.Server import create_app
# from flask import current_app
# from flask import session
#  import requests

views = Blueprint('views', __name__)



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
    
    cookies = {'access_token_cookie': request.cookies.get('access_token_cookie')}
    # response = requests.get(url_for('auth.getCurrentUser',_external=True), cookies=cookies)

    return render_template('home.html', username=current_user.username, sideNavMenuItems=side_nav_menu_items)

@views.route('/admin')
def admin():
    return 'admin page not built yet'

@views.route('/profile')
#Sidenav menu in Settings page that allows user to return home/logout
@jwt_required()
def profile():
    # check for JWT in cookie

    cookies = {'access_token_cookie': request.cookies.get('access_token_cookie')}
    # response = requests.get(url_for('auth.getCurrentUser',_external=True), cookies=cookies)

    return render_template('profile.html', username=current_user.username, sideNavMenuItems=side_nav_menu_items)


@views.route('/userProfile', methods=['GET', "POST"])
@jwt_required()
def userProfile():

    access_token_cookie = request.cookies.get('access_token_cookie')
    user_csrf_token = get_csrf_token(access_token_cookie)
    if request.method == 'POST':
        print("POST")
        return render_template('profile.html', username='test', email='test@gmail.com', csrf_token= user_csrf_token)
    else:
        print("GET")
    #compare if changed
    #if changed update
    return render_template('profile.html', username='test', email='test@gmail.com', csrf_token= user_csrf_token, sideNavMenuItems=side_nav_menu_items)

