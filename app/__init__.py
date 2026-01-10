from flask import Flask
from dotenv import load_dotenv, find_dotenv
import os

from .auth.routes import auth_bp
from .main.routes import dashboard_bp

from app.extensions import mongo

def create_app():
    load_dotenv(find_dotenv())

    app = Flask(__name__)

    app.config['MONGO_URI'] = os.getenv('MONGO_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    mongo.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    
    return app