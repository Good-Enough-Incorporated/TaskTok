**This project is a collaborative effort for Team 5 in UMGC 495 for our capstone project. This developement is purely for school and is not used in any production environment.**

Team instructions: 

Install Python (3.11)

Download Github desktop, VSCode

add the TaskTok repository and make a local copy. From Github Desktop it should also ask to open project in VSCode

Create the virtual environment with VSCode Control Shift P: Python: Create Environment

It should ask if you want to install from requirements.txt

(or manually)
run pip install -r .\requirements.txt

then you should be able to run python .\run.py



to create users, i'm using postman:

POST 192.168.1.26/auth/register

BODY: JSON

{

    "username": "test",
    "email": "test123@gmail.com",
    "password": "hello"


}


to check database, i'm using DB Browser for SQLite

db is located: TaskTok\instance\db.sqlite3
