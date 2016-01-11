# pornote

This project is a parody of the famous french homework online system [Pronote](https://fr.wikipedia.org/wiki/Pronote). Pornote enables you to share your homework instead of receiving it, and rewards you with other homeworks from people of your own class !

Pornote was an original idea of [Gnomino](https://github.com/Gnomino), that I found funny and wanted to actually make so I could in the meantime progress in Python, a new language I just started to learn about.

## How does it work ?

Each person of a class creates an account, and everyone can upload homeworks to the server (but not everyone can access your homework, only those who worked for !). When you upload it, you gain a point, if you make it visible to everyone you gain two points. These points are needed to access other people's homework, so that everyone has to work a bit to get rewarded.

## What is pornote using ?

Pornote is using [Flask](http://flask.pocoo.org/), a microframework for [Python](https://www.python.org/), and some other libraries like [flask-sqlalchemy](http://flask-sqlalchemy.pocoo.org/2.1/) (for the database), and [werkzeug](http://werkzeug.pocoo.org/) (to handle password storage).

## Run pornote on your server

First, you must create the database :

```bash
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```

Then, you need to create a `config.py` file, there is a template called `default_config.py` in the `pornote` directory that you can copy. Don't forget to change the secret key in the configuation file before using it ! Also, you should set the location of your `upload` folder, by changing the `UPLOAD_FOLDER` value in the config file. And finally, you might consider changing the `UNALLOWED_EXTENSIONS` value to prevent from XSS problems on your server.
