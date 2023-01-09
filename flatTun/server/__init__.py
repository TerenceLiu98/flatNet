from server import * 

from flask import Flask, Blueprint, jsonify, abort, request, make_response, url_for,g, redirect
from flask_restful import Api, Resource, reqparse
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from dataclasses import dataclass
from importlib import import_module

app = Flask(__name__)
database = SQLAlchemy()

def register_extentions(app):
    database.init_app(app)
    
def register_blueprints(app):
	for module_name in ["auth", "netspace"]:
		module = import_module('server.{}.routes'.format(module_name))
		app.register_blueprint(module.routes)

@app.before_first_request
def initialize_database():
	with app.app_context():
		database.create_all()


def init_app():
    app.config.from_pyfile("config.py")
    register_extentions(app)
    register_blueprints(app)
    database = SQLAlchemy(app)
    migrate = Migrate(app, database)
    initialize_database()
    return app
