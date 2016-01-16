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
import pornote.member
import pornote.homework

@app.route("/")
def homepage():
    # If the member is not logged in
    if "email" not in session:
        return render_template("homepage.html")
    else:
        member = Member.query.filter_by(email = session["email"]).first()
        homeworks = Homework.query.filter_by(class_nb = member.class_nb).all()
        availabe_homework = []
        for i in range(0, len(homeworks)):
            if homeworks[i].section in ["G", member.section, member.second_lang]:
                availabe_homework.append(homeworks[i])
        sorted_homework = sorted(availabe_homework, key=lambda x: x.end_date)
        return render_template( "homepage.html", 
                                member=member, homeworks=sorted_homework)
