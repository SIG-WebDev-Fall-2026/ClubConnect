from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

from main.extensions import db, bcrypt

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATA_BASE_URL")
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")

db.init_app(app)
bcrypt.init_app(app)
JWTManager(app)

from main import routes
