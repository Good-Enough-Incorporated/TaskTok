
#import logging

from flask import Flask, jsonify, request, render_template, make_response, flash
from flask_jwt_extended import set_access_cookies, create_access_token, get_jwt, get_jwt_identity

from .extensions import db, jwtManager,flaskMail

from .models import User, NoNoTokens
from .schema import UserSchema
from RemindMeClient.celeryManager import celery_init_app
from celery import Celery
from RemindMeClient import task
from datetime import timedelta, timezone, datetime
from dotenv import load_dotenv
import os
from TaskTok.forms import LoginForm
from flask_mail import Mail,Message



def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_ECHO'] = os.environ.get('SQLALCHEMY_ECHO')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = os.environ.get('JWT_TOKEN_LOCATION')
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    hours = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES'))
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=hours) #change hours to .001 to test session expires error
    #app.config["broker_url"] = os.environ.get('broker_url') #celery doesn't like the CELERY_ prefix.
    #app.config['result_backend'] = os.environ.get('result_backend') #celery doesn't like the CELERY_ prefix.
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS')
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Your Gmail address
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Your App Password

    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')     
    #app.config['JWT_COOKIE_DOMAIN'] = 'tasktok.com'  # Set your domain here

    app.config.from_mapping(
    CELERY=dict(
        broker_url='redis://localhost',
        result_backend='redis://localhost',
        task_ignore_result=True,
    ),
) 



    
    db.init_app(app)  # Initialize the db extension with app
    jwtManager.init_app(app)
    app.celery_app = celery_init_app(app)
    flaskMail.init_app(app)


    # Register blueprints:
    from .blueprints import api as api_blueprint
    from .blueprints import auth as auth_blueprint
    from .blueprints import views as views_blueprint
    app.register_blueprint(api_blueprint.api, url_prefix='/api')
    app.register_blueprint(auth_blueprint.auth, url_prefix='/auth')
    app.register_blueprint(views_blueprint.views, url_prefix='/')

#source: https://flask-jwt-extended.readthedocs.io/en/stable/refreshing_tokens.html
    @app.after_request
    def refresh_expiring_jwts(response):
        
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        
            if target_timestamp > exp_timestamp:
                
                #get_jwt_identity returns id
                #but currently assigning identity with userObject
                #probably need to change this to userObject.id
                id = get_jwt_identity()
                userObject = User.get_user_by_id(user_id=id)
                print(f'Reissuing token for [{userObject.username}]')
                access_token = create_access_token(identity=userObject)
               
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response

    @app.errorhandler(404)
    def pageNotFound(error):
        return render_template("error/notFound.html"),404

    @jwtManager.user_identity_loader
    def UserIdentityLookup(user):
        return user.id
    
    @jwtManager.user_lookup_error_loader
    def FailedUserLookup(_jwt_header, jwt_data):
        response = make_response()
        response.content_type = 'text/html'
        response.status_code = 404
        response.set_cookie("access_token_cookie", "", max_age=0)
        response.set_cookie("refresh_token_cookie", "", max_age=0)
        response.set_cookie("csrf_access_token", "", max_age=0)
        response.set_cookie("csrf_refresh_token", "", max_age=0)
        response.data = render_template('error/accountDeleted.html')
        return response
    
    @jwtManager.user_lookup_loader
    def searchLoggedInUser(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        print(identity)
           
        return User.query.get(identity)
        
    #additional claims for roles 'admin'?
    @jwtManager.additional_claims_loader
    def addAdditionalClaims(identity):
       # user = User.getUserById(id=identity)
        if identity.username == "admin":
            return {"is_admin" : True}
        else:
            return {"is_admin" : False}

    @jwtManager.expired_token_loader
    def expiredTokenCallback(jwt_header, jwt_data):
        acceptHeader = request.headers.get('Accept','')
        response = make_response()
        if 'application/json' in acceptHeader:
            response.data = jsonify({"Message": "Token has expired", "Error": "token_expired"})
            response.status_code = 401
            response.content_type = 'application/json'
            
        else:
            form = LoginForm()
            flash('Session expired - Please log in again.', category='error')
            response.data = render_template("loginPage.html", form=form)
            response.status_code = 401
            response.content_type = 'text/html'
        #set the access token to null, otherwise if they keep going to protected pages, they'll get session expired.
        #this will set up future requests to say not authenticated (or redirect to login)
        response.set_cookie("access_token_cookie", "", max_age=0)
        return response
    
    @jwtManager.invalid_token_loader
    def expiredTokenCallback(error):
        return jsonify({"Message": "Signature validation failed", "Error": "token_invalid"}),401
    
    @jwtManager.unauthorized_loader
    def unauthorizedTokenCallback(error):
        acceptHeader = request.headers.get('Accept','')
        response = make_response()
        if 'application/json' in acceptHeader:
            response.data = jsonify({"Message": "API call missing a token", "Error": "token_missing"})
            response.status_code = 401
            response.content_type = 'application/json'
            
        else:
            form = LoginForm()
            response.data = render_template("loginPage.html", form=form)
            response.status_code = 401
            response.content_type = 'text/html'       
        return response


    @jwtManager.token_in_blocklist_loader
    def tokenIsRevokedCallback(jwt_header, jwt_data):
        jti = jwt_data['jti']

        token = db.session.query(NoNoTokens).filter(NoNoTokens.jti == jti).scalar()

        if token is not None:
            return True
        else: 
            return False
        
    @jwtManager.revoked_token_loader
    def tokenWasRevoked(jwt_header, jwt_data):
        return jsonify({"Message": "The supplied token was revoked already", "Error": "token_revoked"}),401


    


    return app
