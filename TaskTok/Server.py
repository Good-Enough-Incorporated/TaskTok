
#import logging

from flask import Flask, jsonify, request

from .extensions import db, jwtManager
from .models import User, NoNoTokens
from .schema import UserSchema

#keycloak_client = Client('192.168.1.26/kc/callback')
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SECRET_KEY'] = r'HJDNUIWQEYH156345357564@@!@$'
    app.config['JWT_SECRET_KEY'] = r'CHANGEMELATER-JWTSECRET'
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    db.init_app(app)  # Initialize the db extension with app
    jwtManager.init_app(app)

    # Register blueprints:
    from .blueprints import api as api_blueprint
    from .blueprints import auth as auth_blueprint
    from .blueprints import views as views_blueprint
    app.register_blueprint(api_blueprint.api, url_prefix='/api')
    app.register_blueprint(auth_blueprint.auth, url_prefix='/auth')
    app.register_blueprint(views_blueprint.views, url_prefix='/')


    @jwtManager.user_identity_loader
    def UserIdentityLookup(user):
        return user.id
    
    @jwtManager.user_lookup_loader
    def searchLoggedInUser(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        print(identity)
           
        return User.query.get(identity)
        
    #additional claims for roles 'admin'?
    @jwtManager.additional_claims_loader
    def addAdditionalClaims(identity):
        
        if identity.username == "admin":
            return {"is_admin" : True}
        else:
            return {"is_admin" : False}

    @jwtManager.expired_token_loader
    def expiredTokenCallback(jwt_header, jwt_data):
        return jsonify({"Message": "Token has expired", "Error": "token_expired"}),401
    
    @jwtManager.invalid_token_loader
    def expiredTokenCallback(error):
        return jsonify({"Message": "Signature validation failed", "Error": "token_invalid"}),401
    
    @jwtManager.unauthorized_loader
    def unauthorizedTokenCallback(error):
        return jsonify({"Message": "Request doesn't contain a token", "Error": "token_missing"}),401


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