
from flask import Flask, jsonify, request, render_template, make_response, flash, url_for
from flask_jwt_extended import set_access_cookies, create_access_token, get_jwt, get_jwt_identity
from .extensions import db, jwtManager, flaskMail, update_celery
from .models import User, NoNoTokens
from flask_migrate import Migrate
from RemindMeClient.celeryManager import celery_init_app
from datetime import timedelta, timezone, datetime
from dotenv import load_dotenv
from TaskTok.forms import LoginForm
from TaskTok.extensions import side_nav_menu_items
import os
from flask_wtf.csrf import CSRFProtect

#  -------------- Unused Imports: Needs Review ------------------
#  from .schema import UserSchema
#  from celery import Celery
#  from RemindMeClient import task
#  from flask_mail import Mail, Message
#  --------------------------------------------------------------
# TODO:maybe remove
# from flask_mail import Mail,Message
# from .schema import UserSchema
# from celery import Celery
# from RemindMeClient import task
url_generated = False

def create_app():
    app = Flask(__name__)
    load_dotenv()  
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    #app.config['SQLALCHEMY_ECHO'] = os.environ.get('SQLALCHEMY_ECHO')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = os.environ.get('JWT_TOKEN_LOCATION')
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_CSRF_CHECK_FORM'] = True
    app.config['WTF_CSRF_FIELD_NAME'] = 'flask_wtf_csrf_token'
    hours = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES'))
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(
        hours=hours)  # change hours to .001 to test session expires error
    app.config["broker_url"] = os.environ.get('broker_url') #celery doesn't like the CELERY_ prefix.
    app.config['result_backend'] = os.environ.get('result_backend') #celery doesn't like the CELERY_ prefix.
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS')
    app.config['MAIL_USERNAME'] = os.environ.get(
        'MAIL_USERNAME')  # Your Gmail address
    app.config['MAIL_PASSWORD'] = os.environ.get(
        'MAIL_PASSWORD')  # Your App Password

    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    # app.config['JWT_COOKIE_DOMAIN'] = 'tasktok.com'  # Set your domain here

    app.config.from_mapping(
        CELERY=dict(
            broker_url='redis://localhost',
            result_backend='redis://localhost',
            task_ignore_result=True,
        ),
    )

    db.init_app(app)  # Initialize the db extension with app
    jwtManager.init_app(app)
    #app.celery_app = celery_init_app(app)
    update_celery(celery_init_app(app))
    flaskMail.init_app(app)
    app.migrate = Migrate(app,db)

    # Register blueprints:
    from .blueprints import api as api_blueprint
    from .blueprints import auth as auth_blueprint
    from .blueprints import views as views_blueprint
    app.register_blueprint(api_blueprint.api, url_prefix='/api')
    app.register_blueprint(auth_blueprint.auth, url_prefix='/auth')
    app.register_blueprint(views_blueprint.views, url_prefix='/')

    csrf = CSRFProtect(app)

        #initialize our URLs for our nav items
    


    # source: https://flask-jwt-extended.readthedocs.io/en/stable/refreshing_tokens.html
    @app.after_request
    def refresh_expiring_jwts(response):

        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)

            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))

            if target_timestamp > exp_timestamp:
                # get_jwt_identity returns user_id
                # but currently assigning identity with user_object
                # probably need to change this to user_object.user_id
                user_id = get_jwt_identity()
                user_object = User.get_user_by_id(user_id=user_id)
                print(f'Reissuing token for [{user_object.username}]')
                access_token = create_access_token(identity=user_object)

                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("error/notFound.html"), 404

    @jwtManager.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwtManager.user_lookup_error_loader
    def failed_user_lookup(_jwt_header, jwt_data):
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
    def search_logged_in_user(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        print(identity)

        return User.query.get(identity)

    # additional claims for roles 'admin'?
    @jwtManager.additional_claims_loader
    def add_additional_claims(identity):
        # user = User.getUserById(user_id=identity)
        if identity.username == "admin":
            return {"is_admin": True}
        else:
            return {"is_admin": False}

    @jwtManager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        print('EXPIRED_TOKEN_CALLBACK')
        # TODO: Add flash message to show this error on the login page
        # This would be triggered if CSRF token isn't on page
        accept_header = request.headers.get('Accept', '')
        response = make_response()
        if 'application/json' in accept_header:
            response.data = jsonify({"Message": "Token has expired", "Error": "token_expired"})
            response.status_code = 401
            response.content_type = 'application/json'

        else:
            form = LoginForm()
            flash('Session expired - Please log in again.', category='error')
            response.data = render_template("loginPage.html", form=form)
            response.status_code = 401
            response.content_type = 'text/html'
        # set the access token to null, otherwise if they keep going to protect pages, they'll get session expired.
        # this will set up future requests to say not authenticated (or redirect to log in)
        response.set_cookie("access_token_cookie", "", max_age=0)
        return response

    @jwtManager.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"Message": "Signature validation failed", "Error": "token_invalid"}), 401

    @jwtManager.unauthorized_loader
    def unauthorized_token_callback(error):
        print(f"UNAUTHORIZED_TOKEN_CALLBACK - {error}")
        # TODO: Add flash message to show this error on the login page
        accept_header = request.headers.get('Accept', '')
        response = make_response()
        if 'application/json' in accept_header:
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
    def token_is_revoked_callback(jwt_header, jwt_data):
        jti = jwt_data['jti']

        token = db.session.query(NoNoTokens).filter(NoNoTokens.jti == jti).scalar()

        if token is not None:
            return True
        else:
            return False

    @jwtManager.revoked_token_loader
    def token_was_revoked(jwt_header, jwt_data):
        return jsonify({"Message": "The supplied token was revoked already", "Error": "token_revoked"}), 401

    return app
