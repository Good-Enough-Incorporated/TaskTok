"""
views.py serves as the main python program
for all views (except auth related stuff)

routes for /, /order, /info, etc
"""

from flask import Blueprint
from flask import render_template, url_for, request, redirect
from flask_jwt_extended import jwt_required, current_user
from TaskTok.forms import LoginForm

#  ----------- Unused imports: Needs review --------------
#  from TaskTok.Server import create_app
# from flask import current_app
# from flask import session
#  import requests

views = Blueprint('views', __name__)
CURRENT_CAR_IMAGE = None


# our root route (home)
@views.route('/', methods=['GET', 'POST'])
# need optional=True so we can check current_user to see if they're already authenticated.
@jwt_required(optional=True)
def main_page():
    """
    function for the main page. If the user is already authenticated, just send him to /home
    otherwise, make them login first.
    """
    # HEADERS = request.environ.get("SSL_CLIENT_CERT")
    if current_user:
        print('User already authenticated')

        return redirect(url_for('views.home'))

    login_form = LoginForm()
    print('User is not authenticated')
    return render_template('loginPage.html', form=login_form)


@views.route('/home')
@jwt_required()
def home():
    # check for JWT in cookie
    side_nav_menu_items = [
        {'title': 'Home', 'url': url_for('views.home')},
        {'title': 'Profile', 'url': url_for('views.profile')},
        {'title': 'Admin', 'url': url_for('views.home')},
        {'title': 'Sign Out', 'url': url_for('auth.logout')},
    ]
    cookies = {'access_token_cookie': request.cookies.get('access_token_cookie')}
    # response = requests.get(url_for('auth.getCurrentUser',_external=True), cookies=cookies)

    return render_template('home.html', username=current_user.username, sideNavMenuItems=side_nav_menu_items)


@views.route('/profile')
def profile():
    return render_template('profile.html')


def request_current_user(access_token):
    api_endpoint = url_for("auth.get_current_user")
    return "test"


# Testing for Boostrap routing
@views.route('/test_bootstrap')
def test_bootstrap():
    return render_template('test_bootstrap.html')
