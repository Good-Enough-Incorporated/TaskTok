"""
views.py serves as the main python program
for all views (except auth related stuff)

routes for /, /order, /info, etc
"""

from flask import Blueprint, current_app
from flask import render_template, url_for, request, redirect, session
from flask_jwt_extended import jwt_required, current_user
from TaskTok.Server import create_app
views = Blueprint('views', __name__)
CURRENT_CAR_IMAGE = None
import requests



#our root route (home)
@views.route('/', methods=['GET','POST'])
def mainPage():
    """
    function for the home page
    """
    #If user clicked 'login' redirect to keycloak.
  
    #otherwise, render the mainPage
    return render_template('loginPage.html')


   
@views.route('/home')
@jwt_required()
def home():
    #check for JWT in cookie
    cookies = {'access_token_cookie': request.cookies.get('access_token_cookie')}
    #response = requests.get(url_for('auth.getCurrentUser',_external=True), cookies=cookies)
    
    
    

    return render_template('home.html', username=current_user.username)
        
        
    


def requestCurrentUser(accessToken):
    API_ENDPOINT = url_for("auth.get_current_user")
    return "test"
    
    