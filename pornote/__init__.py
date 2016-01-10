from flask import Flask, render_template, request, redirect, url_for, flash, session
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
    # If the member is not logged in
    if "email" not in session:
        return render_template("homepage.html")
    else:
        member = Member.query.filter_by(email = session["email"]).first()
        return render_template("homepage.html", name=member.first_name)

@app.route("/deconnexion/")
def sign_out():
    if "email" in session:
        session.pop("email", None)
    return redirect(url_for("homepage"))

@app.route("/connexion/", methods=["GET", "POST"])
def sign_in():
    # If the member is already logged in
    if "email" in session:
        return redirect(url_for("homepage"))

    if request.method == "GET":
        return render_template("sign_in.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        member = Member.query.filter_by(email = email.lower()).first()
        if member and member.check_password(password):
            session["email"] = email
            return redirect(url_for("homepage"))
        else:
            flash("Email ou mot de passe incorrect !")
            return render_template("sign_in.html")

@app.route("/inscription/", methods=["GET", "POST"])
def sign_up():
    # If the member is already logged in
    if "email" in session:
        return redirect(url_for("homepage"))

    if request.method == "GET":
        return render_template("sign_up.html")
    elif request.method == "POST":
        member = Member(
           first_name = request.form.get("first_name"), 
           last_name = request.form.get("last_name"), 
           email = request.form.get("email"),
           class_nb = int(request.form.get("class_nb")),
           password = request.form.get("password")
        )

        db.session.add(member)
        db.session.commit()

        flash("Vous êtes inscrit !")
        # Automatically logs in the new member 
        session["email"] = member.email

        return redirect(url_for("homepage"))

@app.route("/nouveau_devoir/", methods=["GET", "POST"])
def new_homework():
    # If the member is not logged in
    if "email" not in session:
        return render_template("homepage.html")

    member = Member.query.filter_by(email = session["email"]).first()

    if request.method == "GET":
        return render_template("new_homework.html", name=member.first_name)
    elif request.method == "POST":
        date_form = request.form.get("end_date")
        now = date.today()
        date_form += "/" + str(now.year)

        date_form = datetime.datetime.strptime(date_form, "%d/%m/%Y").date()
        # When you're in december and you have work for january
        if date_form < now:
            date_form += timedelta(days=365)

        homework = Homework(
            member_id = member.id,
            subject = request.form.get("subject"),
            description = request.form.get("description"),
            class_nb = member.class_nb,
            end_date = date_form
        )

        db.session.add(homework)
        db.session.commit()

        flash("Devoir ajouté sur le serveur !")

        return redirect(url_for("homepage"))
