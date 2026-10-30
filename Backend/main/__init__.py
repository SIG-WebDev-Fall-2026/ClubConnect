from flask import Flask
from flask_cors import CORS
from main.extensions import db, bcrypt

# Nessecary for creating authentication
from flask_jwt_extended import JWTManager

# Nessecary for using enviroment variables
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)       # Create the app instance
CORS(app)                   # Permits frontend and backend communication

# Configure Database and JWT_SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATA_BASE_URL")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

db.init_app(app)
bcrypt.init_app(app)
JWTManager(app)

from main import routes
