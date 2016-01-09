from flask import Flask, render_template, request, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from datetime import date
import datetime

app = Flask(__name__)
app.config.from_object("pornote.config")
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
        date_form = request.form.get("end_date")
        now = date.today()
        date_form += "/" + str(now.year)

        date_form = datetime.datetime.strptime(date_form, "%d/%m/%Y").date()
        # When you're in december and you have work for january
        if date_form < now:
            date_form += timedelta(days=365)

        homework = Homework(
            member_id = 1, # Temporary member id
            subject = request.form.get("subject"),
            description = request.form.get("description"),
            class_nb = 2, # Temporary class number
            end_date = date_form
        )

        db.session.add(homework)
        db.session.commit()

        return redirect(url_for("homepage"))
