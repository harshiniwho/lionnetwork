from flask import (Blueprint, render_template, redirect, request, session, url_for, flash, g, make_response)
from sqlalchemy.sql import text
import uuid
from .utils import processQuery
from lionnetwork.auth import login_required

user = Blueprint('user', __name__)

@user.route('/admin', methods = ["GET", "POST"])
@login_required
def adminSettings():
    print("Called")
    if request.method == "POST" and g.user.is_admin:
        params = {}
        params['uni'] = request.form['uni']
        params['new_ind'] = request.form['ind']

        if len(params['uni']) > 0:
            params['admin'] = True
            sql = 'update users set is_admin = :admin where columbia_uni = :uni'
            flash(f"Successfully upgraded {params['uni']} to admin.", category = "success") if processQuery(sql, params) else flash(f"Could not upgrade {params['uni']} to admin...", category = "error")

        elif len(params['new_ind']) > 0:
            params['uni'] = session['columbia_uni']
            params['new_id'] = int(str(uuid.uuid4().int)[:5])

            sql = 'insert into industries (industry_id, industry_name, columbia_uni) values (:new_id, :new_ind, :uni)'
            flash(f"Successfully added {params['new_ind']}.", category = "success") if processQuery(sql, params) else flash(f"Could not add {params['new_ind']}...", category = "error")

        return redirect(request.url)
    else:
        return render_template('user/settings.html')

@user.route('/modifyJob', methods = ["GET", "POST"])
def modifyJob():
    if request.method == "POST" and g.user.is_admin:
        params = {}
        if request.form.get('hide') is not None:
            params['listing_id'] = int(request.form.get('hide'))
            params['val'] = False
            sql = 'update job_listings set show_listing = :val where listing_id = :listing_id'
        elif request.form.get('delete') is not None:
            params['listing_id'] = int(request.form.get('delete'))
            sql = 'delete from job_listings where listing_id = :listing_id'
        elif request.form.get('show') is not None:
            params['listing_id'] = int(request.form.get('show'))
            params['val'] = True
            sql = 'update job_listings set show_listing = :val where listing_id = :listing_id'

        flash("Query Success!", category = "success") if processQuery(sql, params) else flash("Query Failure!", category = "error")
        return redirect(url_for('user.jobPosting'))

    elif not g.user.is_admin:
        flash("Invalid Access", category = "error")
        return redirect(url_for('user.jobPosting'))

    else:
        return redirect(url_for('user.jobPosting'))

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
        params['ind'] = int(request.form['industry'])
        
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

    elif request.method == "POST" and g.user:
        params = {}
        params['uni'] = g.user.columbia_uni
        params['delete'] = True if "delete" in request.form.keys() else False
        params['deactivate'] = True if "deactivate" in request.form.keys() else False
        params['reactivate'] = True if "reactivate" in request.form.keys() else False
        params['newName'] = request.form['name'] if "name" in request.form.keys() else None
        params['newMajor'] = request.form['major'] if "major" in request.form.keys() else None

        if params['delete']:
            sqlRemove = 'delete from users where columbia_uni = :uni'
            try:
                g.conn.execute(text(sqlRemove), params)
                flash("Successfully deleted your account.", category = "success")
                return redirect(url_for('auth.logout'))
            except Exception as e:
                print(e)
                flash("Could not remove your account...", category = "error")

        elif params['deactivate']:
            sqlDeactivate = 'update users set is_deactivated = :deactivate where columbia_uni = :uni'
            try:
                g.conn.execute(text(sqlDeactivate), params)
                flash("Successfully deactivated your account.", category = "success")
                return redirect(url_for('auth.logout'))
            except Exception as e:
                print(e)
                flash("Could not remove your account...", category = "error")

        elif params['reactivate']:
            print(params['deactivate'])
            sqlReactivate = 'update users set is_deactivated = :deactivate where columbia_uni = :uni'
            try:
                g.conn.execute(text(sqlReactivate), params)
                flash("Successfully reactivated your account.", category = "success")
                return redirect(url_for('user.jobPosting'))
            except Exception as e:
                print(e)
                flash("Could not reactivated your account...", category = "error")

        elif len(params['newName']) > 0:
            sqlName = 'update users set name = :newName where columbia_uni = :uni'
            try:
                g.conn.execute(text(sqlName), params)
                flash(f"Your name has been updated to {params['newName']}", category = "sucess")
            except Exception as e:
                print(e)
                flash("Could not update your name...", category = "error")

        elif len(params['newMajor']) > 0:
            sqlMajor = 'update users set major = :newMajor where columbia_uni = :uni'
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





