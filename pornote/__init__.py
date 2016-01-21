from flask import Flask
from flask import session, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from werkzeug.contrib.fixers import ProxyFix


app = Flask(__name__)
app.debug = True
app.config.from_object("pornote.config")
manager = Manager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)


from pornote.homepage import *
from pornote.member import *
from pornote.homework import *
from pornote.models import *


@app.errorhandler(404)
def page_not_found(e):
    # If the member is not logged in
    if "email" not in session:
        return render_template("404.html"), 404
    else:
        member = Member.query.filter_by(email=session["email"]).first()
        return render_template("404.html", member=member), 404

app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run()
