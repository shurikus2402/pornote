from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from werkzeug import secure_filename
from datetime import date
import datetime
import os

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
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        class_nb = int(request.form.get("class_nb"))
        email = request.form.get("email")
        password = request.form.get("password")
        password_conf = request.form.get("password_conf")

        # Checks for errors in the form
        if not (first_name and last_name and email and password):
            flash("Inscription invalide ! (un ou plusieurs champs incomplets)")
            return redirect(url_for("sign_up"))
        if password != password_conf:
            flash("Les deux mots de passe ne sont pas identiques !")
            return redirect(url_for("sign_up"))

        member = Member(first_name, last_name, email, password, class_nb)

        db.session.add(member)
        db.session.commit()

        flash("Vous êtes inscrit !")
        # Automatically logs in the new member 
        session["email"] = member.email

        return redirect(url_for("homepage"))

def allowed_file(filename):
    return  '.' in filename and \
            filename.rsplit('.', 1)[1] not in app.config["UNALLOWED_EXTENSIONS"]

@app.route("/nouveau_devoir/", methods=["GET", "POST"])
def new_homework():
    # If the member is not logged in
    if "email" not in session:
        return redirect(url_for("homepage"))

    member = Member.query.filter_by(email = session["email"]).first()

    if request.method == "GET":
        return render_template("new_homework.html", name=member.first_name)
    elif request.method == "POST":
        # Checks for errors in the form
        description = request.form.get("description")
        if not description:
            flash("Veuillez remplir tous les champs, devoir non ajouté !")
            return redirect(url_for("new_homework"))

        # Date system
        date_form = request.form.get("end_date")
        date_form = datetime.datetime.strptime(date_form, "%d/%m/%Y").date()
        # Checks for invalid date
        if date_form <= date.today() or date_form.day > 31 or date_form.month > 12:
            flash("Date non conforme, devoir non ajouté !")
            return redirect(url_for("new_homework"))

        # File upload system
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        else:
            flash("Fichier invalide, devoir non ajouté !")
            return redirect(url_for("new_homework"))

        homework = Homework(
            member_id = member.id,
            subject = request.form.get("subject"),
            description = description,
            end_date = date_form,
            filename = filename,
            class_nb = member.class_nb
        )

        db.session.add(homework)
        db.session.commit()

        flash("Devoir ajouté sur le serveur !")

        return redirect(url_for("homepage"))
