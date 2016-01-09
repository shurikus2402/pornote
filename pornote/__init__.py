from flask import Flask, render_template, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
import datetime

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

@app.route("/nouveau_devoir/", methods=["GET", "POST"])
def new_homework():
    if request.method == "GET":
        return render_template("new_homework.html")
    elif request.method == "POST":
        subject_form = request.form.get("subject")
        print(subject_form)

        date = request.form.get("end_date")
        date = datetime.datetime.strptime(date, "%d/%m")

        homework = Homework(
            member_id = 1, # Temporary member id
            subject = subject_form,
            description = request.form.get("description"),
            class_nb = 2, # Temporary class number
            end_date = date
        )

        db.session.add(homework)
        db.session.commit()

        return redirect(url_for("homepage"))
