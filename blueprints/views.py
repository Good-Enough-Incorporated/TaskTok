"""
views.py serves as the main python program
for all views (except auth related stuff)

routes for /, /order, /info, etc
"""
import datetime
from flask import Blueprint
from flask import render_template, url_for, request, redirect, session
views = Blueprint('views', __name__)
CURRENT_CAR_IMAGE = None



#our root route (home)
@views.route('/', methods=['GET','POST'])
def mainPage():
    """
    function for the home page
    """
    #If user clicked 'login' redirect to keycloak.
    if request.method == "POST":
        #TODO: Need to actually log the user in, for now redirect to example home
        #return redirect(url_for('auth.login'))
        return redirect(url_for('views.home'))
    #otherwise, render the mainPage
    return render_template('landingPage.html')


   
@views.route('/home')
def home():
    return render_template('home.html')