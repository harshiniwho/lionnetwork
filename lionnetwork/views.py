from flask import (Blueprint, render_template, redirect, url_for, session)

views = Blueprint('views', __name__)

@views.route('/')
def index():
    if "columbia_uni" in session:
        return redirect(url_for('user.home'))
    else:
        return render_template("index.html")

@views.route('/payment')
def payment():
    return render_template("payment.html")

@views.route('/forum')
def forum():
    return render_template('forums/index.html')
