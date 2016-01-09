from pornote import db

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
    class_nb = db.Column(db.Integer)

    homework = db.relationship("Homework", backref="author")

class Homework(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    member_id = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)

    subject = db.Column(db.String(128))
    description = db.Column(db.String(256))
    class_nb = db.Column(db.Integer)
    end_date = db.Column(db.DateTime)
