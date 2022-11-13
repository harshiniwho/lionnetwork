import os
from flask import Flask, g
from . import auth, db, forums
from .views import views
from .auth import auth
from .user import user
from .forums import forums
from .posts import posts

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
    app.register_blueprint(user, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')

    app.register_blueprint(forums)
    app.register_blueprint(posts)
    return app
