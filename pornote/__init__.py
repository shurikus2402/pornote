from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

app = Flask(__name__)
app.config.from_object("pornote.default_settings")
manager = Manager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)

from pornote.models import *

@app.route("/")
def homepage():
    return render_template("homepage.html")
