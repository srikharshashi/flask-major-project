import uuid
from pyrebase import pyrebase
from flask import Flask, flash, redirect, render_template, request, abort, url_for,flash,session
from werkzeug.utils import secure_filename
import config
from savethumbnail import upload_video_and_thumbnail
from my_utils.inference import infer
from my_utils.writefile import write_video_file
from flask_executor import Executor
import copy
import sys
sys.setrecursionlimit(100000000)  

app = Flask(__name__)  # Initialze flask constructor
executor = Executor(app)

app.debug = True
app.secret_key="abcd"

# initialize firebase
firebase = pyrebase.initialize_app(config.config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

@app.route("/logout")
def logout():
    session.pop("name",default=None)
    session.pop("is_logged_in",default=None)
    session.pop("email",default=None)
    session.pop("uid",default=None)
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
    if "is_logged_in" in session and session["is_logged_in"]== "True":
        videos=db.child("users").child(session["uid"]).child("videos").get()
        if(videos.each() is None or len(videos.each())<=0):
            videos=None
        return render_template("welcome.html", email=session["email"], name=session["name"],videos=videos)
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
            session["is_logged_in"] = "True"
            session["email"] = user["email"]
            session["uid"] = user["localId"]
            # Get the name of the user
            data = db.child("users").get()
            session["name"] = data.val()[session["uid"]]["name"]
            # Redirect to welcome page
            return redirect(url_for('welcome'))
        except Exception as e:
            print(e)
            # If there is any error, redirect back to login
            
            return redirect(url_for('login'))
    else:
        if "is_logged_in" in session and session["is_logged_in"] == "True":
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
            session["is_logged_in"] = "True"
            session["email"] = user["email"]
            session["uid"] = user["localId"]
            session["name"] = name
            # Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(session["uid"]).set(data)
            # Go to welcome page
            return redirect(url_for('welcome'))
        except Exception  as e:
            print(e)
            print(e["error"]["message"])
            # If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if "is_logged_in" in session and session["is_logged_in"] == "True":
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if "uid" not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'video1' not in request.files or 'video2' not in request.files:
            flash("Sorry, the upload didn't send all of the data!","error")
            return redirect(request.url)
        video1 = request.files['video1']
        video2=request.files['video2']
        print(video1)
        print(video2)
        if not video1 or not video2:
            print("No Video was selected")
            flash("No Video was selected",'error')
        else:
            video_id=str(uuid.uuid4())
            # video2=copy.deepcopy(video1)
            video_path=write_video_file(video_file=video1,output_path=f"./inputs/{video_id}.mp4")
            # print(video)
            filename = secure_filename(video2.filename)
            upload_video_and_thumbnail(video_file=video2,filename=filename,storage=storage,database=db,user=session,video_id=video_id)
            executor.submit(infer,video_path,storage,db,session,video_id)
            flash("Uploading to DB Sucess!",'success')
    elif request.method == 'GET':
        return render_template('upload_video.html')
    return redirect(url_for('welcome'))

@app.route("/analyzed",methods=["GET"])
def analyzed():
    videos=db.child("users").child(session["uid"]).child("videos").get()
    print(videos)
    analyzed_videos=[]
    for video in videos.each():
        if "processed_url" in video.val():
            analyzed_videos.append(video)
    return render_template("analyzed-videos.html",videos=analyzed_videos)


if __name__ == "__main__":
    app.run()
