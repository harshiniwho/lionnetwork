import os

from flask import current_app, g
from sqlalchemy import *
from sqlalchemy.pool import NullPool

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

DB_SERVER = os.environ["DB_SERVER"]

DATABASEURI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/proj1part2"

engine = create_engine(DATABASEURI)

def before_request():
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None


def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass


def init_app(app):
    app.before_request(before_request)
    app.teardown_request(teardown_request)
