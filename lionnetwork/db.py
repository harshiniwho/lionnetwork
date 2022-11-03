import os

from flask import current_app, g
from sqlalchemy import *
from sqlalchemy.pool import NullPool

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

DB_SERVER = os.environ["DB_SERVER"]

DATABASEURI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/proj1part2"

def get_db_connection():
    if 'db' not in g:
        engine = create_engine(DATABASEURI)
        g.db = engine

    return g.db


def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.dispose()


def init_app(app):
    pass
    # app.teardown_appcontext(close_db)
