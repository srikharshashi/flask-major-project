import uuid
from pyrebase import pyrebase
from flask import Flask, flash, redirect, render_template, request, abort, url_for,flash
from werkzeug.utils import secure_filename
import json
import config
from savethumbnail import upload_video_and_thumbnail

app = Flask(__name__)  # Initialze flask constructor
app.debug = True
app.secret_key="abcd"
# app.config['SESSION_TYPE'] = 'filesystem'



# initialize firebase
firebase = pyrebase.initialize_app(config.config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()
# Init  ialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

@app.route("/logout")
def logout():
    global person
    person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}
    return redirect(url_for("welcome"))

# Login
@app.route("/login")
def login():
    return render_template("login.html")


# Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")


# Welcome page
@app.route("/")
def welcome():
    if person["is_logged_in"] == True:
        videos=db.child("users").child(person["uid"]).child("videos").get()
        return render_template("welcome.html", email=person["email"], name=person["name"],user = person,videos=videos)
    else:
        return redirect(url_for('login'))


# If someone clicks on login, they are redirected to /result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":  # Only if data has been posted
        result = request.form  # Get the data
        email = result["email"]
        password = result["pass"]
        try:
            # Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            print(user)
            # Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            # Get the name of the user
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            # Redirect to welcome page
            return redirect(url_for('welcome'))
        except Exception as e:
            print(e)
            # If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))


# If someone clicks on register, they are redirected to /register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":  # Only listen to POST
        result = request.form  # Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            # Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            # Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            # Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            # Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            # Go to welcome page
            return redirect(url_for('welcome'))
        except Exception  as e:
            print(e)
            # If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not person["uid"]:
        return redirect(url_for('login'))
    if request.method == 'POST':
        video = request.files['video']
        print(video)
        if not video:
            print("No Video was selected")
            flash("No Video was selected",'error')
        else:
            filename = secure_filename(video.filename)
            upload_video_and_thumbnail(video_file=video,filename=filename,storage=storage,database=db,user=person,video_id=str(uuid.uuid4()))
            flash("Uploading to DB Sucess!",'success')
    elif request.method == 'GET':
        return render_template('upload_video.html')
    return redirect(url_for('welcome'))


if __name__ == "__main__":
    app.run()
