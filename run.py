from TaskTok.Server import create_app
from flask import Flask, jsonify, request

from TaskTok.extensions import db, jwtManager
from TaskTok.models import User, NoNoTokens
from TaskTok.schema import UserSchema
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
            defaultAcc.setPassword('superpassword')
            defaultAcc.add()     
    app.run(host='0.0.0.0', port=80, debug=True)