from flask import (Blueprint, render_template, redirect, request, session, url_for, flash, g, make_response)
from sqlalchemy.sql import text
import uuid
from .utils import processQuery
from lionnetwork.auth import login_required

user = Blueprint('user', __name__)


def fetch_non_admins():
    users = g.conn.execute('SELECT * from users where is_admin = False')
    return users


def fetch_payments():
    payments = g.conn.execute("SELECT payment_id, amount, columbia_uni, to_char(payment_timestamp, 'Day DD Mon YYYY HH:MM:ss') as payment_timestamp  from payments")
    return payments


@user.route('/admin', methods = ["GET", "POST"])
@login_required
def adminSettings():
    if request.method == "POST" and g.user.is_admin:
        params = {}
        params['uni'] = request.form['uni']
        params['new_ind'] = request.form['ind']

        if len(params['new_ind']) > 0:
            params['uni'] = session['columbia_uni']
            params['new_id'] = int(str(uuid.uuid4().int)[:5])

            sql = 'insert into industries (industry_id, industry_name, columbia_uni) values (:new_id, :new_ind, :uni)'
            flash(f"Successfully added {params['new_ind']}.", category = "success") if processQuery(sql, params) else flash(f"Could not add {params['new_ind']}...", category = "error")
    
        elif len(params['uni']) > 0:
            params['admin'] = True
            sql = 'update users set is_admin = :admin where columbia_uni = :uni'
            flash(f"Successfully upgraded {params['uni']} to admin.", category = "success") if processQuery(sql, params) else flash(f"Could not upgrade {params['uni']} to admin...", category = "error")

        return redirect(request.url)
    else:
        return render_template('user/settings.html', users=fetch_non_admins(), payments=fetch_payments())


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


def fetch_industry_name(industry_id):
    industry_name = g.conn.execute('SELECT industry_name from industries WHERE industry_id = %s', [industry_id]).fetchone()
    return industry_name


@user.route('/home',  methods=('GET', 'POST'))
@login_required
def jobPosting():
    if request.method == "POST":
        jobList = []; params = {}
        params['int'] = False; params['visa'] = False
        session['int'] = False; session['visa'] = False
        industry_id = 1
        params['ind'] = int(request.form['industry_id'])
        if "internship" in request.form.keys():
            session['int'] = True
            params['int'] = True
        if "visa" in request.form.keys():
            session['visa'] = True
            params['visa'] = True
        if "industry_id" in request.form.keys():
            industry_id = int(request.form['industry_id'])

        sql = 'SELECT * FROM job_listings WHERE industry_id = :ind and is_internship = :int and is_visa_sponsored = :visa'
        sqlGetName = 'SELECT industry_name FROM industries WHERE industry_id=:id_'
        if params['ind'] != -1:
            jobList = g.conn.execute(text(sql), params).fetchall()
            session['ind'] = g.conn.execute(text(sqlGetName), {"id_": params['ind']}).fetchone()[0]


        return render_template('user/home.html', jobList = jobList, industries=fetch_industries(), industry_id=industry_id, industry_name=fetch_industry_name(industry_id)[0])

    elif request.method == "GET":
        if "columbia_uni" in session and session['listing_access']:
            jobList = g.conn.execute('SELECT * FROM job_listings').fetchall()
            session['ind'] = "All industries"
            session['int'] = False
            session['visa'] = False
            return render_template('user/home.html', jobList = jobList, industries=fetch_industries(), industry_id=-1, industry_name='')
        else:
            return render_template('user/home.html', industries=fetch_industries(), industry_id=-1, industry_name='')


@user.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    session['order_by'] = False
    if request.method == "GET":
        return render_template('user/settings.html', users=fetch_non_admins(), payments=fetch_payments())

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
                g.conn.execute('delete from comments where columbia_uni = %s', (g.user.columbia_uni,))
                g.conn.execute('delete from posts where columbia_uni = %s', (g.user.columbia_uni,))
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


@user.route('/update', methods=('POST',))
@login_required
def update():
    new_name = request.form['name']
    new_major = request.form['major']

    if new_name != None and new_name != '':
        g.conn.execute('UPDATE users SET name = %s WHERE columbia_uni = %s', (new_name, g.user["columbia_uni"]))

    if new_major != None and new_major != '':
        g.conn.execute('UPDATE users SET major = %s WHERE columbia_uni = %s', (new_major, g.user["columbia_uni"]))
    
    return redirect(url_for('user.settings'))


@user.route('/addJob', methods=('GET', 'POST'))
@login_required
def addJob():
    if request.method == "GET":
        return render_template('user/newJob.html', industries=fetch_industries())
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
        params['deadline'] = request.form['deadline']

        if params['deadline'] != None and params['deadline'] != '':
            sql = "insert into job_listings (listing_id, company_name, position_name, is_visa_sponsored, application_url, is_internship, show_listing, columbia_uni, industry_id, deadline) values (:jid, :comp_name, :job_title, :visa, :app_url, :int_, :show, :uni, :ind_id, :deadline)"
        else:
            sql = "insert into job_listings (listing_id, company_name, position_name, is_visa_sponsored, application_url, is_internship, show_listing, columbia_uni, industry_id) values (:jid, :comp_name, :job_title, :visa, :app_url, :int_, :show, :uni, :ind_id)"
        try:
            g.conn.execute(text(sql), params)
            flash(f"{params['job_title']} added!", category="success")
            return redirect(url_for('user.jobPosting'))
        except Exception as e:
            print(e)
            flash("Could not Add Job... Please try again.", category="error")
            return redirect(request.url)
