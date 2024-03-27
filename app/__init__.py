from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

#Creates an instance of Flask called 'app'
app = Flask(__name__)

#Set the configuration
app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app,db)

#import the routes
from .import routes
