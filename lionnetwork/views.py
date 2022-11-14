from flask import (Blueprint, render_template, redirect, request, session, url_for, flash, g, make_response)
from sqlalchemy.sql import text
import uuid

views = Blueprint('views', __name__)

@views.route('/')
def index():
    if "columbia_uni" in session:
        return redirect(url_for('user.jobPosting'))
    else:
        return render_template("index.html")

@views.route('/payment', methods = ["GET", "POST"])
def payment():
    if request.method == "POST":
        params = {}
        params['pid'] = int(str(uuid.uuid4().int)[:5])
        params['amount'] = float(request.form['amount'])
        params['uni'] = session['columbia_uni']
        params['grant'] = True

        sqlPayment = "insert into payments (payment_id, amount, columbia_uni) values (:pid, :amount, :uni)"

        sqlGrant = 'update users set has_job_listings_access = :grant where columbia_uni = :uni'
        try:
            g.conn.execute(text(sqlPayment), params)
            g.conn.execute(text(sqlGrant), params)
            flash(f"${params['amount']} Donnation Processed!", category="success")
            session['listing_access'] = True
            return redirect(url_for('user.jobPosting'))
        except Exception as e:
            print(e)
            flash("Could Not Process Payment...", category="error")
            return redirect(request.url)

    elif request.method == "GET":
        return render_template("payment.html")


