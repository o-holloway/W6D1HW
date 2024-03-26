from flask import Flask

#Creates an instance of Flask called 'app'
app = Flask(__name__)

#import the routes
from .import routes
