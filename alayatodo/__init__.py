from flask import Flask, g
import sqlite3
import os
import tempfile

# configuration
from flask_bcrypt import Bcrypt

DATABASE = os.path.join(tempfile.gettempdir(), 'alayatodo.db')
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

# For password hashing/salting.
bcrypt = Bcrypt()


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


import alayatodo.views