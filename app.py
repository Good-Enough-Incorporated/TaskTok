
#import logging

from flask import Flask, jsonify, request

from extensions import db
from models import User

#keycloak_client = Client('192.168.1.26/kc/callback')
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite3"
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SECRET_KEY'] = r'HJDNUIWQEYH156345357564@@!@$'
    
    db.init_app(app)  # Initialize the db extension with app

    # Register blueprints:
    from blueprints import api as api_blueprint
    from blueprints import auth as auth_blueprint
    from blueprints import views as views_blueprint
    #app.register_blueprint(api_blueprint.api, url_prefix='/api')
    app.register_blueprint(auth_blueprint.auth, url_prefix='/auth')
    app.register_blueprint(views_blueprint.views, url_prefix='/')

    return app

app = create_app()






if __name__ == "__main__":
    #logging.basicConfig(filename='app.log', level=logging.DEBUG)
    #webserver_IP = get_local_ip()
    #db.create_all()  # Creates the database and table if they don't exist
    with app.app_context():
        try:
            user = User.query.first()
        except:
            #database doesn't exist. create
            print("Creating database and default admin for first run.")
            db.create_all()
            defaultAcc = User(username= "admin", email="admin@tasktok.com")
            defaultAcc.set_password('superpassword')
            defaultAcc.add()
       
   
    app.run(host='0.0.0.0', port=80, debug=True)
