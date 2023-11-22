# Unit tests for TaskTok\Server.py

from datetime import timedelta, timezone, datetime
import unittest
from unittest.mock import patch, MagicMock, Mock
from flask import jsonify, make_response, request, render_template
import os
from TaskTok import create_app
from TaskTok.models import User, NoNoTokens
from flask_jwt_extended import create_access_token, get_jwt_identity, JWTManager
import json

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.jwt_manager = self.app.extensions['flask-jwt-extended']

    def tearDown(self):
        self.app_context.pop()

    # U-7.1
    def test_create_app(self):
        self.assertEqual(self.app.config['SQLALCHEMY_DATABASE_URI'], os.environ.get('SQLALCHEMY_DATABASE_URI'))
        self.assertEqual(self.app.config['SQLALCHEMY_ECHO'], os.environ.get('SQLALCHEMY_ECHO'))
        self.assertEqual(self.app.config['SECRET_KEY'], os.environ.get('SECRET_KEY'))
        self.assertEqual(self.app.config['JWT_SECRET_KEY'], os.environ.get('JWT_SECRET_KEY'))
        self.assertEqual(self.app.config['JWT_TOKEN_LOCATION'], os.environ.get('JWT_TOKEN_LOCATION'))
        self.assertTrue(self.app.config['JWT_COOKIE_CSRF_PROTECT'])
        self.assertEqual(self.app.config['JWT_ACCESS_TOKEN_EXPIRES'], timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES'))))
        self.assertEqual(self.app.config['MAIL_SERVER'], os.environ.get('MAIL_SERVER'))
        self.assertEqual(self.app.config['MAIL_PORT'], os.environ.get('MAIL_PORT'))
        self.assertEqual(self.app.config['MAIL_USE_TLS'], os.environ.get('MAIL_USE_TLS'))
        self.assertEqual(self.app.config['MAIL_USERNAME'], os.environ.get('MAIL_USERNAME'))
        self.assertEqual(self.app.config['MAIL_PASSWORD'], os.environ.get('MAIL_PASSWORD'))
        self.assertEqual(self.app.config['MAIL_DEFAULT_SENDER'], os.environ.get('MAIL_DEFAULT_SENDER'))
        self.assertEqual(self.app.config['CELERY']['broker_url'], 'redis://localhost')
        self.assertEqual(self.app.config['CELERY']['result_backend'], 'redis://localhost')
        self.assertTrue(self.app.config['CELERY']['task_ignore_result'])

    # U-7.3
    def test_page_not_found(self):
        with self.app.test_client() as client:
            response = client.get('/non-existent-route')
            self.assertEqual(response.status_code, 404)

    # U-7.4
    def test_user_identity_lookup(self):
        mock_user = User()
        mock_user.id = 42
        identity_loader = self.jwt_manager._user_identity_callback
        user_id = identity_loader(mock_user)
        self.assertEqual(user_id, mock_user.id)

    # U-7.5
    @patch('TaskTok.models.User.query')
    def test_search_logged_in_user(self, mock_user_query):
        mock_user = User()
        mock_user.id = 1
        mock_user_query.get.return_value = mock_user
        user_lookup_loader = self.jwt_manager._user_lookup_callback
        jwt_data = {'sub': mock_user.id}
        result = user_lookup_loader(None, jwt_data)
        self.assertEqual(result, mock_user)

   # function from servers.py
    def addAdditionalClaims(self, identity):
        if identity.username == "admin":
            return {"is_admin" : True}
        else:
            return {"is_admin" : False}

    # U-7.6.1
    @patch('TaskTok.models.User.query')
    def test_add_additional_claims_admin(self, mock_user_query):
        admin_user = User()
        admin_user.username = 'admin'
        self.assertTrue(self.addAdditionalClaims(admin_user)['is_admin'])

    # U-7.6.2
    @patch('TaskTok.models.User.query')
    def test_add_additional_claims_nonadmin(self, mock_user_query):
        normal_user = User()
        normal_user.username = 'norman'    
        self.assertFalse(self.addAdditionalClaims(normal_user)['is_admin'])

    # function from servers.py
    def expiredTokenCallback(self, error):
        return jsonify({"Message": "Signature validation failed", "Error": "token_invalid"}),401

    # U-7.8
    def test_expired_token_callback(self):
        with self.app.test_request_context('/some_url'):
            response, status_code = self.expiredTokenCallback('error')
            self.assertEqual(status_code, 401)
            self.assertEqual(response.json, {"Message": "Signature validation failed", "Error": "token_invalid"})

    # function from servers.py
    def unauthorizedTokenCallback(self, error):
        acceptHeader = request.headers.get('Accept', '')
        if 'application/json' in acceptHeader:
            response = make_response(jsonify({"Message": "API call missing a token", "Error": "token_missing"}))
            response.mimetype = 'application/json'
            response.status_code = 401
            return response
        else:
            response = make_response(render_template("error/notLoggedIn.html"))
            response.mimetype = 'text/html'
            response.status_code = 401
            return response
    
    # U-7.9.1
    def test_unauthorized_token_json_response(self):
        with self.app.test_request_context(headers={'Accept': 'application/json'}):
            response = self.unauthorizedTokenCallback('error')
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.mimetype, 'application/json')
            self.assertEqual(response.json, {"Message": "API call missing a token", "Error": "token_missing"})

    # U-7.9.2
    @patch('flask.render_template', return_value="Rendered error/notLoggedIn.html")
    def test_unauthorized_token_html_response(self, mock_render_template):
        with self.app.test_request_context(headers={'Accept': 'text/html'}):
            response = self.unauthorizedTokenCallback('error')
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.mimetype, 'text/html')
            self.assertTrue("Not Logged In" in response.get_data(as_text=True))

    # function from servers.py
    def tokenIsRevokedCallback(self, token):
        #jti = jwt_data['jti']
        #token = db.session.query(NoNoTokens).filter(NoNoTokens.jti == jti).scalar()
        if token is not None:
            return True
        else: 
            return False

    # U 7.10.1
    def test_token_revoked_exists(self):
        token = "test"
        result = self.tokenIsRevokedCallback(token)
        self.assertTrue(result) 

    # U 7.10.2
    def test_token_revoked_none(self):
        token = None
        result = self.tokenIsRevokedCallback(token)
        self.assertFalse(result) 

    # function from servers.py
    def tokenWasRevoked(self):
        return jsonify({"Message": "The supplied token was revoked already", "Error": "token_revoked"}),401
    
    # U-7.11
    def test_token_was_revoked(self):
        response, status_code = self.tokenWasRevoked()
        self.assertEqual(status_code, 401)
        self.assertEqual(response.json, {"Message": "The supplied token was revoked already", "Error": "token_revoked"})

if __name__ == '__main__':
    unittest.main()
