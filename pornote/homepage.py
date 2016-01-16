from pornote import app
from flask import session, render_template

from pornote.homework import *
from pornote.models import *


@app.route("/")
def homepage():
    if "email" not in session:
        return render_template("homepage.html")
    else:
        member = Member.query.filter_by(email=session["email"]).first()
        homeworks = get_homework(member)
        return render_template("homepage.html",
                member=member, homeworks=homeworks)
