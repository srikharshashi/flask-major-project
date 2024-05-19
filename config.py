from dotenv import load_dotenv
import os
load_dotenv()
config = {
  "apiKey": os.getenv("APIKEY"),
  "authDomain": os.getenv("AUTHDOMAIN"),
  "databaseURL": os.getenv('DBURL'),
  "projectId": os.getenv('PRJID'),
  "storageBucket": os.getenv('STRGBUCKET'),
  "messagingSenderId": os.getenv('MSGID'),
  "appId": os.getenv('APPID'),
}