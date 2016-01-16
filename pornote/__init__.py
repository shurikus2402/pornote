from flask import Flask, session
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager


app = Flask(__name__)
app.debug = True
app.config.from_object("pornote.config")
manager = Manager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)


from pornote.models import *
from pornote.member import *
from pornote.homework import *


@app.route("/")
def homepage():
    # If the member is not logged in
    if "email" not in session:
        return render_template("homepage.html")
    else:
        member = Member.query.filter_by(email=session["email"]).first()
        homeworks = get_homework(member)
        return render_template("homepage.html", member=member, homeworks=homeworks)


@app.errorhandler(404)
def page_not_found(e):
    if "email" not in session:
        return render_template("404.html"), 404
    else:
        member = Member.query.filter_by(email=session["email"]).first()
        return render_template("404.html", member=member), 404
