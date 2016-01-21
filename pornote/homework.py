import datetime
import os
import shutil

from pornote import app
from flask import session, redirect, url_for, render_template, request, flash
from flask import send_from_directory
from werkzeug import secure_filename
from datetime import date

from pornote.models import *


twin_class = {
    1: 2,
    2: 1,
    3: 4,
    4: 3,
    5: 6,
    6: 5
}

def get_homework(member):
    homework = Homework.query.filter_by(class_nb=member.class_nb).all()
    availabe_homework = []
    today = date.today()

    for i in range(0, len(homework)):
        if (homework[i].section in ["G", member.section, member.second_lang] and
                homework[i].end_date >= today):
            availabe_homework.append(homework[i])

    # In my school and on this specific year, each class has a "twin" class
    # to work with in your section
    homework = Homework.query.filter_by(class_nb=twin_class[member.class_nb]).all()
    for i in range(0, len(homework)):
        if (homework[i].section == member.section and
                homework[i].end_date >= today):
            availabe_homework.append(homework[i])

    return sorted(availabe_homework, key=lambda x: x.end_date)


def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1] not in app.config["UNALLOWED_EXTENSIONS"])


def get_section(subject):
    # Common to everyone
    if subject in ["Français", "Histoire", "Anglais"]:
        return "G"
    # Scientific
    elif subject in ["Maths S", "Physique S", "SVT S"]:
        return "S"
    # Economy
    elif subject in ["Maths ES", "Physique ES", "SVT ES", "Economie"]:
        return "ES"
    # Spanish and German
    else:
        return subject


def add_to_filename(str1, str2):
    index = str1.rfind(".")
    # If str1 is the name of a directory
    if index == -1:
        str1 += str2
    else:
        str1 = str1[:index] + str2 + str1[index:]
    return str1


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
        try:
            if '-' in date_form:
                date_form = datetime.datetime.strptime(date_form, "%Y-%m-%d").date()
            else:
                date_form = datetime.datetime.strptime(date_form, "%d/%m/%Y").date()
            valid_date = True
        except ValueError:
            valid_date = False
        if not valid_date or date_form < date.today():
            flash("Date non conforme, devoir non ajouté !")
            return redirect(url_for("new_homework"))

        # File upload system
        file = request.files.getlist("file[]")
        ## Check for errors
        filenames = {}
        for i in range(len(file)):
            if file[i] and allowed_file(file[i].filename):
                temp_name = secure_filename(file[i].filename)
                if temp_name in filenames.values():
                    temp_name = add_to_filename(temp_name, "%d" % i)
                filenames[i] = temp_name
            else:
                flash("Fichier invalide, devoir non ajouté !")
                return redirect(url_for("new_homework"))
        if len(file) == 1:
            is_dir = False
            save_name = filenames[0]
        else:
            is_dir = True
            save_name = secure_filename("%s" % subject)
        ## If there is already a file/dir with that name, add homework's id to it
        ## (but for now, since the id is not generated yet, use a random string)
        upload_path = "pornote/" + app.config["UPLOAD_FOLDER"]
        path = os.path.join(upload_path, save_name)
        if os.path.exists(path):
            new_name = os.urandom(10)
        else:
            new_name = save_name

        checkbox = request.form.get("is_public")
        if checkbox:
            is_public = True
        else:
            is_public = False

        homework = Homework(
            member_id   = member.id,
            subject     = subject,
            section     = section,
            description = description,
            end_date    = date_form,
            filename    = new_name,
            class_nb    = member.class_nb,
            is_public   = is_public
        )

        db.session.add(homework)
        db.session.commit()

        # If the file/dir has a temporary name
        if new_name != save_name:
            save_name = add_to_filename(save_name, str(homework.id))
            path = os.path.join(upload_path, save_name)
            homework.filename = save_name
      
        if is_dir:
            os.makedirs(path)
            for id, files in filenames.items():
                file_path = os.path.join(path + "/" + files)
                file[id].save(file_path)
            ## Create a zip file of the directory
            shutil.make_archive(path, "zip", path)
            homework.filename = save_name + ".zip"
        else:
            file[0].save(path)

        # Point system
        member.points += 1
        if homework.is_public:
            member.nb_public += 1
            if member.nb_public == 3:
                member.nb_public = 0
                member.points += 1

        db.session.commit()

        flash("Devoir ajouté sur le serveur !")

        return redirect(url_for("homepage"))


@app.route("/uploads/<path:filename>", methods=["GET", "POST"])
def download(filename):
    if "email" not in session:
        return redirect(url_for("homepage"))

    member = Member.query.filter_by(email=session["email"]).first()
    homework = Homework.query.filter_by(filename=filename).first()

    if not homework.is_public:
        if member.points <= 0:
            return redirect(url_for("homepage"))
        member.points -= 1
        db.session.commit()

    current_path = os.path.dirname(os.path.realpath(__file__))
    uploads = os.path.join(current_path, app.config["UPLOAD_FOLDER"])
    return send_from_directory(uploads, filename)
