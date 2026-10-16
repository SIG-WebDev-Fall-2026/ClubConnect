from flask import Flask
from flask_cors import CORS
from .extensions import db

# Nessecary for using enviroment variables
import os
#from dotenv import load_dotenv

app = Flask(__name__)       # Create the app instance
CORS(app)                   # Permits frontend and backend communication

from .routes import api
app.register_blueprint(api, url_prefix="/api")

# Sedrik must Configure the database
# app.config['SQLALCHEMY_DATABASE_URI'] = <You can make this an enviroment I dunno>

#db.init_app(app)
#from main import routes

