from pornote import app
from flask import session, redirect, url_for, render_template, request, flash

from pornote.models import *


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
        section = request.form.get("section")
        second_lang = request.form.get("second_lang")
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
        member = Member.query.filter_by(email = email.lower()).first()
        if member:
            flash("Adresse mail déjà utilisée !")
            return redirect(url_for("sign_up"))

        member = Member(first_name, last_name, email, password, 
                        class_nb, section, second_lang)

        db.session.add(member)
        db.session.commit()

        flash("Vous êtes inscrit !")
        # Automatically logs in the new member 
        session["email"] = member.email

        return redirect(url_for("homepage"))
