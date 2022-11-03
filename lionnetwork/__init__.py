import os

from flask import Flask, g

from . import auth, db

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev', #TODO change to something random for deployment
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

# setup db 
db.init_app(app)

# register blueprints
app.register_blueprint(auth.bp)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/test')
def test():
    connection = db.get_db_connection()
    cursor = g.conn.execute("SELECT * FROM PAYMENTS")
    for row in cursor:
        print(row)
    return "test"