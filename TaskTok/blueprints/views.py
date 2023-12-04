"""
views.py serves as the main python program
for all views (except auth related stuff)

routes for /, /order, /info, etc
"""
from pytz import all_timezones
from flask import Blueprint
from flask import render_template, url_for, request, redirect
from flask_jwt_extended import jwt_required, current_user, get_csrf_token
from TaskTok.forms import LoginForm, UpdateSettingsForm, AddTaskForm
from TaskTok.extensions import generate_links

from TaskTok.extensions import db
from TaskTok.models import User
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
    form = AddTaskForm()
    side_nav_menu_items = generate_links()
    cookies = {'access_token_cookie': request.cookies.get('access_token_cookie')}
    # response = requests.get(url_for('auth.getCurrentUser',_external=True), cookies=cookies)

    return render_template('home.html', username=current_user.username, sideNavMenuItems=side_nav_menu_items, form=form)

@views.route('/admin')
def admin():
    return 'admin page not built yet'


@views.route('/userSettings', methods=['GET', "POST"])
@jwt_required()
def userSettings():
    
    personal_information = {
        'username' : current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name
    }
    for key, value in personal_information.items():
        print(value)
        if value is None:
            personal_information[key] = ''
        
    access_token_cookie = request.cookies.get('access_token_cookie')
    token = get_csrf_token(access_token_cookie)
    form = UpdateSettingsForm()
    error = None
    side_nav_menu_items = generate_links()
    
      
    if request.method == 'POST':
        print("POST")
        
        if form.validate_on_submit():
            print('validating')
            submit_type = request.args.get('form_id')
            #using the form_id, we can check which portions to update
            if submit_type == 'update_information':

                username = request.form.get('username')
                email = request.form.get('email')
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')

                user = User.get_user_by_id(user_id=current_user.id)

                user.first_name = first_name
                user.last_name = last_name
                
                db.session.commit()
                return redirect(url_for('views.userSettings'))
            if submit_type == 'update_credentials':

                user = User.get_user_by_id(user_id=current_user.id)

                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                if user.verify_password(current_password):
                    #update their password
                    user.set_password(new_password)
        
    else:
        print("GET")
    #compare if changed
    #if changed update
    return render_template('profile.html', username=personal_information['username'],first_name=personal_information['first_name'],  last_name=personal_information['last_name'], email=personal_information['email'], form=form, csrf_token=token, sideNavMenuItems=side_nav_menu_items, timezones = all_timezones)

