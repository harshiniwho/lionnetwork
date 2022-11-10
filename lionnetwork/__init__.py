import os
from flask import Flask, g
from . import auth, db, forums
from .views import views
from .auth import auth

# init application
def start_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    # not sure what this is for?
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    return app


"""
@app.route('/test')
def test():
    connection = db.get_db_connection()
    cursor = g.conn.execute("SELECT * FROM PAYMENTS")
    for row in cursor:
        print(row)
    return "test"
"""
