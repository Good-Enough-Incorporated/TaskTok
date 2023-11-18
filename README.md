**This project is a collaborative effort for Team 5 in UMGC 495 for our capstone project. This developement is purely for school and is not used in any production environment.**

1) Install VSCode, Python 3.11
2) Download Git or Github Desktop
3) Clone this repository https://github.com/Good-Enough-Incorporated/TaskTok.git
4) Open the project folder in VSCode (C:\Users\jason\OneDrive\Documents\GitHub\GEI\TaskTok) or where ever you saved it.
5) Ctr + Shift + P > Python: Create Environment > Select the requirement.txt file
6) Run the app.py file and make sure the Flask server runs
(should see something like below)
  WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on https://127.0.0.1:443
 * Running on https://192.168.1.26:443

7) Stop the server by Ctrl + C
   *(should see (.venv) before your commands now)*
8) Run the following commands
   - Flask createDatabase
   - Flask createAdminUser
   - Flask createAdminTasks



**Other Useful Information**
to view the database, i'm using DB Browser for SQLite

db is located: TaskTok\instance\db.sqlite3


For celery/rabbitmq:

Under Server.py > Update the broker_url to your rabitmq instance

Be sure to install the rabbitmq management plugin, and create the vhost

vhost: tasktok

user admin:password

give permissions for admin to tasktok vhost

to run celery, activate the python virtual environment

celery -A RemindMeClient.Client.celery worker --infolevel=INFO

