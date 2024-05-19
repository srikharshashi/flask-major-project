import uuid
from pyrebase import pyrebase
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    abort,
    url_for,
    flash,
    session,
)
from werkzeug.utils import secure_filename
import config
from savethumbnail import upload_video_and_thumbnail
import os

app = Flask(__name__)  # Initialze flask constructor
app.debug = True
app.secret_key = "abcd"
# app.config['SESSION_TYPE'] = 'filesystem'


# initialize firebase
firebase = pyrebase.initialize_app(config.config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()

@app.route("/logout")
def logout():
    session.pop("name", default=None)
    session.pop("is_logged_in", default=None)
    session.pop("email", default=None)
    session.pop("uid", default=None)
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
    if "is_logged_in" in session and session["is_logged_in"] == "True":
        videos = db.child("users").child(session["uid"]).child("videos").get()
        print(videos)
        if videos.each() is None or len(videos.each()) <= 0:
            videos = None

        return render_template(
            "welcome.html", email=session["email"], name=session["name"], videos=videos
        )
    else:
        return redirect(url_for("login"))


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
            return redirect(url_for("welcome"))
        except Exception as e:
            print(e)
            # If there is any error, redirect back to login

            return redirect(url_for("login"))
    else:
        if "is_logged_in" in session and session["is_logged_in"] == "True":
            return redirect(url_for("welcome"))
        else:
            return redirect(url_for("login"))


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
            return redirect(url_for("welcome"))
        except Exception as e:
            print(e)
            print(e["error"]["message"])
            # If there is any error, redirect to register
            return redirect(url_for("register"))

    else:
        if "is_logged_in" in session and session["is_logged_in"] == "True":
            return redirect(url_for("welcome"))
        else:
            return redirect(url_for("register"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "uid" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        video = request.files["video"]
        print(video)
        if not video:
            print("No Video was selected")
            flash("No Video was selected", "error")
        else:
            filename = secure_filename(video.filename)
            upload_video_and_thumbnail(
                video_file=video,
                filename=filename,
                storage=storage,
                database=db,
                user=session,
                video_id=str(uuid.uuid4()),
            )
            flash("Uploading to DB Sucess!", "success")
    elif request.method == "GET":
        return render_template("upload_video.html")
    return redirect(url_for("welcome"))

@app.route("/video/video_id")
def play_video(video_url,video_id):
    video_id=str(uuid.uuid4())

    # Retrieve video URL from Firebase Realtime Database
    # video_url = db.child("users").child(session["uid"]).child("videos").child(video_id).child("video_url").get()

    if video_url:
        return render_template("video.html", video_url=video_url)
    else:
        flash("Video not found", "error")
        return redirect(url_for("welcome"))


if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
