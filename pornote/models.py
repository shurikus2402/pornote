from pornote import db
from werkzeug import generate_password_hash, check_password_hash

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    class_nb = db.Column(db.Integer)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(64))

    homework = db.relationship("Homework", backref="author")

    def __init__(self, first_name, last_name, email, password, class_nb):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.class_nb = class_nb
        self.email = email.lower()
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    member_id = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)

    subject = db.Column(db.String(128))
    description = db.Column(db.String(256))
    end_date = db.Column(db.Date)
    filename = db.Column(db.String(128))
    class_nb = db.Column(db.Integer)
