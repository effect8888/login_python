from ast import Return
import sqlite3
import flask
import hashlib
from flask import request, redirect
import random
import requests


app = flask.Flask(__name__)

databaseName = "database.db"
tableName = "login_details"
mainDatabase = sqlite3.connect(databaseName)
crsr = mainDatabase.cursor()

try:
    crsr.execute(f"""
    CREATE TABLE IF NOT EXISTS {tableName} (
        email text,
        password text,
        username text
    )
    """)
except sqlite3.OperationalError:
    print("Table Already Exists! Skipping the creation of table...")

mainDatabase.commit()
mainDatabase.close()

@app.route("/", methods=["GET"])
def mainPage():
    return """
    <h1>Open index.html to get started!</h1>
    """

@app.route('/get', methods=['GET'])
def get():
    try:
        connection = sqlite3.connect(databaseName)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {tableName}")
        dbData = cursor.fetchall()
        connection.close()

        returnData = {
            "success": True,
            "data": dbData
        }

        return returnData

    except Exception as e:
        return {
            "success": False,
            "cause": e
        }

@app.route("/createaccount", methods=["POST", "GET"])
def createAccount():
    try:
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        h = hashlib.new('sha256')
        h.update(password+"$razok_73bdws37dfh")
        password = h.hexdigest()


        connection = sqlite3.connect(databaseName)
        cursor = connection.cursor()

        cursor.execute(f"SELECT * FROM {tableName} WHERE username IS '{username}'")
        sameUserName = cursor.fetchall()
        if (len(sameUserName) > 0):
            return "Username already in use!"
    
        cursor.execute(f"SELECT * FROM {tableName} WHERE email IS '{email}'")
        sameEmail = cursor.fetchall()
        if (len(sameEmail) > 0):
            return "Email already in use!"

        #verify email-adress

        code = random.randint(100000,999999)
       
        def send_simple_message():
            return requests.post(
                "https://api.mailgun.net/v3/flexes.me/messages",
                auth=("api", "7b3bba68c4d5423554df637cffd4e6db-4534758e-5615d64b"),
                data={"from": "USER VERIFY <user@flexes.me>",
                    "to": ["tewsjean1@gmail.com"],
                    "subject": "verify for FLEXES.ME",
                    "text": f"<h1>YOUR CODE : {code}</h1><br>follow link  https://flexes.me/singin"})

        send_simple_message()


        cursor.execute(f"INSERT INTO {tableName} values (?, ?, ?)", (email, password, username))
        connection.commit()
        connection.close()

        return f"Signed in as {username}!"
    except Exception as e:
        return {
            "success": False,
            "cause": e
        }

@app.route("/signin", methods=["POST", "GET"])
def signIn():
    try:
        email = request.form["email"]
        password = request.form["password"]

        
        h = hashlib.new('sha256')
        h.update(password+"$razok_73bdws37dfh")
        password = h.hexdigest()

        connection = sqlite3.connect(databaseName)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {tableName} WHERE email LIKE '{email}'")
        dbData = list(cursor.fetchall())[0]
        print(dbData)
        connection.close()

        dbPW = list(dbData)[1]
        dbUsername = list(dbData)[2]

        if dbPW == password:
            return f"Logged in as {dbUsername}"
        else:
            return "Incorrect password!"

    except Exception as e:
        print(e)
        return {
            "success": False,
            "cause": "No account found with the provided email!"
        }

app.run()