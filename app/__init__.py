import os
import logging

from flask import Flask, render_template

from app import database
from app.dash_setup import register_dashapps


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    logging.basicConfig(level=logging.DEBUG)

    @app.route('/index/')
    def home():
        return render_template('index.html')

    register_dashapps(app)

    return app