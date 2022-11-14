from flask import (Blueprint, render_template, redirect, request, session, url_for, flash, g, make_response)
from sqlalchemy.sql import text
import uuid
from lionnetwork.auth import login_required

user = Blueprint('user', __name__)

@user.route('/admin', methods = ["GET", "POST"])
@login_required
def adminSettings():
    if request.method == "POST":
        params['uni'] = request.form['uni']
        params['admin'] = True
        sqlUpgrade = 'update users set is_admin = :admin where columbia_uni = :uni'
        try:
            g.conn.execute(text(sqlUpgrade), params)
            flash(f"Successfully upgraded {params['uni']} to admin.", category = "success")
            return redirect(request.url)
        except Exception as e:
            print(e)
            flash(f"Could not upgrade {params['uni']} to admin...", category = "error")
            return redirect(request.url)


def fetch_industries():
    industries = g.conn.execute('SELECT * FROM industries').fetchall()
    return industries

@user.route('/home',  methods=('GET', 'POST'))
@login_required
def jobPosting():
    if request.method == "POST":
        jobList = []; params = {}
        params['int'] = False; params['visa'] = False
        session['int'] = False; session['visa'] = False

        params['ind'] = int(request.form['industry_id'])
        if "internship" in request.form.keys():
            session['int'] = True
            params['int'] = True
        if "visa" in request.form.keys():
            session['visa'] = True
            params['visa'] = True

        sql = 'SELECT * FROM job_listings WHERE industry_id = :ind and is_internship = :int and is_visa_sponsored = :visa'
        sqlGetName = 'SELECT industry_name FROM industries WHERE industry_id=:id_'
        if params['ind'] != -1:
            jobList = g.conn.execute(text(sql), params).fetchall()
            session['ind'] = g.conn.execute(text(sqlGetName), {"id_": params['ind']}).fetchone()[0]

        return render_template('user/home.html', jobList = jobList, industries=fetch_industries())

    elif request.method == "GET":
        if "columbia_uni" in session and session['listing_access']:
            jobList = g.conn.execute('SELECT * FROM job_listings').fetchall()
            session['ind'] = "All industries"
            session['int'] = False
            session['visa'] = False
            return render_template('user/home.html', jobList = jobList, industries=fetch_industries())
        else:
            return render_template('user/home.html', industries=fetch_industries())

@user.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    if request.method == "GET":
        return render_template('user/settings.html')

    elif request.method == "POST":
        params = {}
        params['uni'] = session['columbia_uni']
        if request.form.get('delete') is not None:
            sqlRemove = 'delete from users where columbia_uni = :uni'
            try:
                g.conn.execute(text(sqlRemove), params)
                flash("Successfully deleted your account.", category = "success")
                return redirect(url_for('auth.logout'))
            except Exception as e:
                print(e)
                flash("Could not remove your account...", category = "error")
                return redirect(request.url)

        if request.form.get('deactivate') is not None:
            params['deactivate'] = True
            sqlDeactivate = 'update users set is_deactivated = :deactivate where columbia_uni = :uni'
            try:
                g.conn.execute(text(sqlDeactivate), params)
                flash("Successfully deactivated your account.", category = "success")
                return redirect(url_for('auth.logout'))
            except Exception as e:
                print(e)
                flash("Could not remove your account...", category = "error")
                return redirect(request.url)

        params['newName'] = request.form['name']
        sqlName = 'update users set name = :newName where columbia_uni = :uni'
        if len(params['newName']) > 0:
            try:
                g.conn.execute(text(sqlName), params)
                flash(f"Your name has been updated to {params['newName']}", category = "sucess")
            except Exception as e:
                print(e)
                flash("Could not update your name...", category = "error")

        params['newMajor'] = request.form['major']
        sqlMajor = 'update users set major = :newMajor where columbia_uni = :uni'
        if len(params['newMajor']) > 0:
            try:
                g.conn.execute(text(sqlMajorName), params)
                flash(f"Your majore has been updated to {params['newMajor']}", category = "sucess")
            except Exception as e:
                print(e)
                flash("Could not update your major...", category = "error")

        return redirect(request.url)


@user.route('/addJob', methods=('GET', 'POST'))
@login_required
def addJob():
    if request.method == "GET":
        return render_template('user/newJob.html')
    elif request.method == "POST":
        params = {}

        params['jid'] = int(str(uuid.uuid4().int)[:5])
        params['uni'] = session['columbia_uni']
        params['job_title'] = request.form['jobtitle']
        params['comp_name'] = request.form['company']
        params['app_url'] = request.form['app_url']
        params['int_'] = True if "internship" in request.form.keys() else False
        params['visa'] = True if "visa" in request.form.keys() else False
        params['show'] = True
        params['ind_id'] = int(request.form['industry'])
        params['deadline'] =request.form['deadline']

        sql = "insert into job_listings (listing_id, company_name, position_name, is_visa_sponsored, application_url, is_internship, show_listing, columbia_uni, industry_id, deadline) values (:jid, :comp_name, :job_title, :visa, :app_url, :int_, :show, :uni, :ind_id, :deadline)"
        try:
            g.conn.execute(text(sql), params)
            flash(f"{params['job_title']} added!", category="success")
            return redirect(url_for('user.jobPosting'))
        except Exception as e:
            print(e)
            flash("Could not Add Job... Please try again.", category="error")
            return redirect(request.url)





