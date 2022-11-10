from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template("index.html")

# for testing purpose
@views.route('/forum')
def forum():
    return render_template("forums/index.html")



