# This file is the default configuration file for pornote, don't forget to
# change the secret_key to an actual key !
# (see http://flask.pocoo.org/docs/0.10/quickstart/#sessions)

import os

DEBUG=True
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URI = "sqlite:///" + BASE_DIR + "/app.db"

# Change the secret key !
SECRET_KEY = "change_me"
