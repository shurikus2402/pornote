import datetime
import os
import pathlib

from pornote import app
from flask import session, redirect, url_for, render_template, request, flash
from flask import send_from_directory
from werkzeug import secure_filename
from datetime import date

from pornote.models import *


def get_homework(member):
    homeworks = Homework.query.filter_by(class_nb=member.class_nb).all()
    availabe_homework = []

    for i in range(0, len(homeworks)):
        if (homeworks[i].section in ["G", member.section, member.second_lang] and
                homeworks[i].end_date >= date.today()):
            availabe_homework.append(homeworks[i])

    return sorted(availabe_homework, key=lambda x: x.end_date)


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1] not in app.config["UNALLOWED_EXTENSIONS"])


def get_section(subject):
    if subject in ["Français", "Histoire", "Anglais"]:
        # Common to everyone
        return "G"
    elif subject in ["Maths S", "Physique S", "SVT S"]:
        return "S"
    elif subject in ["Maths ES", "Physique ES", "SVT ES", "Economie"]:
        return "ES"
    else:
        # Spanish and German
        return subject


@app.route("/nouveau_devoir/", methods=["GET", "POST"])
def new_homework():
    if "email" not in session:
        return redirect(url_for("homepage"))

    member = Member.query.filter_by(email=session["email"]).first()

    if request.method == "GET":
        return render_template("new_homework.html", member=member)
    elif request.method == "POST":
        # Section system
        subject = request.form.get("subject")
        section = get_section(subject)

        # Checks for errors in the form
        description = request.form.get("description")
        if not description:
            flash("Veuillez remplir tous les champs, devoir non ajouté !")
            return redirect(url_for("new_homework"))

        # Date system
        date_form = request.form.get("end_date")
        date_form = datetime.datetime.strptime(date_form, "%d/%m/%Y").date()
        # Checks for invalid date
        if (date_form <= date.today() or date_form.day > 31 or
               date_form.month > 12):
            flash("Date non conforme, devoir non ajouté !")
            return redirect(url_for("new_homework"))

        # File upload system
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
        else:
            flash("Fichier invalide, devoir non ajouté !")
            return redirect(url_for("new_homework"))

        homework = Homework(
            member_id   = member.id,
            subject     = subject,
            section     = section,
            description = description,
            end_date    = date_form,
            filename    = filename,
            class_nb    = member.class_nb
        )

        db.session.add(homework)
        db.session.commit()

        # If there is already a file with that name, add homework's id to it
        path = os.path.join("pornote/" + app.config["UPLOAD_FOLDER"], filename)
        f = pathlib.Path(path)
        if f.is_file():
            index = filename.rfind(".")
            filename = filename[:index] + str(homework.id) + filename[index:]
            path = os.path.join("pornote/" + app.config["UPLOAD_FOLDER"], filename)
            homework.filename = filename

        file.save(path)

        member.points += 1
        db.session.commit()

        flash("Devoir ajouté sur le serveur !")

        return redirect(url_for("homepage"))


@app.route("/uploads/<path:filename>", methods=["GET", "POST"])
def download(filename):
    if "email" not in session:
        return redirect(url_for("homepage"))

    member = Member.query.filter_by(email = session["email"]).first()

    # The member needs at least 1 point to download a homework
    if member.points <= 0:
        return redirect(url_for("homepage"))

    member.points -= 1
    db.session.commit()

    current_path = os.path.dirname(os.path.realpath(__file__))
    uploads = os.path.join(current_path, app.config["UPLOAD_FOLDER"])
    return send_from_directory(uploads, filename)
