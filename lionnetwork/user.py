from flask import (Blueprint, render_template, redirect, request, session, url_for, flash, g)

user = Blueprint('user', __name__)

@user.route('/home',  methods=('GET', 'POST'))
def home():
    if request.method == "POST":
        jobList = []
        return render_template('user/home.html', jobList = jobList)

    elif request.method == "GET":
        if "columbia_uni" in session and session['listing_access']:
            jobList = g.conn.execute('SELECT * FROM job_listings').fetchall()
            return render_template('user/home.html', jobList = jobList)
        else:
            return render_template('user/home.html')

@user.route('/settings')
def settings():
    return render_template('user/settings.html')
