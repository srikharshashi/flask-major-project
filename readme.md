# Auto Umpring for Tennis backend

## Features
1) Login/Sign up - Hosted on firebase
2) Fully responsive UI 
3) Based on Python-Flask
4) Uses Flask Executor Framework to asyncronously process videos


## Requirements

### Require pip packages 
```bash
pip install pyrebase4
pip install flask
pip install firebase-admin
pip install dotenv
pip install werkzeug
pip install moviepy
pip install ultralytics
pip install torch
pip install pandas
pip install numpy
pip install opencv-python
```

### Required Linux Packages 
- Developed on a WSL2 Ubuntu 22.04 environment
- CUDA was setup and running on NVIDIA GTX 1650Ti Mobile
- bash`sudo apt-get install x264`
- bash `sudo apt install ffmpeg`


### Setting up firebase

1) Go to https://console.firebase.google.com
2) Login/Register your account
3) Click on add project
4) Give project name
5) Optional: select google analytics
6) Create project
7) Under "Get started by adding Firebase to your app", click on web app
8) Name the web app and copy the "apiKey", "authDomain", "databaseURL", "storageBucket" from the code given there
10) Go to .env and add the values you copied above
11) Go to console, click on authentication (On the left sidebar), click on sign-in method, and enable email/password sign in
12) Go to Storage (On the left sidebar), and click on "Create Database", start in test mode for now, click done.
13) You are all set on firebase !!!

### 

## Models Used
* YOLO v8 for player detection
* Fine Tuned YOLO for tennis ball detection
* Court Key point extraction

## Additional Info

The server starts by default on http://127.0.0.1:5000/
